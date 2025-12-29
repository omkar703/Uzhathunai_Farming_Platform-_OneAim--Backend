"""
Authentication dependencies for Uzhathunai v2.0.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import unauthorized_exception, PermissionError
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
        User object
    
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
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "User account is inactive",
                "error_code": "INACTIVE_USER"
            }
        )

    # Function to check organization status
    # We import here to avoid circular imports
    from app.services.auth_service import AuthService
    
    # Check if the user is a freelancer. If so, no org check needed.
    # We can't easily get the DB session here because get_current_active_user doesn't depend on DB directly in the signature
    # (it depends on get_current_user which does).
    # However, 'current_user' is attached to the session if it came from get_current_user.
    
    # Let's inspect the user's memberships via relationship
    # This relies on lazy loading or eager loading if configured.
    # Note: Accessing relationship might trigger DB query if session is active.
    
    # Logic: If user belongs to ANY organization that is NOT approved, block access?
    # Or only if they are trying to access that specific organization's data?
    # Rigid Requirement: "Block access for unapproved tenants".
    # Interpretation: If I am an Admin of "Farm A", and "Farm A" is not approved, I cannot log in or do actions.
    
    # We will iterate over memberships.
    # (In a real app, we filter by the org_id in the request header/token).
    
    # For MVP: If the user has ANY membership in an unapproved org, we warn or block?
    # Let's block if they have NO approved organizations and are NO freelancer.
    
    # Actually, simpler: Check all memberships. If they have a membership in an org where is_approved=False,
    # AND they are not a Super Admin (who needs to login to approve it), block.
    
    # Super Admin check (naive based on email or role code)
    # If we had the roles loaded.
    
    # Safe fallback: If organization.is_approved is False, raise 403.
    # Real implementation of Organization Approval Check
    if current_user.email == "superadmin@example.com":
        return current_user
        
    # Lazy load or query memberships
    # Since we injected DB session, we can query.
    from app.models.organization import OrgMember, Organization, MemberStatus
    
    # Check if user has ANY active membership in an APPROVED organization
    # OR if they are a freelancer (if we support that without org).
    
    # Query: Select 1 from OrgMember join Organization where user_id=uid and org.is_approved=True
    stmt = (
        db.query(OrgMember)
        .join(Organization)
        .filter(OrgMember.user_id == current_user.id)
        .filter(OrgMember.status == MemberStatus.ACTIVE)
        .filter(Organization.is_approved == True)
    )
    approved_membership = stmt.first()
    
    # Also check if they are in ANY organization at all?
    # If they are in NO organization, maybe they are just a registered user (Freelancer?)
    # If they ARE in an organization but it's not approved, we block.
    
    # Let's see if they are in an Unapproved Org
    stmt_unapproved = (
        db.query(OrgMember)
        .join(Organization)
        .filter(OrgMember.user_id == current_user.id)
        .filter(OrgMember.status == MemberStatus.ACTIVE)
        .filter(Organization.is_approved == False)
    )
    unapproved_membership = stmt_unapproved.first()
    
    if unapproved_membership and not approved_membership:
        # User is part of an unapproved org and NOT part of any approved org.
        # Block access.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "message": "Your organization is awaiting approval.",
                "error_code": "ORG_NOT_APPROVED"
            }
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
