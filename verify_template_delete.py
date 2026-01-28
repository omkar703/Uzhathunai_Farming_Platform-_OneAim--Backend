
import asyncio
import os
import sys
from uuid import UUID
from datetime import date

# Add current directory to path
sys.path.append(os.getcwd())

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User

async def main():
    # Create a temporary FSP Admin to delete the template (or at least try to)
    # Since we can't delete another org's template easily without being that org admin, 
    # and we don't know the password for fsp1@gmail.com.
    # However, the error 500 happens *after* permission check within the delete logic?
    # Actually, if we are not the owner, we might get 403. 
    # But the 500 stack trace shows it reached `service.delete_template`.
    # This implies the user *was* authorized.
    
    # Let's try to simulate the specific condition by:
    # 1. Creating a fresh Template & Audit (linked)
    # 2. Trying to delete that Template
    
    print("Setting up test data for Template Delete Check...")
    from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus, AuditStatus
    from app.models.organization import Organization, OrgMember, OrgMemberRole
    from app.models.rbac import Role
    from app.models.audit import Audit
    from app.models.template import Template
    from app.core.security import get_password_hash
    from uuid import uuid4
    
    db = SessionLocal()
    try:
        # Create FSP Admin
        email = f"delete_tester_{uuid4().hex[:8]}@example.com"
        password = "password123"
        user = User(email=email, password_hash=get_password_hash(password), first_name="Delete", last_name="Tester", is_active=True)
        db.add(user)
        db.flush()
        
        # Create Org
        org = Organization(name=f"Delete Test Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="del@test.com")
        db.add(org)
        db.flush()
        
        # Add Member
        fsp_owner_role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
        db.add(OrgMember(user_id=user.id, organization_id=org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=user.id, organization_id=org.id, role_id=fsp_owner_role.id))
        db.flush()
        
        # Create Template
        template = Template(
            code=f"TMPL_{uuid4().hex[:8]}",
            is_system_defined=False,
            owner_org_id=org.id,
            is_active=True,
            version=1,
            created_by=user.id,
            updated_by=user.id
        )
        db.add(template)
        db.flush()
        template_id = str(template.id)
        
        # Create Farm
        from app.models.farm import Farm
        farm = Farm(
            organization_id=org.id,
            name="Test Farm",
            city="Test City"
        )
        db.add(farm)
        db.flush()

        # Create Plot
        from app.models.plot import Plot
        plot = Plot(
            farm_id=farm.id,
            name="Test Plot"
        )
        db.add(plot)
        db.flush()

        # Create Crop
        from app.models.crop import Crop
        crop = Crop(
            plot_id=plot.id,
            name="Test Crop",
            created_by=user.id
        )
        db.add(crop)
        db.flush()

        # Create Audit linked to Template
        audit = Audit(
            fsp_organization_id=org.id,
            farming_organization_id=org.id,
            template_id=template.id,
            status=AuditStatus.DRAFT,
            audit_number=f"AUD-{uuid4().hex[:8]}",
            name="Test Audit", # Required field
            crop_id=crop.id,
            created_by=user.id
        )
        db.add(audit)
        db.commit()
        
        print(f"Created Template {template_id} linked to Audit {audit.id}")
        
    except Exception as e:
        print(f"Setup Error: {e}")
        return
    finally:
        db.close()

    print(f"Attempting to login as {email}...")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        
        login_resp = await ac.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
        if login_resp.status_code != 200:
             print(f"Login Failed: {login_resp.text}")
             return
             
        token = login_resp.json()["data"]["tokens"]["access_token"]
        print("Login successful.")

        # Delete Template
        print(f"Attempting to delete template {template_id}...")
        resp = await ac.delete(
            f"/api/v1/farm-audit/templates/{template_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body: {resp.text}")
        
        if resp.status_code == 409:
            print("SUCCESS: Received 409 Conflict as expected.")
        elif resp.status_code == 500:
            print("FAILURE: Still receiving 500 Internal Server Error.")
        elif resp.status_code == 204:
            print("WARNING: Template was deleted! (Integrity error didn't trigger?)")
        else:
            print(f"Unexpected status: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
