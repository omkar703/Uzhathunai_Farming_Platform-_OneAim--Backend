"""
Crop Yields API endpoints for Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.crop import (
    CropYieldCreate,
    CropYieldUpdate,
    CropYieldResponse,
    YieldComparisonResponse
)
from app.schemas.response import BaseResponse
from app.services.crop_yield_service import CropYieldService

from app.core.organization_context import get_organization_id
from app.models.enums import OrganizationType

router = APIRouter()


@router.post("/crops/{crop_id}/yields", response_model=BaseResponse[CropYieldResponse], status_code=201)
def create_crop_yield(
    crop_id: UUID,
    data: CropYieldCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Record a crop yield (planned or actual).
    
    - **crop_id**: UUID of the crop
    - **yield_type**: PLANNED or ACTUAL
    - **quantity**: Yield quantity
    - **quantity_unit_id**: Measurement unit for quantity
    - **harvest_date**: Required for ACTUAL yields
    - **harvest_area**: Optional for area-based yields
    - **harvest_area_unit_id**: Required if harvest_area is provided
    - **notes**: Optional notes
    
    For PLANNED yields: Record expected yield before harvest.
    For ACTUAL yields: Record actual yield after harvest with harvest_date.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    crop_yield = service.create_yield(crop_id, org_id, data, current_user.id)
    return {
        "success": True,
        "message": "Crop yield created successfully",
        "data": crop_yield
    }


@router.get("/crops/{crop_id}/yields", response_model=BaseResponse[list[CropYieldResponse]])
def get_crop_yields(
    crop_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all yields for a specific crop.
    
    - **crop_id**: UUID of the crop
    
    Returns list of yields (both planned and actual) with associated photos.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    yields = service.get_yields_by_crop(crop_id, org_id)
    return {
        "success": True,
        "message": "Crop yields retrieved successfully",
        "data": yields
    }


@router.get("/{yield_id}", response_model=BaseResponse[CropYieldResponse])
def get_crop_yield(
    yield_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific yield by ID.
    
    - **yield_id**: UUID of the yield
    
    Returns yield details with associated photos.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    crop_yield = service.get_yield_by_id(yield_id, org_id)
    return {
        "success": True,
        "message": "Crop yield retrieved successfully",
        "data": crop_yield
    }


@router.put("/{yield_id}", response_model=BaseResponse[CropYieldResponse])
def update_crop_yield(
    yield_id: UUID,
    data: CropYieldUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a crop yield.
    
    - **yield_id**: UUID of the yield
    
    Can update quantity, harvest date, notes, etc.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    crop_yield = service.update_yield(yield_id, org_id, data, current_user.id)
    return {
        "success": True,
        "message": "Crop yield updated successfully",
        "data": crop_yield
    }


@router.delete("/{yield_id}", status_code=204)
def delete_crop_yield(
    yield_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a crop yield.
    
    - **yield_id**: UUID of the yield
    
    Permanently deletes the yield record.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.delete_yield(yield_id, org_id, current_user.id)
    return None


# ============================================================================
# Yield Photo Association Endpoints
# ============================================================================

@router.post("/{yield_id}/photos", status_code=201)
def associate_photo_with_yield(
    yield_id: UUID,
    photo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate a crop photo with a yield record.
    
    - **yield_id**: UUID of the yield
    - **photo_id**: UUID of the crop lifecycle photo
    
    Links an existing crop photo to this yield record.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.associate_photo(yield_id, photo_id, org_id)
    return {
        "success": True,
        "message": "Photo associated with yield successfully",
        "data": None
    }


# ============================================================================
# Yield Comparison Endpoints
# ============================================================================

@router.get("/crops/{crop_id}/yield-comparison", response_model=BaseResponse[YieldComparisonResponse])
def get_yield_comparison(
    crop_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compare planned vs actual yields for a crop.
    
    - **crop_id**: UUID of the crop
    
    Returns:
    - Total planned yield
    - Total actual yield
    - Variance (actual - planned)
    - Variance percentage
    - Achievement rate (actual / planned * 100)
    
    Useful for analyzing crop performance and planning future crops.
    """
    service = CropYieldService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    comparison = service.compare_planned_vs_actual(crop_id, org_id)
    return {
        "success": True,
        "message": "Yield comparison retrieved successfully",
        "data": comparison
    }
