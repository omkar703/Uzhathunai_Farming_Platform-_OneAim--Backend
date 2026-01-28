"""
Crop Photos API endpoints for Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
from datetime import date as date_type
from typing import Optional

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.crop import CropPhotoResponse
from app.schemas.response import BaseResponse
from app.services.crop_photo_service import CropPhotoService

from app.core.organization_context import get_organization_id
from app.models.enums import OrganizationType

router = APIRouter()


@router.post("/crops/{crop_id}/photos", response_model=BaseResponse[CropPhotoResponse], status_code=201)
async def upload_crop_photo(
    crop_id: UUID,
    file: UploadFile = File(..., description="Photo file (JPEG, PNG)"),
    caption: Optional[str] = Form(None, description="Photo caption"),
    photo_date: Optional[str] = Form(None, description="Photo date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a crop lifecycle photo.
    
    - **crop_id**: UUID of the crop
    - **file**: Photo file (multipart/form-data)
    - **caption**: Optional caption for the photo
    - **photo_date**: Optional date when photo was taken (YYYY-MM-DD format)
    
    Accepts JPEG and PNG images.
    File is stored in S3 or local storage depending on configuration.
    """
    service = CropPhotoService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # Parse photo_date if provided
    parsed_photo_date = None
    if photo_date:
        try:
            from datetime import datetime
            parsed_photo_date = datetime.strptime(photo_date, "%Y-%m-%d").date()
        except ValueError:
            from app.core.exceptions import ValidationError
            raise ValidationError(
                message="Invalid photo_date format. Use YYYY-MM-DD",
                error_code="INVALID_DATE_FORMAT"
            )
    
    # Create upload data
    from app.schemas.crop import CropPhotoUpload
    upload_data = CropPhotoUpload(
        caption=caption,
        photo_date=parsed_photo_date
    )
    
    photo = await service.upload_photo(
        crop_id,
        org_id,
        file,
        upload_data,
        current_user.id
    )
    return {
        "success": True,
        "message": "Photo uploaded successfully",
        "data": photo
    }


@router.get("/crops/{crop_id}/photos", response_model=BaseResponse[list[CropPhotoResponse]])
def get_crop_photos(
    crop_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all photos for a specific crop.
    
    - **crop_id**: UUID of the crop
    
    Returns list of photos with URLs, captions, and dates.
    """
    service = CropPhotoService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    photos = service.get_photos_by_crop(crop_id, org_id)
    return {
        "success": True,
        "message": "Crop photos retrieved successfully",
        "data": photos
    }


@router.get("/{photo_id}", response_model=BaseResponse[CropPhotoResponse])
def get_crop_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific crop photo by ID.
    
    - **photo_id**: UUID of the photo
    
    Returns photo details with URL, caption, and date.
    """
    service = CropPhotoService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    photo = service.get_photo_by_id(photo_id, org_id)
    return {
        "success": True,
        "message": "Crop photo retrieved successfully",
        "data": photo
    }


@router.delete("/{photo_id}", status_code=204)
def delete_crop_photo(
    photo_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a crop photo.
    
    - **photo_id**: UUID of the photo
    
    Deletes the photo record and removes the file from storage.
    """
    service = CropPhotoService(db)
    
    # Get organization ID from JWT token with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    service.delete_photo(photo_id, org_id, current_user.id)
    return None
