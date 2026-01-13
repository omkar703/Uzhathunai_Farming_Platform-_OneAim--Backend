"""
Integration tests for Organization API endpoints.

Tests cover:
- POST /api/v1/organizations (FARMING)
- POST /api/v1/organizations (FSP)
- GET /api/v1/organizations
- PUT /api/v1/organizations/{id}
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.subscription import SubscriptionPlan
from app.models.fsp_service import MasterService, FSPServiceListing
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope,
    ServiceStatus
)


@pytest.fixture
def owner_role(db: Session) -> Role:
    """Get or create OWNER role for FARMING organizations."""
    role = db.query(Role).filter(Role.code == 'OWNER').first()
    if not role:
        role = Role(
            code='OWNER',
            name='Owner',
            display_name='Organization Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of farming organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def fsp_owner_role(db: Session) -> Role:
    """Get or create FSP_OWNER role for FSP organizations."""
    role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
    if not role:
        role = Role(
            code='FSP_OWNER',
            name='FSP Owner',
            display_name='FSP Organization Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of FSP organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def master_service(db: Session) -> MasterService:
    """Get or create a master service for FSP testing."""
    service = db.query(MasterService).filter(MasterService.code == 'SOIL_TESTING').first()
    if not service:
        service = MasterService(
            code='SOIL_TESTING',
            name='Soil Testing',
            description='Professional soil testing and analysis',
            status=ServiceStatus.ACTIVE,
            sort_order=1
        )
        db.add(service)
        db.commit()
        db.refresh(service)
    return service


class TestCreateOrganizationFarming:
    """Tests for POST /api/v1/organizations (FARMING type)."""
    
    def test_create_farming_organization_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role
    ):
        """Test successful FARMING organization creation via API."""
        payload = {
            "name": "Green Valley Farm",
            "organization_type": "FARMING",
            "description": "A sustainable farming organization",
            "district": "Coimbatore",
            "pincode": "641001",
            "contact_email": "contact@greenvalley.com",
            "contact_phone": "+919876543210"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Green Valley Farm"
        assert data["organization_type"] == "FARMING"
        assert data["status"] == "ACTIVE"
        assert data["description"] == "A sustainable farming organization"
        assert data["district"] == "Coimbatore"
        assert data["pincode"] == "641001"
        assert data["contact_email"] == "contact@greenvalley.com"
        assert data["contact_phone"] == "+919876543210"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_farming_organization_minimal_data(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role
    ):
        """Test FARMING organization creation with minimal required data."""
        payload = {
            "name": "Simple Farm",
            "organization_type": "FARMING"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Simple Farm"
        assert data["organization_type"] == "FARMING"
        assert data["status"] == "ACTIVE"
        assert data["description"] is None
        assert data["district"] is None
    
    def test_create_farming_organization_duplicate_name(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role
    ):
        """Test that duplicate organization names are rejected."""
        payload = {
            "name": "Duplicate Farm",
            "organization_type": "FARMING"
        }
        
        # Create first organization
        response1 = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        assert response1.status_code == 201
        
        # Try to create second organization with same name
        response2 = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with conflict error
        assert response2.status_code == 409
        data = response2.json()
        assert "detail" in data or "message" in data
    
    def test_create_farming_organization_validation_error(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test validation error for invalid data."""
        payload = {
            "name": "",  # Empty name
            "organization_type": "FARMING"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
    
    def test_create_farming_organization_unauthorized(
        self,
        client: TestClient
    ):
        """Test that unauthorized requests are rejected."""
        payload = {
            "name": "Unauthorized Farm",
            "organization_type": "FARMING"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload
        )
        
        # Should fail with unauthorized or forbidden error
        assert response.status_code in [401, 403]


class TestCreateOrganizationFSP:
    """Tests for POST /api/v1/organizations (FSP type)."""
    
    def test_create_fsp_organization_with_services(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        fsp_owner_role: Role,
        master_service: MasterService
    ):
        """Test successful FSP organization creation with services."""
        payload = {
            "name": "AgriConsult Services",
            "organization_type": "FSP",
            "description": "Professional agricultural consulting",
            "district": "Chennai",
            "pincode": "600001",
            "contact_email": "info@agriconsult.com",
            "contact_phone": "+919123456789",
            "services": [
                {
                    "service_id": str(master_service.id),
                    "title": "Expert Soil Testing",
                    "description": "Comprehensive soil analysis with recommendations",
                    "service_area_districts": ["Chennai", "Kanchipuram", "Tiruvallur"],
                    "pricing_model": "PER_ACRE",
                    "base_price": 500.00
                }
            ]
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "AgriConsult Services"
        assert data["organization_type"] == "FSP"
        assert data["status"] == "NOT_STARTED"  # FSP with services starts NOT_STARTED
        assert data["description"] == "Professional agricultural consulting"
        assert data["district"] == "Chennai"
        assert data["pincode"] == "600001"
        assert data["contact_email"] == "info@agriconsult.com"
        assert data["contact_phone"] == "+919123456789"
        assert "id" in data
    
    def test_create_fsp_organization_without_services_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        fsp_owner_role: Role
    ):
        """Test that FSP organization without services is rejected."""
        payload = {
            "name": "FSP Without Services",
            "organization_type": "FSP",
            "services": []  # Empty services
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
        data = response.json()
        assert "service" in str(data).lower()
    
    def test_create_fsp_organization_multiple_services(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        fsp_owner_role: Role,
        master_service: MasterService,
        db: Session
    ):
        """Test FSP organization creation with multiple services."""
        # Create another master service
        service2 = MasterService(
            code='CROP_ADVISORY',
            name='Crop Advisory',
            description='Expert crop management advice',
            status=ServiceStatus.ACTIVE,
            sort_order=2
        )
        db.add(service2)
        db.commit()
        db.refresh(service2)
        
        payload = {
            "name": "Multi-Service FSP",
            "organization_type": "FSP",
            "services": [
                {
                    "service_id": str(master_service.id),
                    "title": "Soil Testing Service",
                    "description": "Professional soil testing",
                    "service_area_districts": ["Chennai"],
                    "pricing_model": "PER_ACRE",
                    "base_price": 500.00
                },
                {
                    "service_id": str(service2.id),
                    "title": "Crop Advisory Service",
                    "description": "Expert crop management",
                    "service_area_districts": ["Chennai", "Vellore"],
                    "pricing_model": "PER_HOUR",
                    "base_price": 200.00
                }
            ]
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        assert data["name"] == "Multi-Service FSP"
        assert data["organization_type"] == "FSP"
        assert data["status"] == "NOT_STARTED"


class TestGetUserOrganizations:
    """Tests for GET /api/v1/organizations."""
    
    def test_get_user_organizations_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """Test getting user's organizations."""
        # Create test organizations
        org1 = Organization(
            name="Farm 1",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(org1)
        db.commit()
        db.refresh(org1)
        
        # Create membership
        member1 = OrgMember(
            user_id=test_user.id,
            organization_id=org1.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member1)
        db.commit()
        
        org2 = Organization(
            name="Farm 2",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(org2)
        db.commit()
        db.refresh(org2)
        
        # Create membership
        member2 = OrgMember(
            user_id=test_user.id,
            organization_id=org2.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member2)
        db.commit()
        
        response = client.get(
            "/api/v1/organizations",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data
        
        # Verify items
        items = data["items"]
        assert isinstance(items, list)
        assert len(items) >= 2
        
        # Verify organization structure
        org_names = [org["name"] for org in items]
        assert "Farm 1" in org_names
        assert "Farm 2" in org_names
        
        # Verify response structure
        for org in items:
            assert "id" in org
            assert "name" in org
            assert "organization_type" in org
            assert "status" in org
            assert "created_at" in org
            assert "updated_at" in org
    
    def test_get_user_organizations_filter_by_type(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        fsp_owner_role: Role,
        db: Session
    ):
        """Test filtering organizations by type."""
        # Create FARMING organization
        org_farming = Organization(
            name="Farming Org",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(org_farming)
        db.commit()
        db.refresh(org_farming)
        
        member_farming = OrgMember(
            user_id=test_user.id,
            organization_id=org_farming.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member_farming)
        db.commit()
        
        # Create FSP organization
        org_fsp = Organization(
            name="FSP Org",
            organization_type=OrganizationType.FSP,
            status=OrganizationStatus.NOT_STARTED,
            created_by=test_user.id
        )
        db.add(org_fsp)
        db.commit()
        db.refresh(org_fsp)
        
        member_fsp = OrgMember(
            user_id=test_user.id,
            organization_id=org_fsp.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member_fsp)
        db.commit()
        
        # Filter by FARMING
        response = client.get(
            "/api/v1/organizations?org_type=FARMING",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        items = data["items"]
        
        # Should only return FARMING organizations
        for org in items:
            assert org["organization_type"] == "FARMING"
    
    def test_get_user_organizations_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """Test pagination of organizations."""
        # Create multiple organizations
        for i in range(5):
            org = Organization(
                name=f"Farm {i}",
                organization_type=OrganizationType.FARMING,
                status=OrganizationStatus.ACTIVE,
                created_by=test_user.id
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            
            member = OrgMember(
                user_id=test_user.id,
                organization_id=org.id,
                status=MemberStatus.ACTIVE
            )
            db.add(member)
        db.commit()
        
        # Get first page with limit 2
        response = client.get(
            "/api/v1/organizations?page=1&limit=2",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data
        
        # Verify pagination values
        assert data["page"] == 1
        assert data["limit"] == 2
        
        # Should return at most 2 organizations
        assert len(data["items"]) <= 2
    
    def test_get_user_organizations_empty(
        self,
        client: TestClient,
        db: Session
    ):
        """Test getting organizations for user with no organizations."""
        # Create new user with no organizations
        from app.core.security import get_password_hash
        new_user = User(
            email="noorg@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="No",
            last_name="Org",
            phone="+919999999999",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Login as new user
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "noorg@example.com",
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/v1/organizations",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        
        # Verify empty list
        assert isinstance(data["items"], list)
        assert len(data["items"]) == 0
        assert data["total"] == 0
    
    def test_get_user_organizations_unauthorized(
        self,
        client: TestClient
    ):
        """Test that unauthorized requests are rejected."""
        response = client.get("/api/v1/organizations")
        
        # Should fail with unauthorized or forbidden error
        assert response.status_code in [401, 403]


class TestUpdateOrganization:
    """Tests for PUT /api/v1/organizations/{id}."""
    
    def test_update_organization_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """Test successful organization update."""
        # Create organization
        org = Organization(
            name="Original Name",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            description="Original description",
            district="Original District",
            created_by=test_user.id
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create membership with OWNER role
        member = OrgMember(
            user_id=test_user.id,
            organization_id=org.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        member_role = OrgMemberRole(
            user_id=test_user.id,
            organization_id=org.id,
            role_id=owner_role.id,
            is_primary=True
        )
        db.add(member_role)
        db.commit()
        
        # Update organization
        payload = {
            "name": "Updated Name",
            "description": "Updated description",
            "district": "Updated District",
            "pincode": "123456",
            "contact_email": "updated@example.com",
            "contact_phone": "+919999999999"
        }
        
        response = client.put(
            f"/api/v1/organizations/{org.id}",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Name"
        assert data["description"] == "Updated description"
        assert data["district"] == "Updated District"
        assert data["pincode"] == "123456"
        assert data["contact_email"] == "updated@example.com"
        assert data["contact_phone"] == "+919999999999"
        assert data["organization_type"] == "FARMING"  # Should not change
        assert data["status"] == "ACTIVE"  # Should not change
    
    def test_update_organization_partial_update(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """Test partial organization update."""
        # Create organization
        org = Organization(
            name="Original Name",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            description="Original description",
            district="Original District",
            created_by=test_user.id
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        # Create membership with OWNER role
        member = OrgMember(
            user_id=test_user.id,
            organization_id=org.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        member_role = OrgMemberRole(
            user_id=test_user.id,
            organization_id=org.id,
            role_id=owner_role.id,
            is_primary=True
        )
        db.add(member_role)
        db.commit()
        
        # Update only name
        payload = {
            "name": "New Name Only"
        }
        
        response = client.put(
            f"/api/v1/organizations/{org.id}",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "New Name Only"
        assert data["description"] == "Original description"  # Should not change
        assert data["district"] == "Original District"  # Should not change
    
    def test_update_organization_not_found(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test updating non-existent organization."""
        fake_id = uuid4()
        payload = {
            "name": "Updated Name"
        }
        
        response = client.put(
            f"/api/v1/organizations/{fake_id}",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with not found error (404) or forbidden (403) if permission check happens first
        assert response.status_code in [403, 404]
    
    def test_update_organization_unauthorized(
        self,
        client: TestClient,
        db: Session
    ):
        """Test that unauthorized requests are rejected."""
        # Create organization
        from app.core.security import get_password_hash
        user = User(
            email="owner@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Owner",
            last_name="User",
            phone="+919888888888",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        org = Organization(
            name="Test Org",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=user.id
        )
        db.add(org)
        db.commit()
        db.refresh(org)
        
        payload = {
            "name": "Updated Name"
        }
        
        response = client.put(
            f"/api/v1/organizations/{org.id}",
            json=payload
        )
        
        # Should fail with unauthorized or forbidden error
        assert response.status_code in [401, 403]
