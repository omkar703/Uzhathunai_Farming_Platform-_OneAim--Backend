"""
Farms API endpoints for Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.farm import (
    FarmCreate,
    FarmUpdate,
    FarmResponse,
    FarmWaterSourceAdd,
    FarmSoilTypeAdd,
    FarmIrrigationModeAdd
)
from app.services.farm_service import FarmService

router = APIRouter()


@router.post("/", response_model=FarmResponse, status_code=201)
def create_farm(
    data: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new farm.
    
    Requires:
    - User must be a member of an organization
    - Farm name and location coordinates
    - Optional: boundary polygon, area, manager, supervisors
    
    GIS validation:
    - Location coordinates must be valid (lat: -90 to 90, lon: -180 to 180)
    - Boundary polygon must be closed (first point == last point)
    - Boundary must have at least 4 points
    """
    service = FarmService(db)
    
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
    
    return service.create_farm(data, membership.organization_id, current_user.id)


@router.get("/", response_model=dict)
def get_farms(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get farms for the current user's organization with pagination.
    
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    
    Returns paginated list of farms with metadata.
    """
    service = FarmService(db)
    
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
    
    farms, total = service.get_farms(membership.organization_id, page, limit)
    
    return {
        "items": farms,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific farm by ID.
    
    - **farm_id**: UUID of the farm
    
    Returns farm details with location, boundary, and associated resources.
    """
    service = FarmService(db)
    
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
    
    return service.get_farm_by_id(farm_id, membership.organization_id)


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: UUID,
    data: FarmUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a farm.
    
    - **farm_id**: UUID of the farm
    
    GIS validation applies if updating location or boundary.
    """
    service = FarmService(db)
    
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
    
    return service.update_farm(farm_id, data, membership.organization_id, current_user.id)


@router.delete("/{farm_id}", status_code=204)
def delete_farm(
    farm_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a farm (soft delete).
    
    - **farm_id**: UUID of the farm
    
    Sets is_active to false. Farm data is retained for historical purposes.
    """
    service = FarmService(db)
    
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
    
    service.delete_farm(farm_id, membership.organization_id, current_user.id)
    return None


# ============================================================================
# Farm Supervisor Endpoints
# ============================================================================

@router.post("/{farm_id}/supervisors", status_code=201)
def assign_supervisor(
    farm_id: UUID,
    supervisor_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Assign a supervisor to a farm.
    
    - **farm_id**: UUID of the farm
    - **supervisor_id**: UUID of the user to assign as supervisor
    
    Supervisor must be a member of the same organization.
    """
    service = FarmService(db)
    
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
    
    service.assign_supervisor(farm_id, supervisor_id, membership.organization_id, current_user.id)
    return {"message": "Supervisor assigned successfully"}


@router.delete("/{farm_id}/supervisors/{supervisor_id}", status_code=204)
def remove_supervisor(
    farm_id: UUID,
    supervisor_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove a supervisor from a farm.
    
    - **farm_id**: UUID of the farm
    - **supervisor_id**: UUID of the supervisor to remove
    """
    service = FarmService(db)
    
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
    
    service.remove_supervisor(farm_id, supervisor_id, membership.organization_id)
    return None


# ============================================================================
# Farm Resource Association Endpoints
# ============================================================================

@router.post("/{farm_id}/water-sources", status_code=201)
def add_water_source(
    farm_id: UUID,
    data: FarmWaterSourceAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate a water source with a farm.
    
    - **farm_id**: UUID of the farm
    - **water_source_id**: UUID of the water source reference data (in request body)
    """
    service = FarmService(db)
    
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
    
    service.add_water_source(farm_id, data.water_source_id, membership.organization_id)
    return {"message": "Water source added successfully"}


@router.post("/{farm_id}/soil-types", status_code=201)
def add_soil_type(
    farm_id: UUID,
    data: FarmSoilTypeAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate a soil type with a farm.
    
    - **farm_id**: UUID of the farm
    - **soil_type_id**: UUID of the soil type reference data (in request body)
    """
    service = FarmService(db)
    
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
    
    service.add_soil_type(farm_id, data.soil_type_id, membership.organization_id)
    return {"message": "Soil type added successfully"}


@router.post("/{farm_id}/irrigation-modes", status_code=201)
def add_irrigation_mode(
    farm_id: UUID,
    data: FarmIrrigationModeAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate an irrigation mode with a farm.
    
    - **farm_id**: UUID of the farm
    - **irrigation_mode_id**: UUID of the irrigation mode reference data (in request body)
    """
    service = FarmService(db)
    
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
    
    service.add_irrigation_mode(farm_id, data.irrigation_mode_id, membership.organization_id)
    return {"message": "Irrigation mode added successfully"}
