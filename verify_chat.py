
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
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus, WorkOrderStatus, ChatContextType
from app.core.security import get_password_hash
from app.main import app
from httpx import AsyncClient, ASGITransport

async def main():
    db = SessionLocal()
    try:
        print("Setting up test data for chat...")
        
        # 1. Create FSP User & Org
        fsp_email = f"fsp_chat_{uuid4().hex[:8]}@example.com"
        password = "password123"
        fsp_user = User(email=fsp_email, password_hash=get_password_hash(password), first_name="FSP", last_name="Chat", is_active=True)
        db.add(fsp_user)
        
        fsp_org = Organization(name=f"FSP Chat Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="fsp@chat.com")
        db.add(fsp_org)
        db.flush()
        
        db.add(OrgMember(user_id=fsp_user.id, organization_id=fsp_org.id, status=MemberStatus.ACTIVE))
        # Add role... skipping explicit role check based on my simplified knowledge of backend, 
        # but in real scenario roles might be needed. 
        # ChatService checks 'Active Member' status, not specific role permissions for basic chat usually,
        # but create_channel might need context access.
        
        # 2. Create Farmer User & Org
        farmer_email = f"farmer_chat_{uuid4().hex[:8]}@example.com"
        farmer_user = User(email=farmer_email, password_hash=get_password_hash(password), first_name="Farmer", last_name="Chat", is_active=True)
        db.add(farmer_user)
        
        farmer_org = Organization(name=f"Farmer Chat Org {uuid4().hex[:8]}", organization_type=OrganizationType.FARMING, status=OrganizationStatus.ACTIVE, contact_email="farmer@chat.com")
        db.add(farmer_org)
        db.flush()
        
        db.add(OrgMember(user_id=farmer_user.id, organization_id=farmer_org.id, status=MemberStatus.ACTIVE))
        
        # 3. Create Work Order
        wo = WorkOrder(
            farming_organization_id=farmer_org.id,
            fsp_organization_id=fsp_org.id,
            title="Chat Context WO",
            status=WorkOrderStatus.ACTIVE,
            work_order_number=f"WO-CHAT-{uuid4().hex[:8]}"
        )
        db.add(wo)
        db.commit()
        
        print(f"Test Data: WO ID {wo.id}, FSP {fsp_email}, Farmer {farmer_email}")
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # Login FSP
            user_a_resp = await ac.post("/api/v1/auth/login", json={"email": fsp_email, "password": password})
            token_a = user_a_resp.json()["data"]["tokens"]["access_token"]
            
            # Login Farmer
            user_b_resp = await ac.post("/api/v1/auth/login", json={"email": farmer_email, "password": password})
            token_b = user_b_resp.json()["data"]["tokens"]["access_token"]
            
            # 1. Create Channel (as FSP)
            print("Creating Channel...")
            create_resp = await ac.post(
                "/api/v1/chat/channels",
                headers={"Authorization": f"Bearer {token_a}"},
                json={
                    "participant_org_id": str(farmer_org.id), # Not strictly needed if inferred from WO context
                    "context_type": "WORK_ORDER",
                    "context_id": str(wo.id),
                    "name": "General Chat"
                }
            )
            print(f"Create Channel Status: {create_resp.status_code}")
            if create_resp.status_code != 201:
                print(create_resp.text)
                return
                
            channel_id = create_resp.json()["data"]["id"]
            print(f"Channel ID: {channel_id}")
            
            # 2. Send Message (as FSP)
            print("Sending Message...")
            send_resp = await ac.post(
                f"/api/v1/chat/channels/{channel_id}/messages",
                headers={"Authorization": f"Bearer {token_a}"},
                json={"content": "Hello Farmer!", "message_type": "TEXT"}
            )
            print(f"Send Message Status: {send_resp.status_code}")
            
            # 3. Get Messages (as Farmer)
            print("Retrieving Messages...")
            get_resp = await ac.get(
                f"/api/v1/chat/channels/{channel_id}/messages",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            print(f"Get Messages Status: {get_resp.status_code}")
            data = get_resp.json()["data"]["items"]
            print(f"Messages found: {len(data)}")
            
            if len(data) > 0 and data[0]["content"] == "Hello Farmer!":
                print("SUCCESS: Chat flow verified.")
            else:
                print("FAILURE: Message not found or incorrect.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
