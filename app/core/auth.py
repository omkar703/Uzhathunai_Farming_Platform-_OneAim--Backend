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
    current_user: User = Depends(get_current_user)
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
