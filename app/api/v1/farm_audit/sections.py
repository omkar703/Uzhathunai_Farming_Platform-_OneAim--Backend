"""
Sections API endpoints for Farm Audit Management in Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.section import (
    SectionCreate,
    SectionUpdate,
    SectionResponse,
    SectionDetailResponse
)
from app.services.section_service import SectionService

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
    
    return org_id


# ============================================================================
# Section Endpoints
# ============================================================================

@router.get("", response_model=List[SectionResponse])
def get_sections(
    include_system: bool = Query(True, description="Include system-defined sections"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get sections for the current user's organization.
    
    - **include_system**: Include system-defined sections (default: true)
    - **language**: Language code for translations (default: en)
    
    Returns list of sections (system and org-specific).
    """
    service = SectionService(db)
    org_id = get_user_organization_id(current_user, db)
    
    return service.get_sections(org_id, language, include_system)


@router.get("/{section_id}", response_model=SectionDetailResponse)
def get_section(
    section_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get section by ID with all translations.
    
    - **section_id**: Section UUID
    - **language**: Language code for translations (default: en)
    
    Returns section with all translations.
    """
    service = SectionService(db)
    org_id = get_user_organization_id(current_user, db)
    
    return service.get_section(section_id, org_id, language)


@router.post("", response_model=SectionDetailResponse, status_code=201)
def create_section(
    data: SectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an organization-specific section.
    
    Only organization admins can create sections.
    System-defined sections cannot be created through this endpoint.
    
    Sections must have translations for at least one language.
    """
    service = SectionService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.create_org_section(data, org_id, current_user.id)


@router.put("/{section_id}", response_model=SectionDetailResponse)
def update_section(
    section_id: UUID,
    data: SectionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization-specific section.
    
    Only organization admins can update sections.
    System-defined sections cannot be updated.
    """
    service = SectionService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    return service.update_org_section(section_id, data, org_id, current_user.id)


@router.delete("/{section_id}", status_code=204)
def delete_section(
    section_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization-specific section.
    
    Only organization admins can delete sections.
    System-defined sections cannot be deleted.
    This is a soft delete (sets is_active to false).
    """
    service = SectionService(db)
    org_id = get_user_organization_id(current_user, db)
    
    # TODO: Add RBAC check for "Audit Template Management" permission
    
    service.delete_org_section(section_id, org_id, current_user.id)
    return None
