"""
Templates API endpoints for Farm Audit Management in Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateDetail,
    TemplateSectionAdd,
    TemplateSectionResponse,
    TemplateParameterAdd,
    TemplateParameterResponse,
    TemplateCopy
)
from app.services.template_service import TemplateService

router = APIRouter()


def get_user_organization_id(user: User, db: Session) -> UUID:
    """
    Helper function to get user's current organization ID.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        Organization ID or None for system users
        
    Raises:
        PermissionError: If user is not a member of any organization
    """
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    from app.core.exceptions import PermissionError
    
    # Check if user is system user (has no organization membership)
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        # Could be a system user - return None
        # TODO: Add proper system user check
        return None
    
    return org_id


def has_consultancy_service(user: User, db: Session) -> bool:
    """
    Check if user's organization has consultancy service.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        True if organization has consultancy service
    """
    from app.models.organization import OrgMember, Organization
    from app.models.subscription import Subscription
    from app.models.fsp_service import MasterService
    from app.models.enums import MemberStatus, SubscriptionStatus
    
    # Get user's organization
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        return False
    
    # Check if organization has active consultancy subscription
    consultancy_service = db.query(MasterService).filter(
        MasterService.service_code == 'CONSULTANCY'
    ).first()
    
    if not consultancy_service:
        return False
    
    subscription = db.query(Subscription).filter(
        Subscription.organization_id == org_id,
        Subscription.master_service_id == consultancy_service.id,
        Subscription.status == SubscriptionStatus.ACTIVE
    ).first()
    
    return subscription is not None


# ============================================================================
# Template Endpoints
# ============================================================================

@router.get("", response_model=dict)
def get_templates(
    crop_type_id: UUID = Query(None, description="Filter by crop type"),
    is_active: bool = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get templates for the current user's organization.
    
    - **crop_type_id**: Filter by crop type (optional)
    - **is_active**: Filter by active status (optional)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    
    Returns paginated list of templates (system and org-specific).
    System users see all templates.
    Organization users see system templates and their own.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    templates, total = service.get_templates(
        organization_id=org_id,
        crop_type_id=crop_type_id,
        is_active=is_active,
        page=page,
        limit=limit
    )
    
    return {
        "items": templates,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get template by ID.
    
    - **template_id**: Template UUID
    
    Returns template with translations.
    """
    service = TemplateService(db)
    return service.get_template(template_id)


@router.post("", response_model=TemplateResponse, status_code=201)
def create_template(
    data: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a template.
    
    System users create system-defined templates.
    Organization users create organization-specific templates.
    
    Templates must have translations for at least one language.
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.create_template(data, current_user.id, org_id)


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a template.
    
    System users can update any template.
    Organization users can only update their own templates.
    System-defined templates cannot be updated by organization users.
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.update_template(template_id, data, current_user.id, org_id)


@router.delete("/{template_id}", status_code=204)
def delete_template(
    template_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a template.
    
    System users can delete any template.
    Organization users can only delete their own templates.
    System-defined templates cannot be deleted by organization users.
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.delete_template(template_id, org_id)
    return None


# ============================================================================
# Template Section Management Endpoints
# ============================================================================

@router.post("/{template_id}/sections", response_model=TemplateSectionResponse, status_code=201)
def add_section_to_template(
    template_id: UUID,
    data: TemplateSectionAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a section to a template.
    
    System users can add sections to any template.
    Organization users can only add sections to their own templates.
    System-defined templates cannot be modified by organization users.
    
    The section must already exist (either system-defined or org-specific).
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.add_section_to_template(template_id, data, org_id)


@router.delete("/{template_id}/sections/{section_id}", status_code=204)
def remove_section_from_template(
    template_id: UUID,
    section_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a section from a template.
    
    System users can remove sections from any template.
    Organization users can only remove sections from their own templates.
    System-defined templates cannot be modified by organization users.
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.remove_section_from_template(template_id, section_id, org_id)
    return None


# ============================================================================
# Template Parameter Management Endpoints
# ============================================================================

@router.post(
    "/{template_id}/sections/{section_id}/parameters",
    response_model=TemplateParameterResponse,
    status_code=201
)
def add_parameter_to_template_section(
    template_id: UUID,
    section_id: UUID,
    data: TemplateParameterAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a parameter to a template section.
    
    System users can add parameters to any template.
    Organization users can only add parameters to their own templates.
    System-defined templates cannot be modified by organization users.
    
    The parameter must already exist (either system-defined or org-specific).
    A parameter snapshot is automatically created at the time of addition.
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.add_parameter_to_template_section(
        template_id,
        section_id,
        data,
        org_id
    )


@router.delete(
    "/{template_id}/sections/{section_id}/parameters/{parameter_id}",
    status_code=204
)
def remove_parameter_from_template_section(
    template_id: UUID,
    section_id: UUID,
    parameter_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a parameter from a template section.
    
    System users can remove parameters from any template.
    Organization users can only remove parameters from their own templates.
    System-defined templates cannot be modified by organization users.
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.remove_parameter_from_template_section(
        template_id,
        section_id,
        parameter_id,
        org_id
    )
    return None


# ============================================================================
# Template Copy Endpoint
# ============================================================================

@router.post("/{template_id}/copy", response_model=TemplateResponse, status_code=201)
def copy_template(
    template_id: UUID,
    data: TemplateCopy,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Copy a template with all its sections and parameters.
    
    Permission rules:
    - System users can copy any template (system or organization)
    - Organization users with consultancy service can copy only their own org templates
    - Regular organization users cannot copy templates
    
    The copy creates:
    - New template with new code and translations
    - New template sections (referencing same section entities)
    - New template parameters (referencing same parameter entities)
    - New parameter snapshots for each parameter
    
    Does NOT copy:
    - Section entities (references existing sections)
    - Parameter entities (references existing parameters)
    - Option sets (references existing option sets)
    
    Requires "Audit Template Management" permission.
    """
    service = TemplateService(db)
    org_id = get_user_organization_id(current_user, db)
    has_consultancy = has_consultancy_service(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.copy_template(
        template_id,
        data,
        current_user.id,
        org_id,
        has_consultancy
    )
