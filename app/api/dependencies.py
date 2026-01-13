"""
FastAPI dependency injection functions for organization access control.
"""
from uuid import UUID
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import MemberStatus
from app.core.exceptions import NotFoundError, PermissionError


def get_organization_by_id(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Organization:
    """
    Get organization by ID with access validation.
    Ensures user is a member of the organization.
    
    Args:
        org_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Organization object
        
    Raises:
        NotFoundError: If organization not found
        PermissionError: If user is not a member
    """
    # Get organization
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise NotFoundError(
            message="Organization not found",
            error_code="ORGANIZATION_NOT_FOUND",
            details={"org_id": str(org_id)}
        )
    
    # Check if user is a member
    member = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.organization_id == org_id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not member:
        raise PermissionError(
            message="Access denied to organization",
            error_code="NOT_A_MEMBER",
            details={"org_id": str(org_id)}
        )
    
    return org


def require_org_admin(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Require user to be organization admin (OWNER/ADMIN role).
    
    Args:
        org_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Current user (if admin)
        
    Raises:
        PermissionError: If user is not a member or not an admin
    """
    # Get user's roles in organization
    member_roles = db.query(OrgMemberRole).join(Role).filter(
        OrgMemberRole.user_id == current_user.id,
        OrgMemberRole.organization_id == org_id
    ).all()
    
    if not member_roles:
        raise PermissionError(
            message="Not a member of organization",
            error_code="NOT_A_MEMBER",
            details={"org_id": str(org_id)}
        )
    
    # Check if user has OWNER or ADMIN role
    admin_roles = ['OWNER', 'ADMIN', 'FSP_OWNER', 'FSP_ADMIN']
    has_admin = any(mr.role.code in admin_roles for mr in member_roles)
    
    if not has_admin:
        raise PermissionError(
            message="Organization admin access required",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"org_id": str(org_id), "required_roles": admin_roles}
        )
    
    return current_user


def require_org_owner(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Require user to be organization owner (OWNER/FSP_OWNER role).
    
    Args:
        org_id: Organization UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Current user (if owner)
        
    Raises:
        PermissionError: If user is not a member or not an owner
    """
    # Get user's roles in organization
    member_roles = db.query(OrgMemberRole).join(Role).filter(
        OrgMemberRole.user_id == current_user.id,
        OrgMemberRole.organization_id == org_id
    ).all()
    
    if not member_roles:
        raise PermissionError(
            message="Not a member of organization",
            error_code="NOT_A_MEMBER",
            details={"org_id": str(org_id)}
        )
    
    # Check if user has OWNER role
    owner_roles = ['OWNER', 'FSP_OWNER']
    has_owner = any(mr.role.code in owner_roles for mr in member_roles)
    
    if not has_owner:
        raise PermissionError(
            message="Organization owner access required",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"org_id": str(org_id), "required_roles": owner_roles}
        )
    
    return current_user
