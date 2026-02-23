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
from app.schemas.response import BaseResponse
from app.services.farm_service import FarmService

from app.core.organization_context import get_organization_id, validate_organization_type
from app.models.enums import OrganizationType

router = APIRouter()


@router.post("/", response_model=BaseResponse[FarmResponse], status_code=201)
def create_farm(
    data: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new farm.
    """
    service = FarmService(db)
    
    # 1. Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # 2. Validation
    validate_organization_type(org_id, OrganizationType.FARMING, db)
    
    farm = service.create_farm(data, org_id, current_user.id)
    return {
        "success": True,
        "message": "Farm created successfully",
        "data": farm
    }


@router.get("/", response_model=BaseResponse[dict])
def get_farms(
    is_active: bool = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):

    """
    Get farms for the current user's organization with pagination.
    """
    service = FarmService(db)
    
    # 1. Get organization ID from context with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # 2. Validation
    validate_organization_type(org_id, OrganizationType.FARMING, db)
    
    farms, total = service.get_farms(org_id, is_active, page, limit)

    
    return {
        "success": True,
        "message": "Farms retrieved successfully",
        "data": {
            "items": farms,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/{farm_id}", response_model=BaseResponse[FarmResponse])
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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    farm = service.get_farm_by_id(farm_id, org_id)
    return {
        "success": True,
        "message": "Farm retrieved successfully",
        "data": farm
    }


@router.put("/{farm_id}", response_model=BaseResponse[FarmResponse])
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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    farm = service.update_farm(farm_id, data, org_id, current_user.id)
    return {
        "success": True,
        "message": "Farm updated successfully",
        "data": farm
    }


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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.delete_farm(farm_id, org_id, current_user.id)
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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.assign_supervisor(farm_id, supervisor_id, org_id, current_user.id)
    return {
        "success": True,
        "message": "Supervisor assigned successfully",
        "data": None
    }


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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.remove_supervisor(farm_id, supervisor_id, org_id)
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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.add_water_source(farm_id, data.water_source_id, org_id)
    return {
        "success": True,
        "message": "Water source added successfully",
        "data": None
    }


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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.add_soil_type(farm_id, data.soil_type_id, org_id)
    return {
        "success": True,
        "message": "Soil type added successfully",
        "data": None
    }


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
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.add_irrigation_mode(farm_id, data.irrigation_mode_id, org_id)
    return {
        "success": True,
        "message": "Irrigation mode added successfully",
        "data": None
    }
