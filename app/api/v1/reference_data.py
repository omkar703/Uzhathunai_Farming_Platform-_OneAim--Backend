"""
Reference Data API endpoints for Uzhathunai v2.0.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.reference_data import (
    ReferenceDataTypeResponse,
    ReferenceDataResponse
)
from app.services.reference_data_service import ReferenceDataService

router = APIRouter()


@router.get("/types", response_model=List[ReferenceDataTypeResponse])
def get_reference_data_types(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all reference data types.
    
    Returns list of reference data types (e.g., soil_types, water_sources, irrigation_modes).
    """
    service = ReferenceDataService(db)
    return service.get_reference_types()


@router.get("/{type_code}", response_model=List[ReferenceDataResponse])
def get_reference_data_by_type(
    type_code: str,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get reference data values for a specific type.
    
    - **type_code**: Code of the reference data type (e.g., 'soil_types', 'water_sources')
    - **language**: Language code for translations (default: en)
    
    Returns list of reference data values with translations and metadata.
    """
    service = ReferenceDataService(db)
    return service.get_reference_data_by_type(type_code, language)
