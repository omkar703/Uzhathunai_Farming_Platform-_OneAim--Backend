"""
Option Sets API endpoints for Farm Audit Management in Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.option_set import (
    OptionSetCreate,
    OptionSetUpdate,
    OptionSetResponse,
    OptionSetDetailResponse,
    OptionCreate,
    OptionUpdate,
    OptionResponse,
    OptionSetListResponse
)
from app.schemas.response import BaseResponse
from app.services.option_set_service import OptionSetService

router = APIRouter()


def get_user_organization_id(user: User, db: Session) -> UUID:
    """
    Helper function to get user's current organization ID.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        Organization ID
        
    Raises:
        PermissionError: If user is not a member of any organization
    """
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    from app.core.exceptions import PermissionError
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return membership.organization_id


# ============================================================================
# Option Set Endpoints
# ============================================================================

@router.get("", response_model=BaseResponse[OptionSetListResponse])
def get_option_sets(
    include_system: bool = Query(True, description="Include system-defined option sets"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get option sets for the current user's organization.
    
    - **include_system**: Include system-defined option sets (default: true)
    - **language**: Language code for translations (default: en)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20)
    
    Returns list of option sets (system and org-specific).
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    items, total = service.get_option_sets(org_id, language, include_system, page, limit)
    
    return {
        "success": True,
        "message": "Option sets retrieved successfully",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.get("/{option_set_id}", response_model=BaseResponse[OptionSetDetailResponse])
def get_option_set(
    option_set_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get option set by ID with all options.
    
    - **option_set_id**: Option set UUID
    - **language**: Language code for translations (default: en)
    
    Returns option set with all options and translations.
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    option_set = service.get_option_set(option_set_id, org_id, language)
    
    return {
        "success": True,
        "message": "Option set retrieved successfully",
        "data": option_set
    }


@router.post("", response_model=BaseResponse[OptionSetDetailResponse], status_code=201)
def create_option_set(
    data: OptionSetCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an organization-specific option set.
    
    Only organization admins can create option sets.
    System-defined option sets cannot be created through this endpoint.
    
    Options can be included in the creation request or added later.
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    option_set = service.create_org_option_set(data, org_id, current_user.id)
    
    return {
        "success": True,
        "message": "Option set created successfully",
        "data": option_set
    }


@router.put("/{option_set_id}", response_model=BaseResponse[OptionSetDetailResponse])
def update_option_set(
    option_set_id: UUID,
    data: OptionSetUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization-specific option set.
    
    Only organization admins can update option sets.
    System-defined option sets cannot be updated.
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    option_set = service.update_org_option_set(option_set_id, data, org_id, current_user.id)
    
    return {
        "success": True,
        "message": "Option set updated successfully",
        "data": option_set
    }


@router.delete("/{option_set_id}", status_code=204)
def delete_option_set(
    option_set_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization-specific option set.
    
    Only organization admins can delete option sets.
    System-defined option sets cannot be deleted.
    This is a soft delete (sets is_active to false).
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.delete_org_option_set(option_set_id, org_id, current_user.id)
    return None


# ============================================================================
# Option Endpoints (within Option Sets)
# ============================================================================

@router.post("/{option_set_id}/options", response_model=BaseResponse[OptionResponse], status_code=201)
def add_option_to_set(
    option_set_id: UUID,
    data: OptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add an option to an option set.
    
    Only organization admins can add options.
    Options cannot be added to system-defined option sets.
    
    Each option must have translations for at least one language.
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    option = service.add_option_to_set(option_set_id, data, org_id, current_user.id)
    
    return {
        "success": True,
        "message": "Option added to set successfully",
        "data": option
    }


@router.put("/{option_set_id}/options/{option_id}", response_model=BaseResponse[OptionResponse])
def update_option(
    option_set_id: UUID,
    option_id: UUID,
    data: OptionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an option in an option set.
    
    Only organization admins can update options.
    Options in system-defined option sets cannot be updated.
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    option = service.update_option(option_id, data, org_id, current_user.id)
    
    return {
        "success": True,
        "message": "Option updated successfully",
        "data": option
    }


@router.delete("/{option_set_id}/options/{option_id}", status_code=204)
def delete_option(
    option_set_id: UUID,
    option_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an option from an option set.
    
    Only organization admins can delete options.
    Options in system-defined option sets cannot be deleted.
    This is a hard delete (removes the option permanently).
    """
    service = OptionSetService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.delete_option(option_id, org_id, current_user.id)
    return None
