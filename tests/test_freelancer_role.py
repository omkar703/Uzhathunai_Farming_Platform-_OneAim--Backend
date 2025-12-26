"""
Tests for FREELANCER role assignment and management.
"""
import pytest
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.services.organization_service import OrganizationService
from app.schemas.auth import UserRegister
from app.schemas.organization import OrganizationCreate, FSPServiceCreate
from app.models.enums import OrganizationType
from app.models.rbac import Role
from app.models.organization import OrgMemberRole


class TestFreelancerRole:
    """Test FREELANCER role assignment and transitions."""
    
    def test_register_user_assigns_freelancer_role(self, db_session: Session):
        """Test that new users are assigned FREELANCER role by default."""
        auth_service = AuthService(db_session)
        
        # Register new user
        user_data = UserRegister(
            email="freelancer@test.com",
            password="Test@1234",
            first_name="Test",
            last_name="Freelancer"
        )
        
        user, access_token, refresh_token = auth_service.register_user(user_data)
        
        # Verify user created
        assert user.id is not None
        assert user.email == "freelancer@test.com"
        
        # Verify FREELANCER role assigned
        assert auth_service.is_freelancer(user.id) is True
        
        # Verify org_member_roles record
        freelancer_role = db_session.query(Role).filter(Role.code == 'FREELANCER').first()
        assert freelancer_role is not None
        
        member_role = db_session.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == user.id,
            OrgMemberRole.organization_id == None,
            OrgMemberRole.role_id == freelancer_role.id
        ).first()
        
        assert member_role is not None
        assert member_role.is_primary is True
    
    def test_get_user_roles_returns_freelancer(self, db_session: Session):
        """Test that get_user_roles returns FREELANCER role."""
        auth_service = AuthService(db_session)
        
        # Register new user
        user_data = UserRegister(
            email="freelancer2@test.com",
            password="Test@1234",
            first_name="Test",
            last_name="Freelancer"
        )
        
        user, _, _ = auth_service.register_user(user_data)
        
        # Get user roles
        roles = auth_service.get_user_roles(user.id)
        
        assert len(roles) == 1
        assert roles[0]["role_code"] == "FREELANCER"
        assert roles[0]["organization_id"] is None
        assert roles[0]["is_freelancer"] is True
        assert roles[0]["is_primary"] is True
    
    def test_create_organization_removes_freelancer_role(self, db_session: Session):
        """Test that creating an organization removes FREELANCER role."""
        auth_service = AuthService(db_session)
        org_service = OrganizationService(db_session)
        
        # Register new user (gets FREELANCER role)
        user_data = UserRegister(
            email="farmer@test.com",
            password="Test@1234",
            first_name="Test",
            last_name="Farmer"
        )
        
        user, _, _ = auth_service.register_user(user_data)
        
        # Verify user is freelancer
        assert auth_service.is_freelancer(user.id) is True
        
        # Create organization
        org_data = OrganizationCreate(
            name="Test Farm",
            organization_type=OrganizationType.FARMING,
            description="Test farm organization"
        )
        
        org = org_service.create_organization(org_data, user.id)
        
        # Verify FREELANCER role removed
        assert auth_service.is_freelancer(user.id) is False
        
        # Verify OWNER role assigned
        roles = auth_service.get_user_roles(user.id)
        assert len(roles) == 1
        assert roles[0]["role_code"] == "OWNER"
        assert roles[0]["organization_id"] == str(org.id)
        assert roles[0]["is_primary"] is True
    
    def test_create_fsp_organization_assigns_fsp_owner(self, db_session: Session):
        """Test that creating FSP organization assigns FSP_OWNER role."""
        auth_service = AuthService(db_session)
        org_service = OrganizationService(db_session)
        
        # Register new user
        user_data = UserRegister(
            email="fsp@test.com",
            password="Test@1234",
            first_name="Test",
            last_name="FSP"
        )
        
        user, _, _ = auth_service.register_user(user_data)
        
        # Create FSP organization
        org_data = OrganizationCreate(
            name="Test FSP",
            organization_type=OrganizationType.FSP,
            description="Test FSP organization"
        )
        
        org = org_service.create_organization(org_data, user.id)
        
        # Verify FREELANCER role removed
        assert auth_service.is_freelancer(user.id) is False
        
        # Verify FSP_OWNER role assigned
        roles = auth_service.get_user_roles(user.id)
        assert len(roles) == 1
        assert roles[0]["role_code"] == "FSP_OWNER"
        assert roles[0]["organization_id"] == str(org.id)
    
    def test_remove_freelancer_role_directly(self, db_session: Session):
        """Test removing FREELANCER role directly."""
        auth_service = AuthService(db_session)
        
        # Register new user
        user_data = UserRegister(
            email="test@test.com",
            password="Test@1234",
            first_name="Test",
            last_name="User"
        )
        
        user, _, _ = auth_service.register_user(user_data)
        
        # Verify user is freelancer
        assert auth_service.is_freelancer(user.id) is True
        
        # Remove FREELANCER role
        auth_service.remove_freelancer_role(user.id)
        db_session.commit()
        
        # Verify FREELANCER role removed
        assert auth_service.is_freelancer(user.id) is False
        
        # Verify no roles
        roles = auth_service.get_user_roles(user.id)
        assert len(roles) == 0
    
    def test_auth_me_endpoint_returns_freelancer_status(self, client, db_session: Session):
        """Test that /auth/me endpoint returns freelancer status."""
        auth_service = AuthService(db_session)
        
        # Register new user
        user_data = UserRegister(
            email="api@test.com",
            password="Test@1234",
            first_name="API",
            last_name="Test"
        )
        
        user, access_token, _ = auth_service.register_user(user_data)
        
        # Call /auth/me endpoint
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert "roles" in data
        assert "is_freelancer" in data
        
        assert data["is_freelancer"] is True
        assert len(data["roles"]) == 1
        assert data["roles"][0]["role_code"] == "FREELANCER"
