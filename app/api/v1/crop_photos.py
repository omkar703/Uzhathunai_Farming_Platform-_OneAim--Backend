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
from app.services.crop_photo_service import CropPhotoService

router = APIRouter()


@router.post("/crops/{crop_id}/photos", response_model=CropPhotoResponse, status_code=201)
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
    
    return await service.upload_photo(
        crop_id,
        membership.organization_id,
        file,
        upload_data,
        current_user.id
    )


@router.get("/crops/{crop_id}/photos", response_model=List[CropPhotoResponse])
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
    
    return service.get_photos_by_crop(crop_id, membership.organization_id)


@router.get("/{photo_id}", response_model=CropPhotoResponse)
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
    
    return service.get_photo_by_id(photo_id, membership.organization_id)


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
    
    service.delete_photo(photo_id, membership.organization_id, current_user.id)
    return None
