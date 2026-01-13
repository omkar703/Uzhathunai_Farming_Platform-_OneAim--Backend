"""
Measurement Units API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.enums import MeasurementUnitCategory
from app.schemas.measurement_unit import (
    MeasurementUnitResponse,
    ConvertQuantityRequest,
    ConvertQuantityResponse
)
from app.services.measurement_unit_service import MeasurementUnitService

router = APIRouter()


@router.get("/", response_model=List[MeasurementUnitResponse])
def get_measurement_units(
    category: Optional[MeasurementUnitCategory] = Query(None, description="Filter by category"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get measurement units, optionally filtered by category.
    
    - **category**: Optional filter by category (AREA, VOLUME, WEIGHT, LENGTH, COUNT)
    - **language**: Language code for translations (default: en)
    
    Returns list of measurement units with translations.
    """
    service = MeasurementUnitService(db)
    
    if category:
        return service.get_units_by_category(category, language)
    else:
        # Get all units across all categories
        all_units = []
        for cat in MeasurementUnitCategory:
            units = service.get_units_by_category(cat, language)
            all_units.extend(units)
        return all_units


@router.get("/{unit_id}", response_model=MeasurementUnitResponse)
def get_measurement_unit(
    unit_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific measurement unit by ID.
    
    - **unit_id**: UUID of the measurement unit
    - **language**: Language code for translations (default: en)
    
    Returns measurement unit details with translation.
    """
    service = MeasurementUnitService(db)
    return service.get_unit_by_id(unit_id, language)


@router.post("/convert", response_model=ConvertQuantityResponse)
def convert_quantity(
    request: ConvertQuantityRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Convert a quantity from one measurement unit to another.
    
    - **from_unit_id**: Source measurement unit UUID
    - **to_unit_id**: Target measurement unit UUID
    - **value**: Quantity value to convert
    
    Returns converted value with unit details.
    
    **Note**: Both units must be in the same category (e.g., both AREA units).
    """
    service = MeasurementUnitService(db)
    converted_value = service.convert_quantity(
        request.value,
        request.from_unit_id,
        request.to_unit_id
    )
    
    # Get unit details for response
    from_unit = service.get_unit_by_id(request.from_unit_id, "en")
    to_unit = service.get_unit_by_id(request.to_unit_id, "en")
    
    return ConvertQuantityResponse(
        original_value=request.value,
        converted_value=converted_value,
        from_unit=from_unit,
        to_unit=to_unit
    )
