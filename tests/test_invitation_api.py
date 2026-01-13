"""
Integration tests for Invitation API endpoints.

Tests cover:
- POST /api/v1/invitations/{invitation_id}/accept
- POST /api/v1/invitations/{invitation_id}/reject
- Expired invitation handling
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.invitation import OrgMemberInvitation
from app.models.rbac import Role
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    InvitationStatus,
    UserRoleScope
)


@pytest.fixture
def owner_role(db: Session) -> Role:
    """Get or create OWNER role for FARMING organizations."""
    role = db.query(Role).filter(Role.code == 'OWNER').first()
    if not role:
        role = Role(
            code='OWNER',
            name='Owner',
            display_name='Organization Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of farming organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def admin_role(db: Session) -> Role:
    """Get or create ADMIN role for FARMING organizations."""
    role = db.query(Role).filter(Role.code == 'ADMIN').first()
    if not role:
        role = Role(
            code='ADMIN',
            name='Admin',
            display_name='Administrator',
            scope=UserRoleScope.ORGANIZATION,
            description='Organization administrator',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def member_role(db: Session) -> Role:
    """Get or create MEMBER role for FARMING organizations."""
    role = db.query(Role).filter(Role.code == 'MEMBER').first()
    if not role:
        role = Role(
            code='MEMBER',
            name='Member',
            display_name='Organization Member',
            scope=UserRoleScope.ORGANIZATION,
            description='Basic organization member',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def test_organization(db: Session, test_user: User, owner_role: Role) -> Organization:
    """Create a test organization with owner membership."""
    org = Organization(
        name="Test Organization",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create owner membership
    member = OrgMember(
        user_id=test_user.id,
        organization_id=org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
    # Assign owner role
    member_role = OrgMemberRole(
        user_id=test_user.id,
        organization_id=org.id,
        role_id=owner_role.id,
        is_primary=True,
        assigned_by=test_user.id
    )
    db.add(member_role)
    db.commit()
    
    return org


class TestAcceptInvitation:
    """Tests for POST /api/v1/invitations/{invitation_id}/accept."""
    
    def test_accept_invitation_success(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test successful invitation acceptance."""
        # Create a new user to accept invitation
        from app.core.security import get_password_hash
        invitee = User(
            email="invitee@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Invitee",
            last_name="User",
            phone="+919999999999",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee)
        db.commit()
        db.refresh(invitee)
        
        # Create invitation
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email=invitee.email,
            invitee_user_id=invitee.id,
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now,
            expires_at=now + timedelta(days=7),
            message="Welcome to our organization!"
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Accept invitation
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/accept",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert data["organization_id"] == str(test_organization.id)
        assert "member_id" in data
        
        # Verify invitation status updated
        db.refresh(invitation)
        assert invitation.status == InvitationStatus.ACCEPTED
        assert invitation.responded_at is not None
        
        # Verify membership created
        member = db.query(OrgMember).filter(
            OrgMember.user_id == invitee.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        assert member.invitation_id == invitation.id
        
        # Verify role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == invitee.id,
            OrgMemberRole.organization_id == test_organization.id,
            OrgMemberRole.role_id == admin_role.id
        ).first()
        assert member_role is not None
        assert member_role.is_primary is True
    
    def test_accept_invitation_not_found(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test accepting non-existent invitation."""
        fake_id = uuid4()
        
        response = client.post(
            f"/api/v1/invitations/{fake_id}/accept",
            headers=auth_headers
        )
        
        # Should fail with not found error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["message"].lower()
    
    def test_accept_invitation_wrong_user(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test accepting invitation by wrong user."""
        # Create invitation for different email
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email="different@example.com",
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now,
            expires_at=now + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Create a different user
        from app.core.security import get_password_hash
        wrong_user = User(
            email="wrong@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Wrong",
            last_name="User",
            phone="+919888888888",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(wrong_user)
        db.commit()
        db.refresh(wrong_user)
        
        # Login as wrong user
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": wrong_user.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to accept invitation
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/accept",
            headers=headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
        data = response.json()
        assert "not for this user" in data["message"].lower()
    
    def test_accept_invitation_already_accepted(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test accepting already accepted invitation."""
        # Create a new user
        from app.core.security import get_password_hash
        invitee = User(
            email="accepted@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Accepted",
            last_name="User",
            phone="+919777777777",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee)
        db.commit()
        db.refresh(invitee)
        
        # Create invitation with ACCEPTED status
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email=invitee.email,
            invitee_user_id=invitee.id,
            role_id=admin_role.id,
            status=InvitationStatus.ACCEPTED,
            invited_at=now,
            responded_at=now,
            expires_at=now + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to accept invitation again
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/accept",
            headers=headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
        data = response.json()
        assert "accepted" in data["message"].lower()
    
    def test_accept_invitation_unauthorized(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test that unauthorized requests are rejected."""
        # Create invitation
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email="test@example.com",
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now,
            expires_at=now + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Try to accept without authentication
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/accept"
        )
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]


class TestRejectInvitation:
    """Tests for POST /api/v1/invitations/{invitation_id}/reject."""
    
    def test_reject_invitation_success(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test successful invitation rejection."""
        # Create a new user to reject invitation
        from app.core.security import get_password_hash
        invitee = User(
            email="rejecter@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Rejecter",
            last_name="User",
            phone="+919666666666",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee)
        db.commit()
        db.refresh(invitee)
        
        # Create invitation
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email=invitee.email,
            invitee_user_id=invitee.id,
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now,
            expires_at=now + timedelta(days=7),
            message="Join us!"
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Reject invitation
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/reject",
            headers=headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        
        # Verify invitation status updated
        db.refresh(invitation)
        assert invitation.status == InvitationStatus.REJECTED
        assert invitation.responded_at is not None
        
        # Verify no membership created
        member = db.query(OrgMember).filter(
            OrgMember.user_id == invitee.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        assert member is None
        
        # Verify no role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == invitee.id,
            OrgMemberRole.organization_id == test_organization.id
        ).first()
        assert member_role is None
    
    def test_reject_invitation_not_found(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test rejecting non-existent invitation."""
        fake_id = uuid4()
        
        response = client.post(
            f"/api/v1/invitations/{fake_id}/reject",
            headers=auth_headers
        )
        
        # Should fail with not found error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["message"].lower()
    
    def test_reject_invitation_wrong_user(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test rejecting invitation by wrong user."""
        # Create invitation for different email
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email="different@example.com",
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now,
            expires_at=now + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Create a different user
        from app.core.security import get_password_hash
        wrong_user = User(
            email="wrongreject@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Wrong",
            last_name="Reject",
            phone="+919555555555",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(wrong_user)
        db.commit()
        db.refresh(wrong_user)
        
        # Login as wrong user
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": wrong_user.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to reject invitation
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/reject",
            headers=headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
        data = response.json()
        assert "not for this user" in data["message"].lower()
    
    def test_reject_invitation_already_rejected(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test rejecting already rejected invitation."""
        # Create a new user
        from app.core.security import get_password_hash
        invitee = User(
            email="alreadyrejected@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Already",
            last_name="Rejected",
            phone="+919444444444",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee)
        db.commit()
        db.refresh(invitee)
        
        # Create invitation with REJECTED status
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email=invitee.email,
            invitee_user_id=invitee.id,
            role_id=admin_role.id,
            status=InvitationStatus.REJECTED,
            invited_at=now,
            responded_at=now,
            expires_at=now + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to reject invitation again
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/reject",
            headers=headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
        data = response.json()
        assert "rejected" in data["message"].lower()
    
    def test_reject_invitation_unauthorized(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test that unauthorized requests are rejected."""
        # Create invitation
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email="test@example.com",
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now,
            expires_at=now + timedelta(days=7)
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Try to reject without authentication
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/reject"
        )
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]


class TestExpiredInvitation:
    """Tests for expired invitation handling."""
    
    def test_accept_expired_invitation(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test accepting expired invitation."""
        # Create a new user
        from app.core.security import get_password_hash
        invitee = User(
            email="expired@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Expired",
            last_name="User",
            phone="+919333333333",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee)
        db.commit()
        db.refresh(invitee)
        
        # Create invitation with past expiry date
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email=invitee.email,
            invitee_user_id=invitee.id,
            role_id=admin_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now - timedelta(days=10),
            expires_at=now - timedelta(days=3)  # Expired 3 days ago
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to accept expired invitation
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/accept",
            headers=headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
        data = response.json()
        assert "expired" in data["message"].lower()
        
        # Verify invitation status updated to EXPIRED
        db.refresh(invitation)
        assert invitation.status == InvitationStatus.EXPIRED
        
        # Verify no membership created
        member = db.query(OrgMember).filter(
            OrgMember.user_id == invitee.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        assert member is None
    
    def test_expired_invitation_marked_correctly(
        self,
        client: TestClient,
        test_organization: Organization,
        member_role: Role,
        db: Session
    ):
        """Test that expired invitation is marked as EXPIRED when accessed."""
        # Create a new user
        from app.core.security import get_password_hash
        invitee = User(
            email="expiredmark@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Expired",
            last_name="Mark",
            phone="+919222222222",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee)
        db.commit()
        db.refresh(invitee)
        
        # Create invitation with past expiry date but PENDING status
        now = datetime.now(timezone.utc)
        invitation = OrgMemberInvitation(
            organization_id=test_organization.id,
            inviter_id=test_organization.created_by,
            invitee_email=invitee.email,
            invitee_user_id=invitee.id,
            role_id=member_role.id,
            status=InvitationStatus.PENDING,
            invited_at=now - timedelta(days=8),
            expires_at=now - timedelta(days=1)  # Expired 1 day ago
        )
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        # Verify initial status is PENDING
        assert invitation.status == InvitationStatus.PENDING
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to accept expired invitation
        response = client.post(
            f"/api/v1/invitations/{invitation.id}/accept",
            headers=headers
        )
        
        # Should fail
        assert response.status_code == 422
        
        # Verify status changed to EXPIRED
        db.refresh(invitation)
        assert invitation.status == InvitationStatus.EXPIRED
