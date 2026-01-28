
import asyncio
import os
import sys
from uuid import UUID, uuid4

# Add current directory to path
sys.path.append(os.getcwd())

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.schedule_template import ScheduleTemplate
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus
from app.core.security import get_password_hash

async def main():
    print("Starting verification of Schedule Template DELETE...")
    
    db = SessionLocal()
    try:
        # 1. Setup Data
        # Create FSP Admin User
        email = f"delete_verifier_{uuid4().hex[:8]}@example.com"
        password = "password123"
        user = User(email=email, password_hash=get_password_hash(password), is_active=True, first_name="Delete", last_name="Verifier")
        db.add(user)
        db.flush()
        
        # Create FSP Org
        org = Organization(name=f"Delete Verify Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="del_ver@test.com")
        db.add(org)
        db.flush()
        
        # Assign User as Admin/Owner
        role = db.query(Role).filter(Role.code == 'FSP_ADMIN').first()
        if not role:
             role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
             
        db.add(OrgMember(user_id=user.id, organization_id=org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=user.id, organization_id=org.id, role_id=role.id))
        
        # Create Crop Type needed for template
        from app.models.crop_data import CropType
        crop_type = db.query(CropType).first()
        if not crop_type:
            print("No crop type found, skipping test (or create one)")
            return

        # Create Schedule Template to Delete
        template = ScheduleTemplate(
            code=f"DEL_TMPL_{uuid4().hex[:8]}",
            crop_type_id=crop_type.id,
            is_system_defined=False,
            owner_org_id=org.id,
            version=1,
            is_active=True,
            created_by=user.id,
            updated_by=user.id
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        template_id = str(template.id)
        
        print(f"Created Template: {template_id} (Active: {template.is_active})")
        
    finally:
        db.close()

    # 2. Authenticate
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_resp = await ac.post("/api/v1/auth/login", json={"email": email, "password": password})
        if login_resp.status_code != 200:
            print(f"Login Failed: {login_resp.text}")
            return
        
        token = login_resp.json()["data"]["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Call DELETE Endpoint
        print(f"Calling DELETE /api/v1/schedule-templates/{template_id}...")
        resp = await ac.delete(f"/api/v1/schedule-templates/{template_id}", headers=headers)
        
        print(f"Delete Response Code: {resp.status_code}")
        if resp.status_code != 204:
            print(f"Delete Failed Body: {resp.text}")
            return
            
        print("Delete request successful (204).")

    # 4. Verify Database State
    db = SessionLocal()
    try:
        params_check = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id).first()
        print(f"Database State - is_active: {params_check.is_active}")
        
        if not params_check.is_active:
            print("SUCCESS: Template is confirmed soft-deleted.")
        else:
            print("FAILURE: Template is still active!")
            
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
