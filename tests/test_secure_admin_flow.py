import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.security import get_password_hash
from app.models.user import User
from app.models.organization import Organization, OrganizationStatus, OrgMember, OrgMemberRole, MemberStatus
from app.models.rbac import Role, UserRoleScope
from app.main import app
from app.core.database import get_db
from typing import Generator, AsyncGenerator
import os

# Test Data
SUPER_ADMIN_EMAIL = "superadmin@example.com"
FARMER_EMAIL = "farmer@example.com"
PASSWORD = "password123"
# DB URL (Env-aware)
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/farm_db")

# Engine & Session
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest_asyncio.fixture(scope="function")
async def async_client(test_db: Session) -> AsyncGenerator[AsyncClient, None]:
    # Override dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def setup_data(test_db: Session):
    # Ensure test data exists
    # 1. Create Roles if not exist
    sa_role = test_db.query(Role).filter(Role.code == "SUPER_ADMIN").first()
    if not sa_role:
        sa_role = Role(
            code="SUPER_ADMIN", 
            name="Super Admin", 
            display_name="Super Administrator",
            scope=UserRoleScope.SYSTEM,
            description="System Super Admin"
        )
        test_db.add(sa_role)
    
    farmer_role = test_db.query(Role).filter(Role.code == "FARMER").first()
    if not farmer_role:
        farmer_role = Role(
            code="FARMER", 
            name="Farmer", 
            display_name="Farmer",
            scope=UserRoleScope.ORGANIZATION,
            description="Farmer Role"
        )
        test_db.add(farmer_role)
    
    test_db.commit()

    # 2. Create Users
    sa_user = test_db.query(User).filter(User.email == SUPER_ADMIN_EMAIL).first()
    if not sa_user:
        sa_user = User(
            email=SUPER_ADMIN_EMAIL,
            password_hash=get_password_hash(PASSWORD),
            first_name="Super",
            last_name="Admin",
            is_active=True
        )
        test_db.add(sa_user)
    
    farmer_user = test_db.query(User).filter(User.email == FARMER_EMAIL).first()
    if not farmer_user:
        farmer_user = User(
            email=FARMER_EMAIL,
            password_hash=get_password_hash(PASSWORD),
            first_name="Farmer",
            last_name="Joe",
            is_active=True
        )
        test_db.add(farmer_user)
    
    test_db.commit()
    
    # 3. Create Organization (Pending Approval)
    test_org = test_db.query(Organization).filter(Organization.name == "Test Farm Org").first()
    if not test_org:
        test_org = Organization(
            name="Test Farm Org",
            organization_type="FARMING", 
            status=OrganizationStatus.NOT_STARTED,
            is_approved=False
        )
        test_db.add(test_org)
        test_db.commit()
    else:
        # Reset approval status
        test_org.is_approved = False
        test_db.commit()

    # 4. Assign Roles
    # Super Admin Role
    sa_member = test_db.query(OrgMember).filter(OrgMember.user_id == sa_user.id, OrgMember.organization_id == test_org.id).first()
    if not sa_member:
        sa_member = OrgMember(user_id=sa_user.id, organization_id=test_org.id, status=MemberStatus.ACTIVE)
        test_db.add(sa_member)
        test_db.commit() 
        
        sa_member_role = OrgMemberRole(user_id=sa_user.id, organization_id=test_org.id, role_id=sa_role.id, is_primary=True)
        test_db.add(sa_member_role)
    
    # Farmer Role
    farmer_member = test_db.query(OrgMember).filter(OrgMember.user_id == farmer_user.id, OrgMember.organization_id == test_org.id).first()
    if not farmer_member:
        farmer_member = OrgMember(user_id=farmer_user.id, organization_id=test_org.id, status=MemberStatus.ACTIVE)
        test_db.add(farmer_member)
        test_db.commit()

        f_role = test_db.query(Role).filter(Role.code == "FARMER").first()
        farmer_member_role = OrgMemberRole(user_id=farmer_user.id, organization_id=test_org.id, role_id=f_role.id, is_primary=True)
        test_db.add(farmer_member_role)
    
    test_db.commit()
    return test_org

@pytest.mark.asyncio
async def test_super_admin_flow(async_client: AsyncClient, test_db, setup_data):
    org_id = str(setup_data.id)
    
    # 1. Login Super Admin
    resp = await async_client.post("/api/v1/auth/login", json={
        "email": SUPER_ADMIN_EMAIL,
        "password": PASSWORD
    })
    
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    sa_token = data["data"]["tokens"]["access_token"]
    sa_refresh = data["data"]["tokens"]["refresh_token"]
    assert sa_token is not None
    assert sa_refresh is not None

    # 2. Test Refresh Token
    resp_refresh = await async_client.post("/api/v1/auth/refresh", json={
        "refresh_token": sa_refresh
    })
    assert resp_refresh.status_code == 200, f"Refresh failed: {resp_refresh.text}"
    new_access_token = resp_refresh.json()["data"]["access_token"]
    assert new_access_token is not None

    # 3. Login Farmer (Standard User)
    resp_f = await async_client.post("/api/v1/auth/login", json={
        "email": FARMER_EMAIL,
        "password": PASSWORD
    })
    assert resp_f.status_code == 200
    farmer_token = resp_f.json()["data"]["tokens"]["access_token"]

    # 4. Negative Test: Farmer tries to approve Org
    resp_fail = await async_client.post(
        f"/api/v1/admin/organizations/{org_id}/approve",
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert resp_fail.status_code == 403
    assert resp_fail.json()["error_code"] == "SUPER_ADMIN_REQUIRED"

    # 5. Positive Test: Super Admin approves Org
    resp_approve = await async_client.post(
        f"/api/v1/admin/organizations/{org_id}/approve",
        headers={"Authorization": f"Bearer {sa_token}"}
    )
    assert resp_approve.status_code == 200
    assert resp_approve.json()["success"] == True
    assert resp_approve.json()["data"]["is_approved"] == True

    # 6. Verify Farmer Access
    # If using get_current_active_user restriction logic:
    resp_me = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {farmer_token}"}
    )
    assert resp_me.status_code == 200
    assert resp_me.json()["success"] == True
