"""
Plots API endpoints for Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.plot import (
    PlotCreate,
    PlotUpdate,
    PlotResponse,
    PlotWaterSourceAdd,
    PlotSoilTypeAdd,
    PlotIrrigationModeAdd
)
from app.schemas.response import BaseResponse
from app.services.plot_service import PlotService

from app.core.organization_context import get_organization_id
from app.models.enums import OrganizationType

router = APIRouter()


@router.post("/farms/{farm_id}/plots", response_model=BaseResponse[PlotResponse], status_code=201)
def create_plot(
    farm_id: UUID,
    data: PlotCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new plot within a farm.
    
    Requires:
    - Plot name
    - Optional: boundary polygon, area
    
    GIS validation:
    - Plot boundary must be within farm boundary
    - Boundary polygon must be closed (first point == last point)
    - Boundary must have at least 4 points
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    plot = service.create_plot(farm_id, data, org_id, current_user.id)
    return {
        "success": True,
        "message": "Plot created successfully",
        "data": plot
    }


@router.get("/farms/{farm_id}/plots", response_model=BaseResponse[dict])
def get_plots_by_farm(
    farm_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get plots for a specific farm with pagination.
    
    - **farm_id**: UUID of the farm
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    plots, total = service.get_plots_by_farm(farm_id, org_id, page, limit)
    
    return {
        "success": True,
        "message": "Plots retrieved successfully",
        "data": {
            "items": plots,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }


@router.get("/{plot_id}", response_model=BaseResponse[PlotResponse])
def get_plot(
    plot_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific plot by ID.
    
    - **plot_id**: UUID of the plot
    
    Returns plot details with boundary and associated resources.
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    plot = service.get_plot_by_id(plot_id, org_id)
    return {
        "success": True,
        "message": "Plot retrieved successfully",
        "data": plot
    }


@router.put("/{plot_id}", response_model=BaseResponse[PlotResponse])
def update_plot(
    plot_id: UUID,
    data: PlotUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a plot.
    
    - **plot_id**: UUID of the plot
    
    GIS validation applies if updating boundary.
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    plot = service.update_plot(plot_id, data, org_id, current_user.id)
    return {
        "success": True,
        "message": "Plot updated successfully",
        "data": plot
    }


@router.delete("/{plot_id}", status_code=204)
def delete_plot(
    plot_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a plot (soft delete).
    
    - **plot_id**: UUID of the plot
    
    Sets is_active to false. Plot data is retained for historical purposes.
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.delete_plot(plot_id, org_id, current_user.id)
    return None


# ============================================================================
# Plot Resource Association Endpoints
# ============================================================================

@router.post("/{plot_id}/water-sources", status_code=201)
def add_water_source(
    plot_id: UUID,
    data: PlotWaterSourceAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate a water source with a plot.
    
    - **plot_id**: UUID of the plot
    - **water_source_id**: UUID of the water source reference data (in request body)
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.add_water_source(plot_id, data.water_source_id, org_id)
    return {
        "success": True,
        "message": "Water source added successfully",
        "data": None
    }


@router.post("/{plot_id}/soil-types", status_code=201)
def add_soil_type(
    plot_id: UUID,
    data: PlotSoilTypeAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate a soil type with a plot.
    
    - **plot_id**: UUID of the plot
    - **soil_type_id**: UUID of the soil type reference data (in request body)
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.add_soil_type(plot_id, data.soil_type_id, org_id)
    return {
        "success": True,
        "message": "Soil type added successfully",
        "data": None
    }


@router.post("/{plot_id}/irrigation-modes", status_code=201)
def add_irrigation_mode(
    plot_id: UUID,
    data: PlotIrrigationModeAdd,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Associate an irrigation mode with a plot.
    
    - **plot_id**: UUID of the plot
    - **irrigation_mode_id**: UUID of the irrigation mode reference data (in request body)
    """
    service = PlotService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.add_irrigation_mode(plot_id, data.irrigation_mode_id, org_id)
    return {
        "success": True,
        "message": "Irrigation mode added successfully",
        "data": None
    }
