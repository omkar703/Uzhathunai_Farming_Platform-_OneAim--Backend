"""
Integration tests for Member API endpoints.

Tests cover:
- POST /api/v1/organizations/{org_id}/members/invite
- PUT /api/v1/organizations/{org_id}/members/{user_id}/roles (multiple roles)
- DELETE /api/v1/organizations/{org_id}/members/{user_id}
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
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
def supervisor_role(db: Session) -> Role:
    """Get or create SUPERVISOR role for FARMING organizations."""
    role = db.query(Role).filter(Role.code == 'SUPERVISOR').first()
    if not role:
        role = Role(
            code='SUPERVISOR',
            name='Supervisor',
            display_name='Supervisor',
            scope=UserRoleScope.ORGANIZATION,
            description='Organization supervisor',
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


class TestInviteMember:
    """Tests for POST /api/v1/organizations/{org_id}/members/invite."""
    
    def test_invite_member_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        db: Session
    ):
        """Test successful member invitation."""
        payload = {
            "invitee_email": "newmember@example.com",
            "role_id": str(admin_role.id),
            "message": "Welcome to our organization!",
            "expires_in_days": 7
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        assert data["invitee_email"] == "newmember@example.com"
        assert data["role_id"] == str(admin_role.id)
        assert data["status"] == "PENDING"
        assert data["message"] == "Welcome to our organization!"
        assert data["organization_id"] == str(test_organization.id)
        assert data["inviter_id"] == str(test_user.id)
        assert "id" in data
        assert "invited_at" in data
        assert "expires_at" in data
        
        # Verify invitation created in database
        invitation = db.query(OrgMemberInvitation).filter(
            OrgMemberInvitation.invitee_email == "newmember@example.com",
            OrgMemberInvitation.organization_id == test_organization.id
        ).first()
        assert invitation is not None
        assert invitation.status == InvitationStatus.PENDING
    
    def test_invite_member_minimal_data(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        member_role: Role
    ):
        """Test member invitation with minimal required data."""
        payload = {
            "invitee_email": "minimal@example.com",
            "role_id": str(member_role.id)
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        
        assert data["invitee_email"] == "minimal@example.com"
        assert data["role_id"] == str(member_role.id)
        assert data["status"] == "PENDING"
        assert data["message"] is None
    
    def test_invite_member_invalid_email(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        member_role: Role
    ):
        """Test invitation with invalid email format."""
        payload = {
            "invitee_email": "invalid-email",
            "role_id": str(member_role.id)
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
    
    def test_invite_member_duplicate_pending_invitation(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        member_role: Role,
        db: Session
    ):
        """Test that duplicate pending invitations are rejected."""
        payload = {
            "invitee_email": "duplicate@example.com",
            "role_id": str(member_role.id)
        }
        
        # Create first invitation
        response1 = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=payload,
            headers=auth_headers
        )
        assert response1.status_code == 201
        
        # Try to create second invitation with same email
        response2 = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with conflict error
        assert response2.status_code == 409
    
    def test_invite_member_unauthorized(
        self,
        client: TestClient,
        test_organization: Organization,
        member_role: Role
    ):
        """Test that unauthorized requests are rejected."""
        payload = {
            "invitee_email": "unauthorized@example.com",
            "role_id": str(member_role.id)
        }
        
        response = client.post(
            f"/api/v1/organizations/{test_organization.id}/members/invite",
            json=payload
        )
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]
    
    def test_invite_member_non_existent_organization(
        self,
        client: TestClient,
        auth_headers: dict,
        member_role: Role
    ):
        """Test invitation to non-existent organization."""
        fake_org_id = uuid4()
        payload = {
            "invitee_email": "test@example.com",
            "role_id": str(member_role.id)
        }
        
        response = client.post(
            f"/api/v1/organizations/{fake_org_id}/members/invite",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with not found or forbidden error
        assert response.status_code in [403, 404]


class TestUpdateMemberRoles:
    """Tests for PUT /api/v1/organizations/{org_id}/members/{user_id}/roles."""
    
    def test_update_member_roles_single_role(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        member_role: Role,
        db: Session
    ):
        """Test updating member to single role."""
        # Create a member with MEMBER role
        from app.core.security import get_password_hash
        new_user = User(
            email="member@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Member",
            last_name="User",
            phone="+919999999999",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create membership
        member = OrgMember(
            user_id=new_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign MEMBER role
        member_role_assignment = OrgMemberRole(
            user_id=new_user.id,
            organization_id=test_organization.id,
            role_id=member_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(member_role_assignment)
        db.commit()
        
        # Update to ADMIN role
        payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True
                }
            ],
            "reason": "Promotion to admin"
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{new_user.id}/roles",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == str(new_user.id)
        assert data["organization_id"] == str(test_organization.id)
        assert len(data["roles"]) == 1
        assert data["roles"][0]["role_id"] == str(admin_role.id)
        assert data["roles"][0]["is_primary"] is True
        
        # Verify in database
        roles = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == new_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).all()
        assert len(roles) == 1
        assert roles[0].role_id == admin_role.id
        assert roles[0].is_primary is True
    
    def test_update_member_roles_multiple_roles(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        member_role: Role,
        db: Session
    ):
        """Test updating member to multiple roles with primary designation."""
        # Create a member with MEMBER role
        from app.core.security import get_password_hash
        new_user = User(
            email="multirole@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Multi",
            last_name="Role",
            phone="+919888888888",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create membership
        member = OrgMember(
            user_id=new_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign MEMBER role
        member_role_assignment = OrgMemberRole(
            user_id=new_user.id,
            organization_id=test_organization.id,
            role_id=member_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(member_role_assignment)
        db.commit()
        
        # Update to multiple roles (ADMIN primary, SUPERVISOR secondary)
        payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": False
                }
            ],
            "reason": "Assigned multiple responsibilities"
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{new_user.id}/roles",
            json=payload,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == str(new_user.id)
        assert len(data["roles"]) == 2
        
        # Verify primary role
        primary_roles = [r for r in data["roles"] if r["is_primary"]]
        assert len(primary_roles) == 1
        assert primary_roles[0]["role_id"] == str(admin_role.id)
        
        # Verify secondary role
        secondary_roles = [r for r in data["roles"] if not r["is_primary"]]
        assert len(secondary_roles) == 1
        assert secondary_roles[0]["role_id"] == str(supervisor_role.id)
        
        # Verify in database
        roles = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == new_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).all()
        assert len(roles) == 2
        
        # Verify exactly one primary role
        primary_count = sum(1 for r in roles if r.is_primary)
        assert primary_count == 1
    
    def test_update_member_roles_no_primary_role_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        member_role: Role,
        db: Session
    ):
        """Test that updating roles without primary designation fails."""
        # Create a member
        from app.core.security import get_password_hash
        new_user = User(
            email="noprimary@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="No",
            last_name="Primary",
            phone="+919777777777",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create membership
        member = OrgMember(
            user_id=new_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign MEMBER role
        member_role_assignment = OrgMemberRole(
            user_id=new_user.id,
            organization_id=test_organization.id,
            role_id=member_role.id,
            is_primary=True,
            assigned_by=test_organization.created_by
        )
        db.add(member_role_assignment)
        db.commit()
        
        # Try to update with no primary role
        payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": False
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": False
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{new_user.id}/roles",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
    
    def test_update_member_roles_multiple_primary_roles_fails(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        member_role: Role,
        db: Session
    ):
        """Test that updating roles with multiple primary designations fails."""
        # Create a member
        from app.core.security import get_password_hash
        new_user = User(
            email="multiprimary@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Multi",
            last_name="Primary",
            phone="+919666666666",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create membership
        member = OrgMember(
            user_id=new_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign MEMBER role
        member_role_assignment = OrgMemberRole(
            user_id=new_user.id,
            organization_id=test_organization.id,
            role_id=member_role.id,
            is_primary=True,
            assigned_by=test_organization.created_by
        )
        db.add(member_role_assignment)
        db.commit()
        
        # Try to update with multiple primary roles
        payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": True
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{new_user.id}/roles",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422
    
    def test_update_member_roles_unauthorized(
        self,
        client: TestClient,
        test_organization: Organization,
        admin_role: Role
    ):
        """Test that unauthorized requests are rejected."""
        fake_user_id = uuid4()
        payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{fake_user_id}/roles",
            json=payload
        )
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]
    
    def test_update_member_roles_non_existent_member(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        admin_role: Role
    ):
        """Test updating roles for non-existent member."""
        fake_user_id = uuid4()
        payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True
                }
            ]
        }
        
        response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{fake_user_id}/roles",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with not found or forbidden error
        assert response.status_code in [403, 404]


class TestRemoveMember:
    """Tests for DELETE /api/v1/organizations/{org_id}/members/{user_id}."""
    
    def test_remove_member_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        member_role: Role,
        db: Session
    ):
        """Test successful member removal."""
        # Create a member to remove
        from app.core.security import get_password_hash
        new_user = User(
            email="toremove@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="To",
            last_name="Remove",
            phone="+919555555555",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create membership
        member = OrgMember(
            user_id=new_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign MEMBER role
        member_role_assignment = OrgMemberRole(
            user_id=new_user.id,
            organization_id=test_organization.id,
            role_id=member_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(member_role_assignment)
        db.commit()
        
        # Remove member
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/members/{new_user.id}?reason=No+longer+needed",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 204
        
        # Verify member removed from database
        member_check = db.query(OrgMember).filter(
            OrgMember.user_id == new_user.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        assert member_check is None
        
        # Verify roles removed
        roles_check = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == new_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).all()
        assert len(roles_check) == 0
    
    def test_remove_member_without_reason(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        member_role: Role,
        db: Session
    ):
        """Test member removal without reason."""
        # Create a member to remove
        from app.core.security import get_password_hash
        new_user = User(
            email="noreason@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="No",
            last_name="Reason",
            phone="+919444444444",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create membership
        member = OrgMember(
            user_id=new_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign MEMBER role
        member_role_assignment = OrgMemberRole(
            user_id=new_user.id,
            organization_id=test_organization.id,
            role_id=member_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(member_role_assignment)
        db.commit()
        
        # Remove member without reason
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/members/{new_user.id}",
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code == 204
        
        # Verify member removed
        member_check = db.query(OrgMember).filter(
            OrgMember.user_id == new_user.id,
            OrgMember.organization_id == test_organization.id
        ).first()
        assert member_check is None
    
    def test_remove_member_unauthorized(
        self,
        client: TestClient,
        test_organization: Organization
    ):
        """Test that unauthorized requests are rejected."""
        fake_user_id = uuid4()
        
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/members/{fake_user_id}"
        )
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]
    
    def test_remove_member_non_existent_member(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization
    ):
        """Test removing non-existent member."""
        fake_user_id = uuid4()
        
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/members/{fake_user_id}",
            headers=auth_headers
        )
        
        # Should fail with not found or forbidden error
        assert response.status_code in [403, 404]
    
    def test_remove_member_cannot_remove_self(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization
    ):
        """Test that user cannot remove themselves."""
        response = client.delete(
            f"/api/v1/organizations/{test_organization.id}/members/{test_user.id}",
            headers=auth_headers
        )
        
        # Should fail with validation error (422) since it's a business rule validation
        assert response.status_code == 422
        data = response.json()
        assert "cannot remove yourself" in str(data).lower()
