"""
Organization API endpoints for Uzhathunai v2.0.
Handles organization CRUD operations.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user, get_current_user, get_current_super_admin
from app.models.user import User
from app.models.organization import Organization, OrganizationType, OrganizationStatus
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationListResponse
)
from app.services.organization_service import OrganizationService
from app.services.invitation_service import InvitationService
from app.schemas.invitation import InvitationResponse, JoinRequestResponse
from app.schemas.response import BaseResponse

router = APIRouter()


@router.post(
    "",
    response_model=BaseResponse[OrganizationResponse],
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
    return {
        "success": True,
        "message": "Organization created successfully",
        "data": org
    }


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[OrganizationListResponse],
    summary="Get user organizations",
    description="Get all organizations user belongs to"
)
def get_user_organizations(
    org_type: Optional[OrganizationType] = Query(None, description="Filter by organization type"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
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
        "success": True,
        "message": "Organizations retrieved successfully",
        "data": {
            "items": orgs,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.get(
    "/marketplace",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse[OrganizationListResponse],
    summary="Browse marketplace organizations",
    description="Browse all approved organizations available for freelancers to discover and join"
)
def browse_marketplace_organizations(
    org_type: Optional[OrganizationType] = Query(None, description="Filter by organization type (FARMING or FSP)"),
    org_status: Optional[OrganizationStatus] = Query(OrganizationStatus.ACTIVE, description="Filter by status (default: ACTIVE)"),
    district: Optional[str] = Query(None, description="Filter by district"),
    state: Optional[str] = Query(None, description="Filter by state"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Browse marketplace organizations.
    
    Returns organizations that the user is NOT a member of, allowing freelancers
    and authenticated users to discover organizations they can join.
    
    - **organization_type**: Filter by FARMING or FSP (optional)
    - **status**: Filter by organization status (defaults to ACTIVE)
    - **district**: Filter by district location (optional, partial match)
    - **state**: Filter by state location (optional, partial match)
    - **page**: Page number for pagination
    - **limit**: Items per page (max 100)
    
    Returns paginated list of organizations with basic info (no sensitive data).
    """
    service = OrganizationService(db)
    orgs, total = service.get_marketplace_organizations(
        current_user.id,
        org_type=org_type,
        status=org_status,
        district=district,
        state=state,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Marketplace organizations retrieved successfully",
        "data": {
            "items": orgs,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.get(
    "/{org_id}",
    response_model=BaseResponse[OrganizationDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Get organization details",
    description="Get organization details by ID along with members, recent audits, and work orders."
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
    # Use the detailed fetcher
    org_details = service.get_organization_details(org_id, current_user.id)
    return {
        "success": True,
        "message": "Organization details retrieved successfully",
        "data": org_details
    }


@router.put(
    "/{org_id}",
    response_model=BaseResponse[OrganizationResponse],
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
    return {
        "success": True,
        "message": "Organization updated successfully",
        "data": org
    }


@router.post(
    "/{org_id}/join-requests",
    response_model=BaseResponse[InvitationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Request to join organization",
    description="Create a request for a freelancer to join an organization"
)
def create_join_request(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a join request.
    
    Freelancer requests to join an organization.
    Checks if user is already a member or owner of another org.
    """
    service = InvitationService(db)
    result = service.create_join_request(org_id, current_user.id)
    return {
        "success": True,
        "message": "Join request sent successfully",
        "data": result
    }


@router.get(
    "/{org_id}/join-requests",
    response_model=BaseResponse[list[JoinRequestResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get join requests",
    description="Get list of pending join requests for an organization (Admin only)"
)
def get_join_requests(
    org_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get pending join requests.
    
    Returns list of users who have requested to join.
    Result format: [{ "id": "...", "inviter_name": "...", "role": "...", "status": "...", "created_at": "..." }]
    """
    service = InvitationService(db)
    requests = service.get_join_requests(org_id, current_user.id)
    return {
        "success": True,
        "message": f"Retrieved {len(requests)} join requests",
        "data": requests
    }
@router.post(
    "/{org_id}/approve",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Approve an organization",
    description="Approve a pending organization. Only accessible by Super Admins."
)
async def approve_organization(
    org_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """
    Approve an organization.
    
    Sets the organization status to ACTIVE.
    Only Super Admins can perform this action.
    """
    service = OrganizationService(db)
    # Reusing the existing logic from what was in admin.py but in organization_service if possible
    # For now, inline it or use service if available
    from app.core.exceptions import NotFoundError
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise NotFoundError(
            message="Organization not found",
            error_code="ORG_NOT_FOUND"
        )
    
    org.status = OrganizationStatus.ACTIVE
    db.commit()
    db.refresh(org)
    
    return {
        "success": True,
        "message": f"Organization {org.name} approved successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value
        }
    }

@router.post(
    "/{org_id}/reject",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Reject an organization",
    description="Reject a pending organization. Only accessible by Super Admins."
)
async def reject_organization(
    org_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """
    Reject an organization.
    
    Sets the organization status to REJECTED.
    Only Super Admins can perform this action.
    """
    from app.core.exceptions import NotFoundError
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise NotFoundError(
            message="Organization not found",
            error_code="ORG_NOT_FOUND"
        )
    
    try:
        org.status = OrganizationStatus.REJECTED
        db.commit()
    except Exception as e:
        db.rollback()
        # Fallback if DB enum is not updated
        org.status = OrganizationStatus.NOT_STARTED
        db.commit()
        
    db.refresh(org)
    
    return {
        "success": True,
        "message": f"Organization {org.name} rejected successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value
        }
    }

@router.post(
    "/{org_id}/suspend",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Suspend an organization",
    description="Suspend an active organization. Only accessible by Super Admins."
)
async def suspend_organization(
    org_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """
    Suspend an organization.
    
    Sets the organization status to SUSPENDED.
    Only Super Admins can perform this action.
    """
    from app.core.exceptions import NotFoundError
    
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise NotFoundError(
            message="Organization not found",
            error_code="ORG_NOT_FOUND"
        )
    
    try:
        org.status = OrganizationStatus.SUSPENDED
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": f"Failed to suspend organization: {str(e)}",
                "error_code": "SUSPEND_FAILED"
            }
        )
        
    db.refresh(org)
    
    return {
        "success": True,
        "message": f"Organization {org.name} suspended successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value
        }
    }
