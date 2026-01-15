"""
Pytest tests for Video Zoom API endpoints.
Tests the Zoom meeting scheduling and join URL functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus
from app.models.work_order import WorkOrder
from app.models.video_session import VideoSession, VideoSessionStatus
from app.models.rbac import Role
from app.core.security import get_password_hash


@pytest.fixture
def farming_org(db: Session) -> Organization:
    """Create an approved farming organization."""
    org = Organization(
        name="Test Farm Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        is_approved=True,
        registration_number="FARM001"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def fsp_org(db: Session) -> Organization:
    """Create an approved FSP organization."""
    org = Organization(
        name="Test FSP Org",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE,
        is_approved=True,
        registration_number="FSP001"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def unapproved_org(db: Session) -> Organization:
    """Create an unapproved organization."""
    org = Organization(
        name="Unapproved Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.PENDING,
        is_approved=False,
        registration_number="UNAPP001"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def fsp_user(db: Session, fsp_org: Organization) -> User:
    """Create an FSP user who is a member of the FSP org."""
    user = User(
        email="fspuser@test.com",
        password_hash=get_password_hash("FspUser123!"),
        first_name="FSP",
        last_name="User",
        phone="+1234567892",
        preferred_language="en",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add as org member
    member = OrgMember(
        user_id=user.id,
        organization_id=fsp_org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
    return user


@pytest.fixture
def fsp_user_headers(client: TestClient, fsp_user: User) -> dict:
    """Get authentication headers for FSP user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": fsp_user.email,
            "password": "FspUser123!",
            "remember_me": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    access_token = data["tokens"]["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def work_order(db: Session, farming_org: Organization, fsp_org: Organization) -> WorkOrder:
    """Create a work order between farming and FSP orgs."""
    wo = WorkOrder(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        title="Test Work Order",
        description="Test work order for video call",
        status="NEW"
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo


@pytest.fixture
def work_order_unapproved(db: Session, unapproved_org: Organization, fsp_org: Organization) -> WorkOrder:
    """Create a work order with an unapproved org."""
    wo = WorkOrder(
        farming_organization_id=unapproved_org.id,
        fsp_organization_id=fsp_org.id,
        title="Unapproved Work Order",
        description="Work order with unapproved org",
        status="NEW"
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo


@pytest.fixture
def active_video_session(db: Session, work_order: WorkOrder, fsp_user: User) -> VideoSession:
    """Create an active video session."""
    session = VideoSession(
        work_order_id=work_order.id,
        topic="Test Meeting",
        start_time=datetime.utcnow() + timedelta(hours=1),
        duration=45,
        status=VideoSessionStatus.ACTIVE,
        created_by=fsp_user.id,
        zoom_meeting_id="123456789",
        join_url="https://zoom.us/j/123456789",
        start_url="https://zoom.us/s/123456789",
        password="testpass"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


class TestScheduleMeeting:
    """Tests for meeting scheduling endpoint."""
    
    @patch("app.api.v1.video_zoom.process_zoom_meeting")
    def test_schedule_meeting_success(
        self,
        mock_process: AsyncMock,
        client: TestClient,
        fsp_user_headers: dict,
        work_order: WorkOrder
    ):
        """Test successful meeting scheduling."""
        response = client.post(
            "/api/v1/video/schedule",
            headers=fsp_user_headers,
            json={
                "work_order_id": str(work_order.id),
                "topic": "Test Video Call",
                "duration": 30
            }
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data["data"]
    
    def test_schedule_meeting_work_order_not_found(
        self,
        client: TestClient,
        fsp_user_headers: dict
    ):
        """Test scheduling with non-existent work order."""
        fake_id = str(uuid4())
        response = client.post(
            "/api/v1/video/schedule",
            headers=fsp_user_headers,
            json={
                "work_order_id": fake_id,
                "topic": "Test Video Call",
                "duration": 30
            }
        )
        
        assert response.status_code == 404
    
    def test_schedule_meeting_org_not_approved(
        self,
        client: TestClient,
        fsp_user_headers: dict,
        work_order_unapproved: WorkOrder
    ):
        """Test scheduling when organization is not approved."""
        response = client.post(
            "/api/v1/video/schedule",
            headers=fsp_user_headers,
            json={
                "work_order_id": str(work_order_unapproved.id),
                "topic": "Test Video Call",
                "duration": 30
            }
        )
        
        assert response.status_code == 403
        data = response.json()
        assert "ORG_NOT_APPROVED" in str(data)
    
    def test_schedule_meeting_no_auth(
        self,
        client: TestClient,
        work_order: WorkOrder
    ):
        """Test scheduling without authentication."""
        response = client.post(
            "/api/v1/video/schedule",
            json={
                "work_order_id": str(work_order.id),
                "topic": "Test Video Call",
                "duration": 30
            }
        )
        
        assert response.status_code == 401


class TestGetJoinUrl:
    """Tests for getting meeting join URL."""
    
    def test_get_join_url_as_host(
        self,
        client: TestClient,
        fsp_user_headers: dict,
        active_video_session: VideoSession
    ):
        """Test getting join URL as the meeting host."""
        response = client.get(
            f"/api/v1/video/{active_video_session.id}/join-url",
            headers=fsp_user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["role"] == "host"
        assert "start_url" in data["data"]["url"] or data["data"]["url"] is not None
    
    def test_get_join_url_session_not_found(
        self,
        client: TestClient,
        fsp_user_headers: dict
    ):
        """Test getting join URL for non-existent session."""
        fake_id = str(uuid4())
        response = client.get(
            f"/api/v1/video/{fake_id}/join-url",
            headers=fsp_user_headers
        )
        
        assert response.status_code == 404
    
    def test_get_join_url_pending_session(
        self,
        client: TestClient,
        fsp_user_headers: dict,
        db: Session,
        work_order: WorkOrder,
        fsp_user: User
    ):
        """Test getting join URL for a pending session."""
        # Create a pending session
        pending_session = VideoSession(
            work_order_id=work_order.id,
            topic="Pending Meeting",
            start_time=datetime.utcnow() + timedelta(hours=1),
            duration=45,
            status=VideoSessionStatus.PENDING,
            created_by=fsp_user.id
        )
        db.add(pending_session)
        db.commit()
        db.refresh(pending_session)
        
        response = client.get(
            f"/api/v1/video/{pending_session.id}/join-url",
            headers=fsp_user_headers
        )
        
        assert response.status_code == 400
        assert "not active" in response.json()["detail"].lower()
    
    def test_get_join_url_no_auth(
        self,
        client: TestClient,
        active_video_session: VideoSession
    ):
        """Test getting join URL without authentication."""
        response = client.get(
            f"/api/v1/video/{active_video_session.id}/join-url"
        )
        
        assert response.status_code == 401


class TestVideoSessionModel:
    """Tests for VideoSession model."""
    
    def test_video_session_creation(
        self,
        db: Session,
        work_order: WorkOrder,
        fsp_user: User
    ):
        """Test creating a video session."""
        session = VideoSession(
            work_order_id=work_order.id,
            topic="Model Test Meeting",
            start_time=datetime.utcnow() + timedelta(hours=2),
            duration=60,
            status=VideoSessionStatus.PENDING,
            created_by=fsp_user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        assert session.id is not None
        assert session.status == VideoSessionStatus.PENDING
        assert session.work_order_id == work_order.id
    
    def test_video_session_status_transitions(
        self,
        db: Session,
        work_order: WorkOrder,
        fsp_user: User
    ):
        """Test video session status transitions."""
        session = VideoSession(
            work_order_id=work_order.id,
            topic="Status Test",
            status=VideoSessionStatus.PENDING,
            created_by=fsp_user.id
        )
        db.add(session)
        db.commit()
        
        # Transition to ACTIVE
        session.status = VideoSessionStatus.ACTIVE
        session.zoom_meeting_id = "123"
        session.join_url = "https://zoom.us/j/123"
        session.start_url = "https://zoom.us/s/123"
        db.commit()
        db.refresh(session)
        
        assert session.status == VideoSessionStatus.ACTIVE
        
        # Transition to COMPLETED
        session.status = VideoSessionStatus.COMPLETED
        db.commit()
        db.refresh(session)
        
        assert session.status == VideoSessionStatus.COMPLETED
