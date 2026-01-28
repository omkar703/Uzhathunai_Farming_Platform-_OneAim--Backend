
import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.schedule_template import ScheduleTemplate
from app.models.user import User
from app.core.security import get_password_hash
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus

@pytest.mark.asyncio
async def test_delete_schedule_template(db: Session, client: AsyncClient):
    # 1. Setup Data
    # Create FSP Admin User
    email = f"del_p_test_{uuid4().hex[:8]}@example.com"
    password = "password123"
    user = User(email=email, password_hash=get_password_hash(password), is_active=True, first_name="Delete", last_name="Verifier")
    db.add(user)
    db.commit() # Commit to get ID
    
    # Create FSP Org
    org = Organization(name=f"Del P Org {uuid4().hex[:8]}", organization_type=OrganizationType.FSP, status=OrganizationStatus.ACTIVE, contact_email="del_p@test.com")
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
    # Ensure crop type exists
    if not crop_type:
        from app.models.crop_data import CropCategory
        cat = CropCategory(code="TEST_CAT", is_active=True)
        db.add(cat)
        db.commit()
        crop_type = CropType(code="TEST_CROP", category_id=cat.id, is_active=True)
        db.add(crop_type)
        db.commit()

    # Create Template
    template = ScheduleTemplate(
        code=f"DEL_T_{uuid4().hex[:8]}",
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

    # 2. Login
    login_resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Call DELETE
    resp = await client.delete(f"/api/v1/schedule-templates/{template_id}", headers=headers)
    assert resp.status_code == 204

    # 4. Verify DB
    db.expire_all()
    t_check = db.query(ScheduleTemplate).filter(ScheduleTemplate.id == template_id).first()
    assert t_check is not None
    assert t_check.is_active is False
