import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
import io
from datetime import datetime

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.work_order import WorkOrder
from app.models.audit import Audit, AuditParameterInstance, AuditResponsePhoto
from app.models.video_session import VideoSession, VideoSessionStatus
from app.models.template import Template
from app.models.crop import Crop
from app.models.plot import Plot
from app.models.farm import Farm
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope,
    AuditStatus,
    PhotoSourceType
)

@pytest.fixture
def fsp_user(db: Session) -> User:
    from app.core.security import get_password_hash
    user = User(
        email=f"fsp_{uuid4().hex[:6]}@example.com",
        password_hash=get_password_hash("Pass123!"),
        first_name="FSP",
        last_name="Auditor",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def fsp_headers(client: TestClient, fsp_user: User) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": fsp_user.email, "password": "Pass123!"}
    )
    token = response.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def setup_data(db: Session, fsp_user: User):
    # 1. Create FSP Org
    fsp_org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE,
        is_approved=True
    )
    db.add(fsp_org)
    db.flush()
    
    # 2. Create Farming Org
    farm_org = Organization(
        name="Test Farm Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        is_approved=True
    )
    db.add(farm_org)
    db.flush()

    # 3. Create Work Order
    work_order = WorkOrder(
        fsp_organization_id=fsp_org.id,
        farming_organization_id=farm_org.id,
        title="Remote Audit WO",
        status="ACTIVE",
        total_amount=100
    )
    db.add(work_order)
    db.flush()

    # 4. Create Farm, Plot, Crop
    farm = Farm(name="Test Farm", organization_id=farm_org.id)
    db.add(farm)
    db.flush()
    
    plot = Plot(name="Test Plot", farm_id=farm.id)
    db.add(plot)
    db.flush()
    
    crop = Crop(name="Test Crop", plot_id=plot.id)
    db.add(crop)
    db.flush()

    # 5. Create Template & Audit
    template = Template(code=f"TPL-{uuid4().hex[:6]}", owner_org_id=fsp_org.id, version=1)
    db.add(template)
    db.flush()
    
    audit = Audit(
        name="Remote Audit",
        fsp_organization_id=fsp_org.id,
        farming_organization_id=farm_org.id,
        work_order_id=work_order.id,
        crop_id=crop.id,
        template_id=template.id,
        status=AuditStatus.IN_PROGRESS
    )
    db.add(audit)
    db.flush()

    # 6. Create Video Session
    video_session = VideoSession(
        work_order_id=work_order.id,
        audit_id=audit.id,
        status=VideoSessionStatus.ACTIVE,
        zoom_meeting_id="123456789"
    )
    db.add(video_session)
    db.commit()

    return {
        "fsp_org": fsp_org,
        "farm_org": farm_org,
        "work_order": work_order,
        "audit": audit,
        "video_session": video_session
    }

def test_capture_snapshot_e2e(client: TestClient, fsp_headers: dict, setup_data: dict, db: Session):
    audit_id = setup_data["audit"].id
    session_id = setup_data["video_session"].id
    
    # Create a mock image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    # Call the capture endpoint
    response = client.post(
        f"/api/v1/farm-audit/audits/{audit_id}/capture",
        headers=fsp_headers,
        data={"session_id": str(session_id)},
        files={"file": ("test.jpg", img_byte_arr, "image/jpeg")}
    )

    assert response.status_code == 202
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Snapshot capture initiated successfully"
    
    # Check if the photo record is created (it's a background task, so we might need a small wait or check syncly if tested locally)
    # In FastAPI TestClient + BackgroundTasks, they run synchronously unless configured otherwise.
    
    db.expire_all()
    photo = db.query(AuditResponsePhoto).filter(AuditResponsePhoto.audit_id == audit_id).first()
    assert photo is not None
    assert photo.source_type == PhotoSourceType.LIVE_CAPTURE
    assert "Live snapshot" in photo.caption
    assert photo.audit_id == audit_id

def test_capture_snapshot_mismatch_fails(client: TestClient, fsp_headers: dict, setup_data: dict, db: Session):
    audit_id = setup_data["audit"].id
    
    # Create another session linked to different work order
    other_wo = WorkOrder(
        fsp_organization_id=setup_data["fsp_org"].id,
        farming_organization_id=setup_data["farm_org"].id,
        title="Other WO",
        total_amount=50
    )
    db.add(other_wo)
    db.flush()
    
    wrong_session = VideoSession(
        work_order_id=other_wo.id,
        status=VideoSessionStatus.ACTIVE
    )
    db.add(wrong_session)
    db.commit()

    img = io.BytesIO(b"fake-image-data")
    
    response = client.post(
        f"/api/v1/farm-audit/audits/{audit_id}/capture",
        headers=fsp_headers,
        data={"session_id": str(wrong_session.id)},
        files={"file": ("test.jpg", img, "image/jpeg")}
    )

    assert response.status_code == 422
    assert "not linked to the same Work Order" in response.json()["message"]
