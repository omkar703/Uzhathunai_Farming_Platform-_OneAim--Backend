
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
from app.models.rbac import Role
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus, WorkOrderStatus
from app.core.security import get_password_hash
from app.main import app
from httpx import AsyncClient, ASGITransport

async def main():
    db = SessionLocal()
    try:
        print("Setting up test data for farming providers...")
        
        # 0. Get Roles
        farming_owner_role = db.query(Role).filter(Role.code == 'OWNER').first()
        fsp_owner_role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
        
        if not farming_owner_role or not fsp_owner_role:
            print("Roles not found! Run seed scripts.")
            return

        # 1. Create FSP User & Org
        fsp_email = f"fsp_prov_{uuid4().hex[:8]}@example.com"
        password = "password123"
        fsp_user = User(email=fsp_email, password_hash=get_password_hash(password), first_name="FSP", last_name="Provider", is_active=True)
        db.add(fsp_user)
        
        fsp_org = Organization(name=f"FSP Prov Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="fsp@test.com")
        db.add(fsp_org)
        db.flush()
        
        # FSP Membership
        db.add(OrgMember(user_id=fsp_user.id, organization_id=fsp_org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=fsp_user.id, organization_id=fsp_org.id, role_id=fsp_owner_role.id))
        
        # 2. Create Farmer User & Org
        farmer_email = f"farmer_prov_{uuid4().hex[:8]}@example.com"
        farmer_user = User(email=farmer_email, password_hash=get_password_hash(password), first_name="Farmer", last_name="Consumer", is_active=True)
        db.add(farmer_user)
        
        farmer_org = Organization(name=f"Farmer Prov Org {uuid4().hex[:8]}", organization_type=OrganizationType.FARMING, status=OrganizationStatus.ACTIVE, contact_email="farmer@test.com")
        db.add(farmer_org)
        db.flush()
        
        # Farmer Membership
        db.add(OrgMember(user_id=farmer_user.id, organization_id=farmer_org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=farmer_user.id, organization_id=farmer_org.id, role_id=farming_owner_role.id))
        
        # 3. Create Work Order (Active)
        wo_active = WorkOrder(
            farming_organization_id=farmer_org.id,
            fsp_organization_id=fsp_org.id,
            title="Active Contract",
            status=WorkOrderStatus.ACTIVE,
            work_order_number=f"WO-ACT-{uuid4().hex[:8]}"
        )
        db.add(wo_active)
        
        # 4. Create Work Order (Completed/History)
        wo_completed = WorkOrder(
            farming_organization_id=farmer_org.id,
            fsp_organization_id=fsp_org.id,
            title="Completed Contract",
            status=WorkOrderStatus.COMPLETED,
            work_order_number=f"WO-COMP-{uuid4().hex[:8]}"
        )
        db.add(wo_completed)
        
        db.commit()
        
        print(f"Test Data Created: FSP {fsp_org.name}, Farmer {farmer_org.name}")
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            
            # Login Farmer
            user_b_resp = await ac.post("/api/v1/auth/login", json={"email": farmer_email, "password": password})
            token_b = user_b_resp.json()["data"]["tokens"]["access_token"]
            
            # Call GET /providers
            print("Fetching Farming Providers...")
            response = await ac.get(
                "/api/v1/farming-services/providers",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            
            print(f"Response Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()["data"]
                print(f"Providers found: {len(data)}")
                if len(data) > 0:
                    provider = data[0]
                    print(f"Provider: {provider['name']}")
                    print(f"Active Contracts: {provider['active_contracts_count']}")
                    print(f"Total History: {provider['total_contracts_history']}")
                    
                    if provider['id'] == str(fsp_org.id):
                        print("SUCCESS: FSP found in providers list.")
                        if provider['active_contracts_count'] == 1 and provider['total_contracts_history'] == 2:
                            print("SUCCESS: Contract counts match.")
                        else:
                            print(f"FAILURE: Counts mismatch. Expected 1 active, 2 total. Got {provider['active_contracts_count']}, {provider['total_contracts_history']}")
                    else:
                        print("FAILURE: Wrong FSP ID.")
                else:
                    print("FAILURE: No providers returned.")
            else:
                print(f"FAILURE: API Error: {response.text}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
