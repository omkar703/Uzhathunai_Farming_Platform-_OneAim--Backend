
import asyncio
import os
import sys
from uuid import uuid4
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.work_order import WorkOrder
from app.models.rbac import Role
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus, WorkOrderStatus
from app.core.security import get_password_hash
from app.main import app
from httpx import AsyncClient, ASGITransport

async def main():
    db = SessionLocal()
    try:
        print("Setting up test data for Work Order Assignment...")
        
        # 0. Get Roles
        farming_owner_role = db.query(Role).filter(Role.code == 'OWNER').first()
        fsp_owner_role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
        
        # 1. Create FSP User (Admin) & Org
        fsp_admin_email = f"fsp_admin_{uuid4().hex[:8]}@example.com"
        password = "password123"
        fsp_admin = User(email=fsp_admin_email, password_hash=get_password_hash(password), first_name="FSP", last_name="Admin", is_active=True)
        db.add(fsp_admin)
        db.flush()  # Iterate to generate ID
        
        fsp_org = Organization(name=f"FSP Assign Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="fsp@test.com")
        db.add(fsp_org)
        db.flush()
        
        db.add(OrgMember(user_id=fsp_admin.id, organization_id=fsp_org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=fsp_admin.id, organization_id=fsp_org.id, role_id=fsp_owner_role.id))
        db.flush()
        
        # 2. Create FSP Member (Field Officer)
        fsp_member_email = f"fsp_field_{uuid4().hex[:8]}@example.com"
        fsp_member = User(email=fsp_member_email, password_hash=get_password_hash(password), first_name="Field", last_name="Officer", is_active=True)
        db.add(fsp_member)
        db.flush() # Iterate to generate ID
        
        db.add(OrgMember(user_id=fsp_member.id, organization_id=fsp_org.id, status=MemberStatus.ACTIVE))
        # Role assignment skipped for brevity, but member status is active
        db.flush()

        # 3. Create Farmer User & Org
        farmer_email = f"farmer_assgn_{uuid4().hex[:8]}@example.com"
        farmer_user = User(email=farmer_email, password_hash=get_password_hash(password), first_name="Farmer", last_name="Assign", is_active=True)
        db.add(farmer_user)
        db.flush() # Iterate to generate ID
        
        farmer_org = Organization(name=f"Farmer Assign Org {uuid4().hex[:8]}", organization_type=OrganizationType.FARMING, status=OrganizationStatus.ACTIVE, contact_email="farmer@test.com")
        db.add(farmer_org)
        db.flush()
        
        db.add(OrgMember(user_id=farmer_user.id, organization_id=farmer_org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=farmer_user.id, organization_id=farmer_org.id, role_id=farming_owner_role.id))
        db.flush()
        # 4. Create Work Order (ACCEPTED)
        wo = WorkOrder(
            farming_organization_id=farmer_org.id,
            fsp_organization_id=fsp_org.id,
            title="Drone Spraying Service",
            description="Detailed description of spraying",
            status=WorkOrderStatus.ACCEPTED,
            work_order_number=f"WO-ASSIGN-{uuid4().hex[:8]}",
            created_by=farmer_user.id
        )
        db.add(wo)
        db.commit()
        
        print(f"Test Data: WO ID {wo.id}, FSP Admin {fsp_admin_email}, Member {fsp_member_email}")
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            
            # Login FSP Admin
            login_resp = await ac.post("/api/v1/auth/login", json={"email": fsp_admin_email, "password": password})
            token = login_resp.json()["data"]["tokens"]["access_token"]
            
            # 1. Assign Work Order
            print("Assigning Work Order...")
            assign_resp = await ac.put(
                f"/api/v1/work-orders/{wo.id}/assign",
                headers={"Authorization": f"Bearer {token}"},
                json={"assigned_to_user_id": str(fsp_member.id)}
            )
            print(f"Assign Status: {assign_resp.status_code}")
            if assign_resp.status_code == 200:
                data = assign_resp.json()["data"]
                if data.get("assigned_member") and data["assigned_member"]["id"] == str(fsp_member.id):
                    print("SUCCESS: Member assigned.")
                else:
                    print(f"FAILURE: Assignment not reflected in response. {data.get('assigned_member')}")
            else:
                print(f"FAILURE: {assign_resp.text}")
                
            # 2. Start Project
            print("Starting Project...")
            start_resp = await ac.post(
                f"/api/v1/work-orders/{wo.id}/start",
                headers={"Authorization": f"Bearer {token}"}
            )
            print(f"Start Status: {start_resp.status_code}")
            if start_resp.status_code == 200:
                data = start_resp.json()["data"]
                if data["status"] == "ACTIVE":
                     print("SUCCESS: Project started (Status: ACTIVE).")
                     if data.get("service_snapshot") and data["service_snapshot"]["name"] == "Drone Spraying Service":
                         print("SUCCESS: Service snapshot present.")
                     else:
                         print("FAILURE: Service snapshot missing.")
                else:
                     print(f"FAILURE: Status mismatch. {data['status']}")
            else:
                print(f"FAILURE: {start_resp.text}")
                
            # 3. Verify Active Provider Stats (Optional check)
            # Need to login as farmer
            login_farmer_resp = await ac.post("/api/v1/auth/login", json={"email": farmer_email, "password": password})
            token_farmer = login_farmer_resp.json()["data"]["tokens"]["access_token"]
            
            print("Checking Providers List...")
            prov_resp = await ac.get(
                "/api/v1/farming-services/providers",
                headers={"Authorization": f"Bearer {token_farmer}"}
            )
            if prov_resp.status_code == 200:
                prov_data = prov_resp.json()["data"]
                # Should have 1 active contract
                if len(prov_data) > 0 and prov_data[0]["active_contracts_count"] == 1:
                     print("SUCCESS: Active provider reflected correctly.")
                else:
                     print(f"FAILURE: Provider stats incorrect. {prov_data}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
