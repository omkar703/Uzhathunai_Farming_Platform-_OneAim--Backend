"""
Sections API endpoints for Farm Audit Management in Uzhathunai v2.0.
"""
from typing import List, Optional
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
    SectionDetailResponse,
    SectionListResponse
)
from app.schemas.response import BaseResponse
from app.services.section_service import SectionService

router = APIRouter()


def get_user_organization_id(user: User, db: Session) -> Optional[UUID]:
    """
    Helper function to get user's current organization ID.
    
    Args:
        user: Current user
        db: Database session
        
    Returns:
        Organization ID or None if Super Admin
        
    Raises:
        PermissionError: If user is not a member of any organization
    """
    from app.models.organization import OrgMember
    from app.models.organization import OrgMemberRole
    from app.models.rbac import Role
    from app.models.enums import MemberStatus
    from app.core.exceptions import PermissionError
    
    # Check for Super Admin role first
    is_super_admin = db.query(OrgMemberRole).join(Role).filter(
        OrgMemberRole.user_id == user.id,
        Role.code == "SUPER_ADMIN"
    ).first() is not None
    
    if is_super_admin:
        return None

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
# Section Endpoints
# ============================================================================

@router.get("", response_model=BaseResponse[SectionListResponse])
def get_sections(
    include_system: bool = Query(True, description="Include system-defined sections"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get sections for the current user's organization.
    
    - **include_system**: Include system-defined sections (default: true)
    - **language**: Language code for translations (default: en)
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20)
    
    Returns list of sections (system and org-specific).
    """
    service = SectionService(db)
    org_id = get_user_organization_id(current_user, db)
    
    items, total = service.get_sections(org_id, language, include_system, page, limit)
    
    return {
        "success": True,
        "message": "Sections retrieved successfully",
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.get("/{section_id}", response_model=BaseResponse[SectionDetailResponse])
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
    
    section = service.get_section(section_id, org_id, language)
    
    return {
        "success": True,
        "message": "Section retrieved successfully",
        "data": section
    }


@router.post("", response_model=BaseResponse[SectionDetailResponse], status_code=201)
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
    
    section = service.create_org_section(data, org_id, current_user.id)
    
    return {
        "success": True,
        "message": "Section created successfully",
        "data": section
    }


@router.put("/{section_id}", response_model=BaseResponse[SectionDetailResponse])
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
    
    section = service.update_org_section(section_id, data, org_id, current_user.id)
    
    return {
        "success": True,
        "message": "Section updated successfully",
        "data": section
    }


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
