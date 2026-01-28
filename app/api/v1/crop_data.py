"""
Crop Data API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.crop_data import (
    CropCategoryResponse,
    CropTypeResponse,
    CropVarietyResponse
)
from app.schemas.response import BaseResponse
from app.services.crop_data_service import CropDataService

router = APIRouter()


@router.get("/categories", response_model=BaseResponse[list[CropCategoryResponse]])
def get_crop_categories(
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all crop categories.
    
    - **language**: Language code for translations (default: en)
    
    Returns list of crop categories with translations.
    """
    service = CropDataService(db)
    categories = service.get_crop_categories(language)
    return {
        "success": True,
        "message": "Crop categories retrieved successfully",
        "data": categories
    }


@router.get("/types", response_model=BaseResponse[list[CropTypeResponse]])
def get_crop_types(
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get crop types, optionally filtered by category.
    
    - **category_id**: Optional filter by crop category UUID
    - **language**: Language code for translations (default: en)
    
    Returns list of crop types with translations.
    """
    service = CropDataService(db)
    
    if category_id:
        types = service.get_crop_types_by_category(category_id, language)
    else:
        # Get all types across all categories
        categories = service.get_crop_categories(language)
        types = []
        for category in categories:
            cat_types = service.get_crop_types_by_category(category.id, language)
            types.extend(cat_types)
            
    return {
        "success": True,
        "message": "Crop types retrieved successfully",
        "data": types
    }


@router.get("/varieties", response_model=BaseResponse[list[CropVarietyResponse]])
def get_crop_varieties(
    type_id: Optional[UUID] = Query(None, alias="crop_type_id", description="Filter by type ID"),
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get crop varieties, optionally filtered by type.
    
    - **type_id**: Optional filter by crop type UUID
    - **language**: Language code for translations (default: en)
    
    Returns list of crop varieties with translations and metadata.
    """
    service = CropDataService(db)
    
    if type_id:
        varieties = service.get_crop_varieties_by_type(type_id, language)
    else:
        # Get all varieties across all types
        categories = service.get_crop_categories(language)
        varieties = []
        for category in categories:
            types = service.get_crop_types_by_category(category.id, language)
            for crop_type in types:
                cat_varieties = service.get_crop_varieties_by_type(crop_type.id, language)
                varieties.extend(cat_varieties)
                
    return {
        "success": True,
        "message": "Crop varieties retrieved successfully",
        "data": varieties
    }


@router.get("/varieties/{variety_id}", response_model=BaseResponse[CropVarietyResponse])
def get_crop_variety(
    variety_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific crop variety by ID.
    
    - **variety_id**: UUID of the crop variety
    - **language**: Language code for translations (default: en)
    
    Returns crop variety details with translation and metadata.
    """
    service = CropDataService(db)
    
    # Get the variety from database
    from app.models.crop_data import CropVariety, CropVarietyTranslation
    variety = db.query(CropVariety).filter(CropVariety.id == variety_id).first()
    
    if not variety:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(
            message=f"Crop variety {variety_id} not found",
            error_code="CROP_VARIETY_NOT_FOUND"
        )
    
    # Get translation
    translation = db.query(CropVarietyTranslation).filter(
        CropVarietyTranslation.variety_id == variety_id,
        CropVarietyTranslation.language_code == language
    ).first()
    
    # Fallback to English if translation not found
    if not translation:
        translation = db.query(CropVarietyTranslation).filter(
            CropVarietyTranslation.variety_id == variety_id,
            CropVarietyTranslation.language_code == "en"
        ).first()
    
    res = CropVarietyResponse(
        id=variety.id,
        crop_type_id=variety.crop_type_id,
        code=variety.code,
        name=translation.name if translation else variety.code,
        description=translation.description if translation else None,
        variety_metadata=variety.variety_metadata or {},
        sort_order=variety.sort_order,
        is_active=variety.is_active
    )
    return {
        "success": True,
        "message": "Crop variety retrieved successfully",
        "data": res
    }
