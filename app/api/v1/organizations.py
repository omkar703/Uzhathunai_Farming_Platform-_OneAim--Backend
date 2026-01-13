"""
Organization API endpoints for Uzhathunai v2.0.
Handles organization CRUD operations.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import OrganizationType
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse
)
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create organization",
    description="Create a new organization (FARMING or FSP type)"
)
def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new organization.
    
    - **name**: Organization name (required, 1-200 chars)
    - **organization_type**: FARMING or FSP (required)
    - **description**: Organization description (optional)
    - **district**: District location (optional)
    - **pincode**: Postal code (optional)
    - **services**: FSP services (required for FSP type)
    
    Creator automatically becomes OWNER (FARMING) or FSP_OWNER (FSP).
    """
    service = OrganizationService(db)
    org = service.create_organization(data, current_user.id)
    return org


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Get user organizations",
    description="Get all organizations user belongs to"
)
def get_user_organizations(
    org_type: Optional[OrganizationType] = Query(None, description="Filter by organization type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all organizations user belongs to.
    
    Supports filtering by organization type and pagination.
    Returns paginated results with metadata.
    """
    service = OrganizationService(db)
    orgs, total = service.get_user_organizations(
        current_user.id,
        org_type=org_type,
        page=page,
        limit=limit
    )
    
    return {
        "items": orgs,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 0
    }


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get organization details",
    description="Get organization details by ID"
)
def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get organization details.
    
    User must be a member of the organization.
    """
    service = OrganizationService(db)
    org = service.get_organization(org_id, current_user.id)
    return org


@router.put(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update organization",
    description="Update organization details"
)
def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update organization details.
    
    Only OWNER/ADMIN can update organization.
    
    - **name**: Organization name (optional)
    - **description**: Organization description (optional)
    - **district**: District location (optional)
    - **pincode**: Postal code (optional)
    - **contact_email**: Contact email (optional)
    - **contact_phone**: Contact phone (optional)
    """
    service = OrganizationService(db)
    org = service.update_organization(org_id, current_user.id, data)
    return org
