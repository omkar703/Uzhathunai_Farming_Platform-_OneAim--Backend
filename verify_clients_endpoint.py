
import asyncio
import os
import sys
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.work_order import WorkOrder
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus, WorkOrderStatus
from app.core.security import get_password_hash
from app.main import app
from httpx import AsyncClient, ASGITransport

async def main():
    db = SessionLocal()
    try:
        print("Setting up test data...")
        
        # 1. Create Test User (FSP Owner)
        email = f"fsp_owner_{uuid4().hex[:8]}@example.com"
        password = "password123"
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            first_name="FSP",
            last_name="Owner",
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # 2. Create FSP Organization
        fsp_org = Organization(
            name=f"Test FSP {uuid4().hex[:8]}",
            organization_type=OrganizationType.FSP,
            status=OrganizationStatus.ACTIVE,
            contact_email="fsp@example.com"
        )
        db.add(fsp_org)
        db.flush()
        
        # Add user to FSP Org
        fsp_member = OrgMember(user_id=user.id, organization_id=fsp_org.id, status=MemberStatus.ACTIVE)
        db.add(fsp_member)
        db.flush()
        
        # Assign FSP_OWNER role (assuming role exists, otherwise skipping permission check might fail depending on implementation)
        # For simplicity, we'll assume usage of OrganizationService._check_admin_permission logic
        # which checks for 'FSP_OWNER' or 'FSP_ADMIN' code in roles.
        # We need to ensure these roles exist or Mock them. 
        # Let's just manually insert a role if needed or rely on existing seed data.
        from app.models.rbac import Role
        fsp_role = db.query(Role).filter(Role.code == "FSP_OWNER").first()
        if not fsp_role:
            fsp_role = Role(code="FSP_OWNER", name="FSP Owner", scope="ORGANIZATION")
            db.add(fsp_role)
            db.flush()
            
        fsp_member_role = OrgMemberRole(
            user_id=user.id, 
            organization_id=fsp_org.id, 
            role_id=fsp_role.id,
            is_primary=True
        )
        db.add(fsp_member_role)
        
        # 3. Create Farming Organization (The Client)
        farming_org = Organization(
            name=f"Client Farm {uuid4().hex[:8]}",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            contact_email="client@example.com",
            contact_phone="1234567890"
        )
        db.add(farming_org)
        db.flush()
        
        # 4. Create Work Order
        wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Advisory Services",
            status=WorkOrderStatus.ACTIVE,
            work_order_number=f"WO-{uuid4().hex[:8]}",
            created_by=user.id
        )
        db.add(wo)
        db.commit()
        
        print(f"Test data created. User: {email}, FSP Org: {fsp_org.id}, Client Org: {farming_org.id}")
        
        # 5. Login to get token
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            login_response = await ac.post("/api/v1/auth/login", json={
                "email": email,
                "password": password
            })
            if login_response.status_code != 200:
                print(f"Login failed: {login_response.text}")
                return
                
            token = login_response.json()["data"]["tokens"]["access_token"]
            
            # 6. Call Clients Endpoint
            print("Calling GET /api/v1/fsp-services/clients...")
            response = await ac.get(
                "/api/v1/fsp-services/clients",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json().get("data", [])
                if len(data) == 1 and data[0]["id"] == str(farming_org.id):
                    print("SUCCESS: Retrieved expected client.")
                else:
                    print("FAILURE: Unexpected data returned.")
            else:
                print("FAILURE: Endpoint returned error.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
