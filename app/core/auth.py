"""
Authentication dependencies for Uzhathunai v2.0.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
# Import custom exceptions
from app.core.exceptions import unauthorized_exception, PermissionError, AuthenticationError
from app.models.user import User
from app.services.auth_service import AuthService

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
    
    Returns:
        User object with current_organization_id attached
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise unauthorized_exception(
            message="Invalid or expired token",
            error_code="INVALID_TOKEN"
        )
    
    # Get user ID from payload
    user_id: str = payload.get("sub")
    if not user_id:
        raise unauthorized_exception(
            message="Invalid token payload",
            error_code="INVALID_TOKEN_PAYLOAD"
        )
    
    # Query user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise unauthorized_exception(
            message="User not found",
            error_code="USER_NOT_FOUND"
        )
    
    # Extract organization context from token and attach to user object
    org_context = payload.get("org")
    if org_context and org_context.get("id"):
        # Attach organization ID to user object for easy access in endpoints
        user.current_organization_id = org_context.get("id")
    else:
        # No organization context (freelancer or old token)
        user.current_organization_id = None
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User object
    
    Raises:
        AuthenticationError: If user is not active
        PermissionError: If organization is not approved
    """
    if not current_user.is_active:
        raise AuthenticationError(
            message="User account is inactive",
            error_code="INACTIVE_USER"
        )

    # Function to check organization status
    # We import here to avoid circular imports
    from app.services.auth_service import AuthService
    
    # Real implementation of Organization Approval Check
    # Super admins bypass the organization approval check
    from app.models.rbac import Role
    from app.models.organization import OrgMemberRole
    
    is_super_admin = (
        db.query(OrgMemberRole)
        .join(Role)
        .filter(OrgMemberRole.user_id == current_user.id)
        .filter(Role.code == "SUPER_ADMIN")
        .first() is not None
    )
    
    if is_super_admin:
        return current_user
        
    # Lazy load or query memberships
    # Since we injected DB session, we can query.
    from app.models.organization import OrgMember, Organization, MemberStatus
    from app.models.enums import OrganizationStatus
    
    # Check if user has ANY active membership in an ACTIVE or IN_PROGRESS organization
    stmt = (
        db.query(OrgMember)
        .join(Organization)
        .filter(OrgMember.user_id == current_user.id)
        .filter(OrgMember.status == MemberStatus.ACTIVE)
        .filter(Organization.status.in_([OrganizationStatus.ACTIVE, OrganizationStatus.IN_PROGRESS]))
    )
    approved_membership = stmt.first()
    
    # Let's see if they are in a truly unapproved Org (NOT_STARTED)
    stmt_unapproved = (
        db.query(OrgMember)
        .join(Organization)
        .filter(OrgMember.user_id == current_user.id)
        .filter(OrgMember.status == MemberStatus.ACTIVE)
        .filter(Organization.status == OrganizationStatus.NOT_STARTED)
    )
    unapproved_membership = stmt_unapproved.first()
    
    if unapproved_membership and not approved_membership:
        # User is part of an unapproved org and NOT part of any approved org.
        # Block access.
        raise PermissionError(
            message="Your organization is awaiting approval.",
            error_code="ORG_NOT_APPROVED"
        )
        
    return current_user


# Optional: Get current user without raising exception
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.
    Useful for endpoints that work with or without authentication.
    
    Args:
        credentials: HTTP Authorization credentials (optional)
        db: Database session
    
    Returns:
        User object or None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def require_non_freelancer(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Require user to NOT be a freelancer.
    
    Use this dependency for endpoints that require organization membership.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User object
    
    Raises:
        PermissionError: If user is a freelancer
    """
    auth_service = AuthService(db)
    
    if auth_service.is_freelancer(current_user.id):
        raise PermissionError(
            message="This feature requires organization membership. Please create or join an organization.",
            error_code="FREELANCER_NOT_ALLOWED",
            details={"user_id": str(current_user.id)}
        )
    
    return current_user


def get_current_freelancer(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user and verify they are a freelancer.
    
    Use this dependency for freelancer-only endpoints.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User object
    
    Raises:
        PermissionError: If user is not a freelancer
    """
    auth_service = AuthService(db)
    
    
    if not auth_service.is_freelancer(current_user.id):
        raise PermissionError(
            message="This feature is only available to freelancers",
            error_code="NOT_A_FREELANCER",
            details={"user_id": str(current_user.id)}
        )
    
    return current_user


def get_current_super_admin(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user and verify they are a Super Admin.
    
    This verifies the user has the 'SUPER_ADMIN' role in the default organization (or system-wide).
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User object
    
    Raises:
        PermissionError: If user is not a Super Admin
    """
    from sqlalchemy import select
    from app.models.rbac import Role
    from app.models.organization import OrgMemberRole
    
    # Check if ANY OrgMemberRole for this user maps to a 'SUPER_ADMIN' role.
    has_super_admin_role = (
        db.query(OrgMemberRole)
        .join(Role)
        .filter(OrgMemberRole.user_id == current_user.id)
        .filter(Role.code == "SUPER_ADMIN")
        .first()
    )
    
    if not has_super_admin_role:
        raise PermissionError(
            message="Super Admin privileges required",
            error_code="SUPER_ADMIN_REQUIRED" # This matches the test expectation
        )
        
    return current_user
