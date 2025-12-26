"""
End-to-End test for Member Invitation Flow.

Task 12.3: Test member invitation flow
- Invite member with role
- Verify invitation created
- Verify invitation email sent (logged for now, actual email in Phase 8)
- Accept invitation
- Verify membership created
- Verify role assigned

Requirements: FR2.1, FR2.4
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

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
        name="E2E Invitation Test Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        description="Organization for testing invitation flow",
        district="Coimbatore",
        pincode="641001",
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


class TestE2EMemberInvitationFlow:
    """
    End-to-end test for complete member invitation flow.
    
    This test verifies the entire workflow from invitation creation
    through acceptance and membership establishment.
    """
    
    def test_complete_member_invitation_flow(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """
        Test complete member invitation flow from invitation to acceptance.
        
        Requirements: FR2.1, FR2.4
        
        Steps:
        1. Invite member with role via API
        2. Verify invitation created in database
        3. Verify invitation email sent (mocked)
        4. Create invitee user account
        5. Accept invitation via API
        6. Verify membership created
        7. Verify role assigned
        8. Verify invitation status updated to ACCEPTED
        """
        # Step 1: Invite member with role via API
        invitee_email = "newmember@example.com"
        invitation_message = "Welcome to our farming organization!"
        
        invite_payload = {
            "invitee_email": invitee_email,
            "role_id": str(admin_role.id),
            "message": invitation_message,
            "expires_in_days": 7
        }
        
        invite_response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=invite_payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert invite_response.status_code == 201, \
            f"Expected 201, got {invite_response.status_code}: {invite_response.text}"
        
        invite_data = invite_response.json()
        
        assert "id" in invite_data
        assert invite_data["invitee_email"] == invitee_email
        assert invite_data["role_id"] == str(admin_role.id)
        assert invite_data["status"] == "PENDING"
        assert invite_data["message"] == invitation_message
        assert invite_data["organization_id"] == str(test_organization.id)
        assert invite_data["inviter_id"] == str(test_user.id)
        assert "invited_at" in invite_data
        assert "expires_at" in invite_data
        
        invitation_id = invite_data["id"]
        
        # Step 2: Verify invitation created in database
        invitation = db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        assert invitation is not None, "Invitation not found in database"
        assert invitation.organization_id == test_organization.id
        assert invitation.inviter_id == test_user.id
        assert invitation.invitee_email == invitee_email
        assert invitation.role_id == admin_role.id
        assert invitation.status == InvitationStatus.PENDING
        assert invitation.message == invitation_message
        assert invitation.invited_at is not None
        assert invitation.expires_at is not None
        assert invitation.responded_at is None
        assert invitation.invitee_user_id is None  # User doesn't exist yet
        
        # Verify expiry date is in the future
        assert invitation.expires_at > datetime.now(timezone.utc), \
            "Invitation expiry date should be in the future"
        
        # Step 3: Verify invitation email sent (logged for now)
        # Note: Email sending is logged in the service (TODO for Phase 8)
        # For now, we just verify the invitation was created successfully
        # In Phase 8, this will be replaced with actual email service verification
        
        # Step 4: Create invitee user account
        from app.core.security import get_password_hash
        invitee_user = User(
            email=invitee_email,
            password_hash=get_password_hash("InviteePass123!"),
            first_name="New",
            last_name="Member",
            phone="+919876543210",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee_user)
        db.commit()
        db.refresh(invitee_user)
        
        # Login as invitee to get auth token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee_email,
                "password": "InviteePass123!",
                "remember_me": False
            }
        )
        
        assert login_response.status_code == 200, \
            f"Login failed: {login_response.status_code}: {login_response.text}"
        
        invitee_token = login_response.json()["tokens"]["access_token"]
        invitee_headers = {"Authorization": f"Bearer {invitee_token}"}
        
        # Step 5: Accept invitation via API
        accept_response = client.post(
            f"/api/v1/invitations/{invitation_id}/accept",
            headers=invitee_headers
        )
        
        # Verify API response
        assert accept_response.status_code == 200, \
            f"Expected 200, got {accept_response.status_code}: {accept_response.text}"
        
        accept_data = accept_response.json()
        
        assert accept_data["success"] is True
        assert "message" in accept_data
        assert accept_data["organization_id"] == str(test_organization.id)
        assert "member_id" in accept_data
        
        member_id = accept_data["member_id"]
        
        # Step 6: Verify membership created
        member = db.query(OrgMember).filter(
            OrgMember.id == member_id
        ).first()
        
        assert member is not None, "Membership not found in database"
        assert member.user_id == invitee_user.id
        assert member.organization_id == test_organization.id
        assert member.status == MemberStatus.ACTIVE, \
            f"Expected ACTIVE member status, got {member.status}"
        assert member.joined_at is not None
        assert member.left_at is None
        assert member.invited_by == test_user.id
        assert member.invitation_id == invitation.id
        assert member.created_at is not None
        
        # Step 7: Verify role assigned
        member_role_assignment = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == invitee_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).first()
        
        assert member_role_assignment is not None, \
            "Role assignment not found in database"
        assert member_role_assignment.role_id == admin_role.id, \
            "Incorrect role assigned"
        assert member_role_assignment.is_primary is True, \
            "Role should be marked as primary"
        assert member_role_assignment.assigned_at is not None
        assert member_role_assignment.assigned_by == test_user.id
        assert member_role_assignment.created_at is not None
        
        # Verify the role is actually ADMIN
        role = db.query(Role).filter(Role.id == member_role_assignment.role_id).first()
        assert role is not None
        assert role.code == 'ADMIN'
        assert role.name == 'ADMIN'
        assert role.scope == UserRoleScope.ORGANIZATION
        
        # Step 8: Verify invitation status updated to ACCEPTED
        db.refresh(invitation)
        
        assert invitation.status == InvitationStatus.ACCEPTED, \
            f"Expected ACCEPTED status, got {invitation.status}"
        assert invitation.responded_at is not None, \
            "Responded timestamp should be set"
        assert invitation.invitee_user_id == invitee_user.id, \
            "Invitee user ID should be set"
        
        # Verify responded_at is recent (within last minute)
        time_diff = datetime.now(timezone.utc) - invitation.responded_at
        assert time_diff.total_seconds() < 60, \
            "Responded timestamp should be recent"
        
        # Additional verification: User can now access organization
        org_list_response = client.get(
            "/api/v1/organizations",
            headers=invitee_headers
        )
        
        assert org_list_response.status_code == 200
        organizations = org_list_response.json()
        
        # Verify new member can see the organization
        org_ids = [org["id"] for org in organizations]
        assert str(test_organization.id) in org_ids, \
            "New member should see organization in their list"
        
        # Verify new member can access organization details
        org_detail_response = client.get(
            f"/api/v1/organizations/{test_organization.id}",
            headers=invitee_headers
        )
        
        assert org_detail_response.status_code == 200
        org_details = org_detail_response.json()
        assert org_details["id"] == str(test_organization.id)
        assert org_details["name"] == test_organization.name
    
    def test_member_invitation_flow_with_member_role(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        member_role: Role,
        db: Session
    ):
        """
        Test invitation flow with MEMBER role (basic role).
        
        Requirements: FR2.1, FR2.4
        
        Verifies that invitation flow works correctly with basic member role.
        """
        # Invite member with MEMBER role
        invitee_email = "basicmember@example.com"
        
        invite_payload = {
            "invitee_email": invitee_email,
            "role_id": str(member_role.id),
            "message": "Join as a basic member"
        }
        
        invite_response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=invite_payload,
            headers=auth_headers
        )
        
        assert invite_response.status_code == 201
        invitation_id = invite_response.json()["id"]
        
        # Create invitee user
        from app.core.security import get_password_hash
        invitee_user = User(
            email=invitee_email,
            password_hash=get_password_hash("MemberPass123!"),
            first_name="Basic",
            last_name="Member",
            phone="+919876543211",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee_user)
        db.commit()
        db.refresh(invitee_user)
        
        # Login as invitee
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee_email,
                "password": "MemberPass123!",
                "remember_me": False
            }
        )
        
        assert login_response.status_code == 200
        invitee_token = login_response.json()["tokens"]["access_token"]
        invitee_headers = {"Authorization": f"Bearer {invitee_token}"}
        
        # Accept invitation
        accept_response = client.post(
            f"/api/v1/invitations/{invitation_id}/accept",
            headers=invitee_headers
        )
        
        assert accept_response.status_code == 200
        
        # Verify membership and role
        member = db.query(OrgMember).filter(
            OrgMember.user_id == invitee_user.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        member_role_assignment = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == invitee_user.id,
            OrgMemberRole.organization_id == test_organization.id,
            OrgMemberRole.role_id == member_role.id
        ).first()
        
        assert member_role_assignment is not None
        assert member_role_assignment.is_primary is True
        
        # Verify role is MEMBER
        role = db.query(Role).filter(Role.id == member_role_assignment.role_id).first()
        assert role.code == 'MEMBER'
    
    def test_member_invitation_flow_minimal_data(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """
        Test invitation flow with minimal required data (no message).
        
        Requirements: FR2.1, FR2.4
        
        Verifies that invitation flow works with only required fields.
        """
        # Invite member with minimal data
        invitee_email = "minimal@example.com"
        
        invite_payload = {
            "invitee_email": invitee_email,
            "role_id": str(admin_role.id)
            # No message, no custom expiry
        }
        
        invite_response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=invite_payload,
            headers=auth_headers
        )
        
        assert invite_response.status_code == 201
        invite_data = invite_response.json()
        
        assert invite_data["message"] is None
        invitation_id = invite_data["id"]
        
        # Verify invitation in database
        invitation = db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        assert invitation is not None
        assert invitation.message is None
        assert invitation.status == InvitationStatus.PENDING
        
        # Create invitee user and accept
        from app.core.security import get_password_hash
        invitee_user = User(
            email=invitee_email,
            password_hash=get_password_hash("MinimalPass123!"),
            first_name="Minimal",
            last_name="User",
            phone="+919876543212",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee_user)
        db.commit()
        db.refresh(invitee_user)
        
        # Login and accept
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee_email,
                "password": "MinimalPass123!",
                "remember_me": False
            }
        )
        
        assert login_response.status_code == 200
        invitee_token = login_response.json()["tokens"]["access_token"]
        invitee_headers = {"Authorization": f"Bearer {invitee_token}"}
        
        accept_response = client.post(
            f"/api/v1/invitations/{invitation_id}/accept",
            headers=invitee_headers
        )
        
        assert accept_response.status_code == 200
        
        # Verify membership created
        member = db.query(OrgMember).filter(
            OrgMember.user_id == invitee_user.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        # Verify role assigned
        member_role_assignment = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == invitee_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).first()
        
        assert member_role_assignment is not None
        assert member_role_assignment.role_id == admin_role.id
        assert member_role_assignment.is_primary is True
    
    def test_invitation_flow_verifies_all_database_relationships(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """
        Test that invitation flow properly establishes all database relationships.
        
        Requirements: FR2.1, FR2.4
        
        Verifies:
        - Invitation links to organization, inviter, role
        - Membership links to user, organization, invitation
        - Role assignment links to user, organization, role
        - All foreign key relationships are valid
        """
        # Create invitation
        invitee_email = "relationships@example.com"
        
        invite_payload = {
            "invitee_email": invitee_email,
            "role_id": str(admin_role.id),
            "message": "Testing relationships"
        }
        
        invite_response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=invite_payload,
            headers=auth_headers
        )
        
        assert invite_response.status_code == 201
        invitation_id = invite_response.json()["id"]
        
        # Verify invitation relationships
        invitation = db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.id == invitation_id
        ).first()
        
        assert invitation.organization_id == test_organization.id
        assert invitation.inviter_id == test_user.id
        assert invitation.role_id == admin_role.id
        
        # Verify foreign key relationships are valid
        assert invitation.organization is not None
        assert invitation.inviter is not None
        assert invitation.role is not None
        
        # Create invitee and accept
        from app.core.security import get_password_hash
        invitee_user = User(
            email=invitee_email,
            password_hash=get_password_hash("RelPass123!"),
            first_name="Rel",
            last_name="Test",
            phone="+919876543213",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(invitee_user)
        db.commit()
        db.refresh(invitee_user)
        
        # Login and accept
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": invitee_email,
                "password": "RelPass123!",
                "remember_me": False
            }
        )
        
        assert login_response.status_code == 200
        invitee_token = login_response.json()["tokens"]["access_token"]
        invitee_headers = {"Authorization": f"Bearer {invitee_token}"}
        
        accept_response = client.post(
            f"/api/v1/invitations/{invitation_id}/accept",
            headers=invitee_headers
        )
        
        assert accept_response.status_code == 200
        
        # Verify membership relationships
        member = db.query(OrgMember).filter(
            OrgMember.user_id == invitee_user.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        
        assert member is not None
        assert member.user_id == invitee_user.id
        assert member.organization_id == test_organization.id
        assert member.invited_by == test_user.id
        assert member.invitation_id == invitation.id
        
        # Verify foreign key relationships are valid
        assert member.user is not None
        assert member.organization is not None
        
        # Verify role assignment relationships
        member_role_assignment = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == invitee_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).first()
        
        assert member_role_assignment is not None
        assert member_role_assignment.user_id == invitee_user.id
        assert member_role_assignment.organization_id == test_organization.id
        assert member_role_assignment.role_id == admin_role.id
        assert member_role_assignment.assigned_by == test_user.id
        
        # Verify foreign key relationships are valid
        assert member_role_assignment.user is not None
        assert member_role_assignment.organization is not None
        assert member_role_assignment.role is not None
        
        # Verify invitation updated with invitee_user_id
        db.refresh(invitation)
        assert invitation.invitee_user_id == invitee_user.id
