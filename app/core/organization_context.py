"""
Helper utilities for extracting organization context from authenticated users.
"""
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import OrgMember, MemberStatus
from app.core.exceptions import PermissionError


def get_organization_id(current_user: User, db: Session) -> UUID:
    """
    Extract organization ID from JWT token context or fallback to first active membership.
    
    Args:
        current_user: Authenticated user (with current_organization_id attached from JWT)
        db: Database session
    
    Returns:
        Organization UUID
    
    Raises:
        PermissionError: If user has no organization membership
    """
    # Try to get organization from JWT token context
    if hasattr(current_user, 'current_organization_id') and current_user.current_organization_id:
        return UUID(current_user.current_organization_id)
    
    # Fallback to first active membership (backward compatibility)
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return membership.organization_id
