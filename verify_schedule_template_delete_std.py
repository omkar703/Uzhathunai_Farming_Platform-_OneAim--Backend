
import asyncio
import os
import sys
import json
import urllib.request
import urllib.error
from uuid import UUID, uuid4

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.schedule_template import ScheduleTemplate
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus
from app.core.security import get_password_hash

def make_request(method, url, data=None, headers=None):
    if headers is None:
        headers = {}
    
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

def main():
    print("Starting verification of Schedule Template DELETE (urllib)...")
    
    template_id = None
    email = f"std_del_{uuid4().hex[:8]}@example.com"
    password = "password123"

    db = SessionLocal()
    try:
        # 1. Setup Data
        # Create FSP Admin User
        user = User(email=email, password_hash=get_password_hash(password), is_active=True, first_name="Delete", last_name="Verifier")
        db.add(user)
        db.commit() 
        
        # Create FSP Org
        org = Organization(name=f"Std Del Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="std_del@test.com")
        db.add(org)
        db.commit()
        
        # Assign User as Admin
        role = db.query(Role).filter(Role.code == 'FSP_ADMIN').first() or db.query(Role).filter(Role.code == 'FSP_OWNER').first()
        db.add(OrgMember(user_id=user.id, organization_id=org.id, status=MemberStatus.ACTIVE))
        db.add(OrgMemberRole(user_id=user.id, organization_id=org.id, role_id=role.id))
        db.commit()
        
        # Create Crop Type
        from app.models.crop_data import CropType
        crop_type = db.query(CropType).first()
        if not crop_type:
            from app.models.crop_data import CropCategory
            cat = db.query(CropCategory).first()
            if not cat:
                cat = CropCategory(code="TEST_CAT", is_active=True)
                db.add(cat)
                db.commit()
            
            crop_type = CropType(code="TEST_CROP", category_id=cat.id, is_active=True)
            db.add(crop_type)
            db.commit()

        # Create Template
        template = ScheduleTemplate(
            code=f"STD_DEL_{uuid4().hex[:8]}",
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
        template_id = str(template.id)
        print(f"Created Template: {template_id}")

    finally:
        db.close()

    # 2. Login
    print("Logging in...")
    status, body = make_request("POST", "http://localhost:8000/api/v1/auth/login", {"email": email, "password": password})
    if status != 200:
        print(f"Login Failed: {status} {body}")
        return

    resp_json = json.loads(body)
    token = resp_json["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Call DELETE
    print(f"Calling DELETE /api/v1/schedule-templates/{template_id}...")
    status, body = make_request("DELETE", f"http://localhost:8000/api/v1/schedule-templates/{template_id}", headers=headers)
    
    print(f"DELETE Response: {status}")
    if status != 204:
        print(f"DELETE Failed Body: {body}")
        return

    # 4. Verify DB
    db = SessionLocal()
    try:
        t_check = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id).first()
        print(f"DB Check - is_active: {t_check.is_active}")
        
        if t_check.is_active is False:
            print("SUCCESS: Template soft-deleted.")
        else:
            print("FAILURE: Template is still active.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
