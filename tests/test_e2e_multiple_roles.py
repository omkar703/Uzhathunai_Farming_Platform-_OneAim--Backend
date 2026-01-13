"""
End-to-End test for Multiple Roles Assignment.

Task 12.4: Test multiple roles assignment
- Assign multiple roles to member
- Verify all roles created in org_member_roles
- Verify one role marked as primary
- Test permission union (member has permissions from all roles)

Requirements: FR2.8, FR3.2
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role, Permission, RolePermission
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope,
    PermissionEffect
)
from app.services.rbac_service import RBACService


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
        name="E2E Multiple Roles Test Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        description="Organization for testing multiple roles assignment",
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


@pytest.fixture
def test_member_user(db: Session) -> User:
    """Create a test user to be added as member with multiple roles."""
    from app.core.security import get_password_hash
    
    user = User(
        email="multirole@example.com",
        password_hash=get_password_hash("MultiRole123!"),
        first_name="Multi",
        last_name="Role",
        phone="+919876543220",
        preferred_language="en",
        is_active=True,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def permission_farms_create(db: Session) -> Permission:
    """Get or create farms.create permission."""
    perm = db.query(Permission).filter(
        Permission.resource == 'farms',
        Permission.action == 'create'
    ).first()
    if not perm:
        perm = Permission(
            code='farms.create',
            name='Create Farms',
            resource='farms',
            action='create',
            description='Permission to create farms'
        )
        db.add(perm)
        db.commit()
        db.refresh(perm)
    return perm


@pytest.fixture
def permission_farms_update(db: Session) -> Permission:
    """Get or create farms.update permission."""
    perm = db.query(Permission).filter(
        Permission.resource == 'farms',
        Permission.action == 'update'
    ).first()
    if not perm:
        perm = Permission(
            code='farms.update',
            name='Update Farms',
            resource='farms',
            action='update',
            description='Permission to update farms'
        )
        db.add(perm)
        db.commit()
        db.refresh(perm)
    return perm


@pytest.fixture
def permission_members_manage(db: Session) -> Permission:
    """Get or create members.manage permission."""
    perm = db.query(Permission).filter(
        Permission.resource == 'members',
        Permission.action == 'manage'
    ).first()
    if not perm:
        perm = Permission(
            code='members.manage',
            name='Manage Members',
            resource='members',
            action='manage',
            description='Permission to manage organization members'
        )
        db.add(perm)
        db.commit()
        db.refresh(perm)
    return perm


class TestE2EMultipleRolesAssignment:
    """
    End-to-end test for multiple roles assignment to a member.
    
    This test verifies the complete flow of assigning multiple roles to a member
    and ensuring permission union works correctly.
    """
    
    def test_assign_multiple_roles_to_member_complete_flow(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        permission_farms_create: Permission,
        permission_farms_update: Permission,
        permission_members_manage: Permission,
        db: Session
    ):
        """
        Test complete flow of assigning multiple roles to a member.
        
        Requirements: FR2.8, FR3.2
        
        Steps:
        1. Add member to organization with initial role (ADMIN)
        2. Assign additional role (SUPERVISOR) to member
        3. Verify all roles created in org_member_roles
        4. Verify one role marked as primary
        5. Setup permissions for each role
        6. Test permission union (member has permissions from all roles)
        """
        # Create a unique test member for this test
        from app.core.security import get_password_hash
        test_member_user = User(
            email="multirole1@example.com",
            password_hash=get_password_hash("MultiRole123!"),
            first_name="Multi",
            last_name="Role1",
            phone="+919876543221",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(test_member_user)
        db.commit()
        db.refresh(test_member_user)
        
        # Step 1: Add member to organization with initial role (ADMIN)
        # First, create membership
        member = OrgMember(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE,
            invited_by=test_user.id
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        
        # Assign initial role (ADMIN) as primary
        initial_role_assignment = OrgMemberRole(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            role_id=admin_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(initial_role_assignment)
        db.commit()
        
        # Verify initial role assignment
        roles_count = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == test_member_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).count()
        assert roles_count == 1, "Should have exactly one role initially"
        
        # Step 2: Assign additional role (SUPERVISOR) via API
        update_roles_payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True  # Keep ADMIN as primary
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": False  # SUPERVISOR as secondary
                }
            ],
            "reason": "Adding supervisor responsibilities"
        }
        
        update_response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{test_member_user.id}/roles",
            json=update_roles_payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert update_response.status_code == 200, \
            f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        response_data = update_response.json()
        assert "roles" in response_data
        assert len(response_data["roles"]) == 2, "Should have 2 roles after update"
        
        # Step 3: Verify all roles created in org_member_roles
        member_roles = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == test_member_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).all()
        
        assert len(member_roles) == 2, \
            f"Expected 2 role assignments, found {len(member_roles)}"
        
        # Verify both roles are present
        role_ids = [mr.role_id for mr in member_roles]
        assert admin_role.id in role_ids, "ADMIN role should be assigned"
        assert supervisor_role.id in role_ids, "SUPERVISOR role should be assigned"
        
        # Verify all role assignments have proper attributes
        for member_role in member_roles:
            assert member_role.user_id == test_member_user.id
            assert member_role.organization_id == test_organization.id
            assert member_role.assigned_at is not None
            assert member_role.assigned_by == test_user.id
            assert member_role.created_at is not None
        
        # Step 4: Verify one role marked as primary
        primary_roles = [mr for mr in member_roles if mr.is_primary]
        assert len(primary_roles) == 1, \
            f"Expected exactly 1 primary role, found {len(primary_roles)}"
        
        primary_role = primary_roles[0]
        assert primary_role.role_id == admin_role.id, \
            "ADMIN should be the primary role"
        
        # Verify the other role is not primary
        secondary_roles = [mr for mr in member_roles if not mr.is_primary]
        assert len(secondary_roles) == 1, "Should have exactly 1 secondary role"
        assert secondary_roles[0].role_id == supervisor_role.id, \
            "SUPERVISOR should be the secondary role"
        
        # Step 5: Setup permissions for each role
        # Grant farms.create to ADMIN role
        admin_perm_create = RolePermission(
            role_id=admin_role.id,
            permission_id=permission_farms_create.id,
            effect=PermissionEffect.ALLOW
        )
        db.add(admin_perm_create)
        
        # Grant members.manage to ADMIN role
        admin_perm_members = RolePermission(
            role_id=admin_role.id,
            permission_id=permission_members_manage.id,
            effect=PermissionEffect.ALLOW
        )
        db.add(admin_perm_members)
        
        # Grant farms.update to SUPERVISOR role
        supervisor_perm_update = RolePermission(
            role_id=supervisor_role.id,
            permission_id=permission_farms_update.id,
            effect=PermissionEffect.ALLOW
        )
        db.add(supervisor_perm_update)
        
        db.commit()
        
        # Step 6: Test permission union (member has permissions from all roles)
        rbac_service = RBACService(db)
        
        # Test permission from ADMIN role (farms.create)
        has_farms_create = rbac_service.check_permission(
            test_member_user.id,
            test_organization.id,
            'farms',
            'create'
        )
        assert has_farms_create is True, \
            "Member should have farms.create permission from ADMIN role"
        
        # Test permission from ADMIN role (members.manage)
        has_members_manage = rbac_service.check_permission(
            test_member_user.id,
            test_organization.id,
            'members',
            'manage'
        )
        assert has_members_manage is True, \
            "Member should have members.manage permission from ADMIN role"
        
        # Test permission from SUPERVISOR role (farms.update)
        has_farms_update = rbac_service.check_permission(
            test_member_user.id,
            test_organization.id,
            'farms',
            'update'
        )
        assert has_farms_update is True, \
            "Member should have farms.update permission from SUPERVISOR role"
        
        # Test permission not granted to any role
        has_farms_delete = rbac_service.check_permission(
            test_member_user.id,
            test_organization.id,
            'farms',
            'delete'
        )
        assert has_farms_delete is False, \
            "Member should not have farms.delete permission (not granted to any role)"
        
        # Verify permission union: member has permissions from BOTH roles
        # This is the key test for FR3.2 - union of permissions from multiple roles
        print("\n=== Permission Union Verification ===")
        print(f"Member has {len(member_roles)} roles: ADMIN (primary) and SUPERVISOR")
        print(f"ADMIN role grants: farms.create, members.manage")
        print(f"SUPERVISOR role grants: farms.update")
        print(f"Member effective permissions (union): farms.create, members.manage, farms.update")
        print(f"✓ farms.create: {has_farms_create}")
        print(f"✓ members.manage: {has_members_manage}")
        print(f"✓ farms.update: {has_farms_update}")
        print(f"✗ farms.delete: {has_farms_delete} (not granted)")
    
    def test_assign_three_roles_to_member(
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
        """
        Test assigning three roles to a member.
        
        Requirements: FR2.8
        
        Verifies that a member can have more than two roles and
        exactly one is marked as primary.
        """
        # Create a unique test member for this test
        from app.core.security import get_password_hash
        test_member_user = User(
            email="multirole2@example.com",
            password_hash=get_password_hash("MultiRole123!"),
            first_name="Multi",
            last_name="Role2",
            phone="+919876543222",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(test_member_user)
        db.commit()
        db.refresh(test_member_user)
        
        # Create membership
        member = OrgMember(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE,
            invited_by=test_user.id
        )
        db.add(member)
        db.commit()
        
        # Assign three roles via API
        update_roles_payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": False
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": True  # SUPERVISOR as primary
                },
                {
                    "role_id": str(member_role.id),
                    "is_primary": False
                }
            ],
            "reason": "Assigning multiple responsibilities"
        }
        
        update_response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{test_member_user.id}/roles",
            json=update_roles_payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert update_response.status_code == 200
        response_data = update_response.json()
        assert len(response_data["roles"]) == 3, "Should have 3 roles"
        
        # Verify all three roles in database
        member_roles = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == test_member_user.id,
            OrgMemberRole.organization_id == test_organization.id
        ).all()
        
        assert len(member_roles) == 3, f"Expected 3 roles, found {len(member_roles)}"
        
        # Verify role IDs
        role_ids = [mr.role_id for mr in member_roles]
        assert admin_role.id in role_ids
        assert supervisor_role.id in role_ids
        assert member_role.id in role_ids
        
        # Verify exactly one primary role
        primary_roles = [mr for mr in member_roles if mr.is_primary]
        assert len(primary_roles) == 1, "Should have exactly 1 primary role"
        assert primary_roles[0].role_id == supervisor_role.id, \
            "SUPERVISOR should be the primary role"
        
        # Verify two secondary roles
        secondary_roles = [mr for mr in member_roles if not mr.is_primary]
        assert len(secondary_roles) == 2, "Should have exactly 2 secondary roles"
    
    def test_change_primary_role(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        db: Session
    ):
        """
        Test changing which role is primary.
        
        Requirements: FR2.8
        
        Verifies that primary role can be changed while maintaining
        the constraint of exactly one primary role.
        """
        # Create a unique test member for this test
        from app.core.security import get_password_hash
        test_member_user = User(
            email="multirole3@example.com",
            password_hash=get_password_hash("MultiRole123!"),
            first_name="Multi",
            last_name="Role3",
            phone="+919876543223",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(test_member_user)
        db.commit()
        db.refresh(test_member_user)
        
        # Create membership with two roles
        member = OrgMember(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE,
            invited_by=test_user.id
        )
        db.add(member)
        db.commit()
        
        # Initial assignment: ADMIN as primary
        role1 = OrgMemberRole(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            role_id=admin_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(role1)
        
        role2 = OrgMemberRole(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            role_id=supervisor_role.id,
            is_primary=False,
            assigned_by=test_user.id
        )
        db.add(role2)
        db.commit()
        
        # Verify initial state
        primary_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == test_member_user.id,
            OrgMemberRole.organization_id == test_organization.id,
            OrgMemberRole.is_primary == True
        ).first()
        assert primary_role.role_id == admin_role.id
        
        # Change primary role to SUPERVISOR
        update_roles_payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": False  # No longer primary
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": True  # Now primary
                }
            ],
            "reason": "Changing primary role to supervisor"
        }
        
        update_response = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{test_member_user.id}/roles",
            json=update_roles_payload,
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        
        # Verify primary role changed
        db.expire_all()  # Clear session cache
        
        new_primary_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == test_member_user.id,
            OrgMemberRole.organization_id == test_organization.id,
            OrgMemberRole.is_primary == True
        ).first()
        
        assert new_primary_role is not None
        assert new_primary_role.role_id == supervisor_role.id, \
            "SUPERVISOR should now be the primary role"
        
        # Verify still only one primary role
        primary_count = db.query(OrgMemberRole).filter(
            OrgMemberRole.user_id == test_member_user.id,
            OrgMemberRole.organization_id == test_organization.id,
            OrgMemberRole.is_primary == True
        ).count()
        assert primary_count == 1, "Should still have exactly 1 primary role"
    
    def test_permission_union_with_deny_precedence(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        permission_farms_create: Permission,
        db: Session
    ):
        """
        Test that DENY takes precedence over ALLOW in permission union.
        
        Requirements: FR3.2
        
        Verifies that when a member has multiple roles, if any role
        has DENY for a permission, it takes precedence over ALLOW
        from other roles.
        """
        # Create a unique test member for this test
        from app.core.security import get_password_hash
        test_member_user = User(
            email="multirole4@example.com",
            password_hash=get_password_hash("MultiRole123!"),
            first_name="Multi",
            last_name="Role4",
            phone="+919876543224",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(test_member_user)
        db.commit()
        db.refresh(test_member_user)
        
        # Create membership with two roles
        member = OrgMember(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE,
            invited_by=test_user.id
        )
        db.add(member)
        db.commit()
        
        # Assign both roles
        role1 = OrgMemberRole(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            role_id=admin_role.id,
            is_primary=True,
            assigned_by=test_user.id
        )
        db.add(role1)
        
        role2 = OrgMemberRole(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            role_id=supervisor_role.id,
            is_primary=False,
            assigned_by=test_user.id
        )
        db.add(role2)
        db.commit()
        
        # Grant farms.create to ADMIN role with ALLOW
        admin_perm = RolePermission(
            role_id=admin_role.id,
            permission_id=permission_farms_create.id,
            effect=PermissionEffect.ALLOW
        )
        db.add(admin_perm)
        
        # Grant farms.create to SUPERVISOR role with DENY
        supervisor_perm = RolePermission(
            role_id=supervisor_role.id,
            permission_id=permission_farms_create.id,
            effect=PermissionEffect.DENY
        )
        db.add(supervisor_perm)
        db.commit()
        
        # Test permission - DENY should take precedence
        rbac_service = RBACService(db)
        
        has_permission = rbac_service.check_permission(
            test_member_user.id,
            test_organization.id,
            'farms',
            'create'
        )
        
        assert has_permission is False, \
            "DENY from SUPERVISOR role should take precedence over ALLOW from ADMIN role"
        
        print("\n=== DENY Precedence Verification ===")
        print(f"Member has 2 roles: ADMIN and SUPERVISOR")
        print(f"ADMIN role: ALLOW farms.create")
        print(f"SUPERVISOR role: DENY farms.create")
        print(f"Result: DENY takes precedence")
        print(f"✗ farms.create: {has_permission} (DENY wins)")
    
    def test_validation_requires_exactly_one_primary_role(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        test_organization: Organization,
        admin_role: Role,
        supervisor_role: Role,
        db: Session
    ):
        """
        Test that validation requires exactly one primary role.
        
        Requirements: FR2.8
        
        Verifies that API rejects requests with:
        - No primary role
        - Multiple primary roles
        """
        # Create a unique test member for this test
        from app.core.security import get_password_hash
        test_member_user = User(
            email="multirole5@example.com",
            password_hash=get_password_hash("MultiRole123!"),
            first_name="Multi",
            last_name="Role5",
            phone="+919876543225",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(test_member_user)
        db.commit()
        db.refresh(test_member_user)
        
        # Create membership
        member = OrgMember(
            user_id=test_member_user.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE,
            invited_by=test_user.id
        )
        db.add(member)
        db.commit()
        
        # Test 1: No primary role (should fail)
        no_primary_payload = {
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
        
        response1 = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{test_member_user.id}/roles",
            json=no_primary_payload,
            headers=auth_headers
        )
        
        assert response1.status_code == 422, \
            "Should reject request with no primary role"
        
        # Test 2: Multiple primary roles (should fail)
        multiple_primary_payload = {
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
        
        response2 = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{test_member_user.id}/roles",
            json=multiple_primary_payload,
            headers=auth_headers
        )
        
        assert response2.status_code == 422, \
            "Should reject request with multiple primary roles"
        
        # Test 3: Exactly one primary role (should succeed)
        valid_payload = {
            "roles": [
                {
                    "role_id": str(admin_role.id),
                    "is_primary": True
                },
                {
                    "role_id": str(supervisor_role.id),
                    "is_primary": False
                }
            ]
        }
        
        response3 = client.put(
            f"/api/v1/organizations/{test_organization.id}/members/{test_member_user.id}/roles",
            json=valid_payload,
            headers=auth_headers
        )
        
        assert response3.status_code == 200, \
            "Should accept request with exactly one primary role"
