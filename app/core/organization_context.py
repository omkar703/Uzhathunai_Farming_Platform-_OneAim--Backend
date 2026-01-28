"""
Helper utilities for extracting organization context from authenticated users.
"""
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import OrgMember, MemberStatus
from app.core.exceptions import PermissionError


from app.models.organization import OrgMember, Organization, MemberStatus
from app.models.enums import OrganizationType
from app.core.exceptions import PermissionError, ValidationError


def get_organization_id(current_user: User, db: Session, expected_type: Optional[OrganizationType] = None) -> UUID:
    """
    Extract organization ID from JWT token context with smart type inference.
    
    Optimized to minimize database roundtrips:
    1. Fetches all active memberships for the user in a single query.
    2. Checks if token org matches expectation.
    3. Performs smart inference without redundant queries if mismatches occur.
    """
    from app.core.logging import get_logger
    debug_logger = get_logger("app.core.org_context_debug")

    # Fetch all active memberships with their organization types in ONE query
    memberships = db.query(Organization.id, Organization.organization_type, Organization.name).join(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).all()
    
    if not memberships:
        raise PermissionError(
            message="This action requires organization membership. Please create or switch to an organization.",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )

    active_id_from_token = None
    if hasattr(current_user, 'current_organization_id') and current_user.current_organization_id:
        active_id_from_token = UUID(current_user.current_organization_id)

    # 1. Check if token organization matches expectation
    if active_id_from_token:
        token_membership = next((m for m in memberships if m.id == active_id_from_token), None)
        if token_membership:
            # If no expectation or type matches, we are good
            if not expected_type or token_membership.organization_type == expected_type:
                return active_id_from_token
            
            # Type mismatch - fallback to smart inference
            # Only log at debug level to avoid cluttering info logs during auto-resolution
            debug_logger.debug(f"Token org {active_id_from_token} ({token_membership.organization_type.value}) doesn't match expected type {expected_type.value}. Attempting smart inference.")

    # 2. Smart Type Inference (from already fetched memberships)
    if expected_type:
        type_memberships = [m for m in memberships if m.organization_type == expected_type]
        
        if len(type_memberships) == 1:
            inferred_id = type_memberships[0].id
            # Log as info only once when inference happens if you want, but keep it concise
            debug_logger.debug(f"Smart inferred organization ID {inferred_id} for type {expected_type.value}", extra={"user_id": str(current_user.id)})
            return inferred_id
        elif len(type_memberships) > 1:
            # Ambiguous - user must choose
            org_names = ", ".join([m.name for m in type_memberships])
            raise PermissionError(
                message=f"Please switch to one of your {expected_type.value} organizations to continue: {org_names}",
                error_code="MULTIPLE_ORGANIZATIONS_OF_TYPE"
            )

    # 3. Final Fallback (Newest membership from the list)
    # Since we can't easily get 'newest' from the query above without ordering the join,
    # we use the first one if we have no better option, or re-query for the absolute newest.
    # But usually, reaching here means the specific type requested wasn't found.
    
    if expected_type:
         raise PermissionError(
            message=f"This feature requires a {expected_type.value} organization membership.",
            error_code="INVALID_ORGANIZATION_TYPE"
        )

    # Fallback to the first available membership if no specific type was requested
    return memberships[0].id


def validate_organization_type(org_id: UUID, expected_type: OrganizationType, db: Session):
    """
    Validate that the organization matches the expected type with helpful error messages.
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise PermissionError(
            message="Organization not found",
            error_code="ORGANIZATION_NOT_FOUND"
        )
        
    if org.organization_type != expected_type:
        raise PermissionError(
            message=f"You are currently active in '{org.name}' ({org.organization_type.value}). This feature requires a {expected_type.value} organization.",
            error_code="INVALID_ORGANIZATION_TYPE",
            details={
                "expected": expected_type.value,
                "current": org.organization_type.value,
                "org_name": org.name
            }
        )
