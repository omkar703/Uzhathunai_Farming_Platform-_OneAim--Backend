"""
Crops API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.enums import CropLifecycle
from app.schemas.crop import (
    CropCreate,
    CropUpdate,
    CropResponse,
    UpdateLifecycleRequest
)
from app.services.crop_service import CropService

router = APIRouter()


@router.post("/", response_model=CropResponse, status_code=201)
def create_crop(
    data: CropCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new crop.
    
    Requires:
    - Plot ID
    - Crop name
    - Crop type and variety
    - Optional: area, plant count, planned date
    
    Initial lifecycle state is PLANNED.
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return service.create_crop(data.plot_id, membership.organization_id, data, current_user.id)


@router.get("/", response_model=dict)
def get_crops(
    plot_id: Optional[UUID] = Query(None, description="Filter by plot ID"),
    lifecycle: Optional[CropLifecycle] = Query(None, description="Filter by lifecycle stage"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get crops with pagination and filtering.
    
    - **plot_id**: Optional filter by plot UUID
    - **lifecycle**: Optional filter by lifecycle stage
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    
    Returns paginated list of crops with metadata.
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    # Build filters
    filters = {}
    if plot_id:
        filters['plot_id'] = plot_id
    if lifecycle:
        filters['lifecycle'] = lifecycle
    
    crops, total = service.get_crops(membership.organization_id, filters, page, limit)
    
    return {
        "items": crops,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(
    crop_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific crop by ID.
    
    - **crop_id**: UUID of the crop
    
    Returns crop details with lifecycle information.
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return service.get_crop_by_id(crop_id, membership.organization_id)


@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: UUID,
    data: CropUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a crop.
    
    - **crop_id**: UUID of the crop
    
    Note: Use PUT /{crop_id}/lifecycle to update lifecycle stage.
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return service.update_crop(crop_id, membership.organization_id, data, current_user.id)


@router.delete("/{crop_id}", status_code=204)
def delete_crop(
    crop_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a crop.
    
    - **crop_id**: UUID of the crop
    
    Permanently deletes the crop and associated data.
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    service.delete_crop(crop_id, membership.organization_id, current_user.id)
    return None


# ============================================================================
# Crop Lifecycle Endpoints
# ============================================================================

@router.put("/{crop_id}/lifecycle", response_model=CropResponse)
def update_crop_lifecycle(
    crop_id: UUID,
    data: UpdateLifecycleRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update crop lifecycle stage.
    
    - **crop_id**: UUID of the crop
    - **new_lifecycle**: New lifecycle stage
    
    Valid transitions:
    - PLANNED → PLANTED, TERMINATED
    - PLANTED → TRANSPLANTED, PRODUCTION, TERMINATED
    - TRANSPLANTED → PRODUCTION, TERMINATED
    - PRODUCTION → COMPLETED, TERMINATED
    - COMPLETED → CLOSED
    - TERMINATED → CLOSED
    - CLOSED → (terminal state, no transitions)
    
    Automatically updates corresponding date field (e.g., planted_date when moving to PLANTED).
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return service.update_lifecycle(crop_id, membership.organization_id, data.new_lifecycle, current_user.id)


@router.get("/plots/{plot_id}/crop-history", response_model=List[CropResponse])
def get_crop_history(
    plot_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get crop history for a specific plot.
    
    - **plot_id**: UUID of the plot
    
    Returns all crops (past and present) for the plot, ordered by creation date.
    """
    service = CropService(db)
    
    # Get user's current organization
    from app.models.organization import OrgMember
    from app.models.enums import MemberStatus
    
    membership = db.query(OrgMember).filter(
        OrgMember.user_id == current_user.id,
        OrgMember.status == MemberStatus.ACTIVE
    ).first()
    
    if not membership:
        from app.core.exceptions import PermissionError
        raise PermissionError(
            message="User is not a member of any organization",
            error_code="NO_ORGANIZATION_MEMBERSHIP"
        )
    
    return service.get_crop_history(plot_id, membership.organization_id)
