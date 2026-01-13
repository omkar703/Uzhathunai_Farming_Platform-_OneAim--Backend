"""
Audit permission checking utilities for Farm Audit Management System.
Provides decorators and helper functions for RBAC enforcement.
"""
from functools import wraps
from typing import Callable
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.exceptions import PermissionError
from app.services.rbac_service import RBACService
from app.models.user import User


class AuditPermissions:
    """Audit permission constants."""
    
    # Template Management (Requirement 18.1)
    TEMPLATE_MANAGE = ("audit_template", "manage")
    TEMPLATE_CREATE = ("audit_template", "create")
    TEMPLATE_READ = ("audit_template", "read")
    TEMPLATE_UPDATE = ("audit_template", "update")
    TEMPLATE_DELETE = ("audit_template", "delete")
    TEMPLATE_COPY = ("audit_template", "copy")
    
    # Audit Creation (Requirement 18.2)
    AUDIT_CREATE = ("audit", "create")
    
    # Audit Response (Requirement 18.3)
    AUDIT_RESPONSE = ("audit", "response")
    AUDIT_RESPONSE_CREATE = ("audit", "response_create")
    AUDIT_RESPONSE_UPDATE = ("audit", "response_update")
    AUDIT_PHOTO_UPLOAD = ("audit", "photo_upload")
    
    # Audit Review (Requirement 18.4)
    AUDIT_REVIEW = ("audit", "review")
    AUDIT_REVIEW_CREATE = ("audit", "review_create")
    AUDIT_REVIEW_UPDATE = ("audit", "review_update")
    AUDIT_ISSUE_CREATE = ("audit", "issue_create")
    AUDIT_RECOMMENDATION_CREATE = ("audit", "recommendation_create")
    
    # Audit Finalization (Requirement 18.5)
    AUDIT_FINALIZE = ("audit", "finalize")
    
    # Audit Sharing (Requirement 18.6)
    AUDIT_SHARE = ("audit", "share")
    
    # Audit Recommendation Approval (Requirement 18.7)
    AUDIT_RECOMMENDATION_APPROVE = ("audit", "recommendation_approve")
    
    # Audit Read Access
    AUDIT_READ = ("audit", "read")
    AUDIT_REPORT_GENERATE = ("audit", "report_generate")


def check_audit_permission(
    db: Session,
    user: User,
    organization_id: UUID,
    resource: str,
    action: str
) -> None:
    """
    Check if user has audit permission in organization.
    Raises PermissionError if user lacks permission.
    
    Args:
        db: Database session
        user: Current user
        organization_id: Organization ID
        resource: Resource name (e.g., "audit_template", "audit")
        action: Action name (e.g., "create", "update", "delete")
    
    Raises:
        PermissionError: If user lacks permission
    """
    rbac_service = RBACService(db)
    
    has_permission = rbac_service.check_permission(
        user_id=user.id,
        organization_id=organization_id,
        resource=resource,
        action=action
    )
    
    if not has_permission:
        raise PermissionError(
            message=f"Insufficient permissions for {resource}.{action}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={
                "user_id": str(user.id),
                "organization_id": str(organization_id),
                "resource": resource,
                "action": action
            }
        )


def require_audit_permission(resource: str, action: str):
    """
    Decorator to require audit permission for service methods.
    
    Usage:
        @require_audit_permission("audit_template", "create")
        def create_template(self, data, user, organization_id):
            ...
    
    Args:
        resource: Resource name
        action: Action name
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Extract user and organization_id from kwargs
            user = kwargs.get('user')
            organization_id = kwargs.get('organization_id')
            
            if not user:
                raise ValueError("User must be provided in kwargs")
            if not organization_id:
                raise ValueError("Organization ID must be provided in kwargs")
            
            # Check permission
            check_audit_permission(
                db=self.db,
                user=user,
                organization_id=organization_id,
                resource=resource,
                action=action
            )
            
            # Call original function
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator


def get_user_organization_id(db: Session, user: User) -> UUID:
    """
    Get user's primary organization ID.
    
    Args:
        db: Database session
        user: Current user
    
    Returns:
        Organization ID
    
    Raises:
        PermissionError: If user has no organization
    """
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    # Get user's first active organization
    member = db.query(OrgMember).filter(
        OrgMember.user_id == user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not member:
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP",
            details={"user_id": str(user.id)}
        )
    
    return member.organization_id


def check_system_user(user: User) -> bool:
    """
    Check if user is a system user (SUPER_ADMIN).
    
    Args:
        user: Current user
    
    Returns:
        True if user is system user, False otherwise
    """
    # System users are identified by having SUPER_ADMIN role
    # This is a simplified check - in production, you might want to check
    # the user's roles more thoroughly
    return user.is_superuser if hasattr(user, 'is_superuser') else False


def validate_organization_access(
    db: Session,
    user: User,
    organization_id: UUID
) -> None:
    """
    Validate that user has access to organization.
    
    Args:
        db: Database session
        user: Current user
        organization_id: Organization ID to validate
    
    Raises:
        PermissionError: If user doesn't have access to organization
    """
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    # Check if user is member of organization
    member = db.query(OrgMember).filter(
        OrgMember.user_id == user.id,
        OrgMember.organization_id == organization_id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not member:
        raise PermissionError(
            message="User does not have access to this organization",
            error_code="ORGANIZATION_ACCESS_DENIED",
            details={
                "user_id": str(user.id),
                "organization_id": str(organization_id)
            }
        )
