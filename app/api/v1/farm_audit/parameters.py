"""
Parameters API endpoints for Farm Audit Management in Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.parameter import ParameterType
from app.schemas.parameter import (
    ParameterCreate,
    ParameterUpdate,
    ParameterCopy,
    ParameterResponse,
    ParameterDetailResponse
)
from app.services.parameter_service import ParameterService

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
# Parameter Endpoints
# ============================================================================

@router.get("", response_model=List[ParameterResponse])
def get_parameters(
    parameter_type: Optional[ParameterType] = Query(None, description="Filter by parameter type"),
    include_system: bool = Query(True, description="Include system-defined parameters"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get parameters for the current user's organization.
    
    - **parameter_type**: Filter by parameter type (TEXT, NUMERIC, SINGLE_SELECT, MULTI_SELECT, DATE)
    - **include_system**: Include system-defined parameters (default: true)
    - **language**: Language code for translations (default: en)
    
    Returns list of parameters (system and org-specific).
    """
    service = ParameterService(db)
    org_id = get_user_organization_id(current_user, db)
    
    return service.get_parameters(org_id, parameter_type, language, include_system)


@router.get("/{parameter_id}", response_model=ParameterDetailResponse)
def get_parameter(
    parameter_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get parameter by ID with all translations and option sets.
    
    - **parameter_id**: Parameter UUID
    - **language**: Language code for translations (default: en)
    
    Returns parameter with all translations and option set references.
    """
    service = ParameterService(db)
    org_id = get_user_organization_id(current_user, db)
    
    return service.get_parameter(parameter_id, org_id, language)


@router.post("", response_model=ParameterDetailResponse, status_code=201)
def create_parameter(
    data: ParameterCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an organization-specific parameter.
    
    Only organization admins can create parameters.
    System-defined parameters cannot be created through this endpoint.
    
    Parameter types:
    - TEXT: Free text input
    - NUMERIC: Numeric input with optional min/max validation
    - SINGLE_SELECT: Single choice from option set
    - MULTI_SELECT: Multiple choices from option set
    - DATE: Date input
    
    For SINGLE_SELECT and MULTI_SELECT types, option_set_ids must be provided.
    
    Parameter metadata can include:
    - min_value, max_value: For NUMERIC types
    - unit: Unit of measurement
    - decimal_places: Number of decimal places for NUMERIC
    - min_photos, max_photos: Photo requirements
    - validation_rules: Additional validation rules
    """
    service = ParameterService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.create_org_parameter(data, org_id, current_user.id)


@router.put("/{parameter_id}", response_model=ParameterDetailResponse)
def update_parameter(
    parameter_id: UUID,
    data: ParameterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization-specific parameter.
    
    Only organization admins can update parameters.
    System-defined parameters cannot be updated.
    
    You can update:
    - is_active: Activate/deactivate parameter
    - parameter_metadata: Update validation rules and photo requirements
    - translations: Update multilingual content
    - option_set_ids: Update associated option sets (for SELECT types)
    """
    service = ParameterService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.update_org_parameter(parameter_id, data, org_id, current_user.id)


@router.delete("/{parameter_id}", status_code=204)
def delete_parameter(
    parameter_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization-specific parameter.
    
    Only organization admins can delete parameters.
    System-defined parameters cannot be deleted.
    This is a soft delete (sets is_active to false).
    
    Inactive parameters are not available for new templates but existing
    templates using them will continue to work.
    """
    service = ParameterService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.delete_org_parameter(parameter_id, org_id, current_user.id)
    return None


@router.post("/{parameter_id}/copy", response_model=ParameterDetailResponse, status_code=201)
def copy_parameter(
    parameter_id: UUID,
    data: ParameterCopy,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Copy a parameter to create a new one.
    
    Permission rules:
    - System users can copy from any parameter (system or organization)
    - Organization users with consultancy service can copy only from their own organization parameters
    - Regular organization users cannot copy parameters
    
    The copy operation:
    - Creates a deep copy of the parameter with a new code
    - Copies all translations
    - Copies parameter_metadata (validation rules, photo requirements)
    - References the same option sets (does not copy option sets)
    
    Use this to:
    - Create variations of existing parameters
    - Reuse parameter configurations across templates
    - Build organization-specific parameter libraries
    """
    service = ParameterService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.copy_parameter(parameter_id, data, org_id, current_user.id, current_user)
