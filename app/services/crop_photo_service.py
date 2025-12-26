"""
Crop Photo service for managing crop lifecycle photos.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError
from app.models.crop import Crop, CropLifecyclePhoto, CropYield, CropYieldPhoto
from app.models.plot import Plot
from app.models.farm import Farm
from app.schemas.crop import CropPhotoUpload, CropPhotoResponse

logger = get_logger(__name__)


class CropPhotoService:
    """Service for crop photo operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upload_photo(
        self,
        crop_id: UUID,
        data: CropPhotoUpload,
        org_id: UUID,
        user_id: UUID
    ) -> CropPhotoResponse:
        """
        Upload a photo for a crop.
        
        Args:
            crop_id: Crop ID
            data: Photo upload data
            org_id: Organization ID
            user_id: User ID uploading the photo
            
        Returns:
            Created photo
            
        Raises:
            NotFoundError: If crop not found
        """
        # Validate crop exists and belongs to org
        crop = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    Crop.id == crop_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Create photo
        photo = CropLifecyclePhoto(
            crop_id=crop_id,
            file_url=data.file_url,
            file_key=data.file_key,
            caption=data.caption,
            photo_date=data.photo_date,
            uploaded_by=user_id
        )
        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        logger.info(
            "Uploaded crop photo",
            extra={
                "photo_id": str(photo.id),
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "file_url": data.file_url,
                "has_caption": data.caption is not None,
                "has_photo_date": data.photo_date is not None
            }
        )
        
        return self._to_response(photo)
    
    def get_photos_by_crop(
        self,
        crop_id: UUID,
        org_id: UUID
    ) -> List[CropPhotoResponse]:
        """
        Get all photos for a crop.
        
        Args:
            crop_id: Crop ID
            org_id: Organization ID
            
        Returns:
            List of photos
            
        Raises:
            NotFoundError: If crop not found
        """
        # Validate crop exists and belongs to org
        crop = (
            self.db.query(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    Crop.id == crop_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Get photos
        photos = (
            self.db.query(CropLifecyclePhoto)
            .filter(CropLifecyclePhoto.crop_id == crop_id)
            .order_by(CropLifecyclePhoto.uploaded_at.desc())
            .all()
        )
        
        logger.info(
            "Retrieved photos by crop",
            extra={
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "count": len(photos)
            }
        )
        
        return [self._to_response(p) for p in photos]
    
    def get_photo_by_id(
        self,
        photo_id: UUID,
        org_id: UUID
    ) -> CropPhotoResponse:
        """
        Get photo by ID with ownership validation.
        
        Args:
            photo_id: Photo ID
            org_id: Organization ID
            
        Returns:
            Photo details
            
        Raises:
            NotFoundError: If photo not found or not owned by organization
        """
        photo = (
            self.db.query(CropLifecyclePhoto)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .options(
                joinedload(CropLifecyclePhoto.crop),
                joinedload(CropLifecyclePhoto.uploader)
            )
            .filter(
                and_(
                    CropLifecyclePhoto.id == photo_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not photo:
            raise NotFoundError(
                message=f"Photo {photo_id} not found",
                error_code="PHOTO_NOT_FOUND",
                details={"photo_id": str(photo_id)}
            )
        
        logger.info(
            "Retrieved photo by ID",
            extra={
                "photo_id": str(photo_id),
                "org_id": str(org_id)
            }
        )
        
        return self._to_response(photo)
    
    def delete_photo(
        self,
        photo_id: UUID,
        org_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete crop photo (hard delete with cascade).
        
        Args:
            photo_id: Photo ID
            org_id: Organization ID
            user_id: User ID deleting the photo
            
        Raises:
            NotFoundError: If photo not found
        """
        photo = (
            self.db.query(CropLifecyclePhoto)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    CropLifecyclePhoto.id == photo_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not photo:
            raise NotFoundError(
                message=f"Photo {photo_id} not found",
                error_code="PHOTO_NOT_FOUND",
                details={"photo_id": str(photo_id)}
            )
        
        # Store file info for logging before deletion
        file_url = photo.file_url
        file_key = photo.file_key
        crop_id = photo.crop_id
        
        # Hard delete (cascade will delete yield associations)
        self.db.delete(photo)
        self.db.commit()
        
        logger.info(
            "Deleted crop photo",
            extra={
                "photo_id": str(photo_id),
                "crop_id": str(crop_id),
                "org_id": str(org_id),
                "user_id": str(user_id),
                "file_url": file_url,
                "file_key": file_key
            }
        )
        
        # Note: Actual file deletion from storage (S3 or local) should be handled
        # by a separate background job or file storage service to ensure
        # database consistency even if file deletion fails
    
    def get_photos_by_yield(
        self,
        yield_id: UUID,
        org_id: UUID
    ) -> List[CropPhotoResponse]:
        """
        Get all photos associated with a yield.
        
        Args:
            yield_id: Yield ID
            org_id: Organization ID
            
        Returns:
            List of photos
            
        Raises:
            NotFoundError: If yield not found
        """
        # Validate yield exists and belongs to org
        crop_yield = (
            self.db.query(CropYield)
            .join(Crop)
            .join(Plot)
            .join(Farm)
            .filter(
                and_(
                    CropYield.id == yield_id,
                    Farm.organization_id == org_id
                )
            )
            .first()
        )
        
        if not crop_yield:
            raise NotFoundError(
                message=f"Yield {yield_id} not found",
                error_code="YIELD_NOT_FOUND",
                details={"yield_id": str(yield_id)}
            )
        
        # Get photos through yield associations
        photos = (
            self.db.query(CropLifecyclePhoto)
            .join(CropYieldPhoto, CropLifecyclePhoto.id == CropYieldPhoto.photo_id)
            .filter(CropYieldPhoto.crop_yield_id == yield_id)
            .order_by(CropLifecyclePhoto.uploaded_at.desc())
            .all()
        )
        
        logger.info(
            "Retrieved photos by yield",
            extra={
                "yield_id": str(yield_id),
                "org_id": str(org_id),
                "count": len(photos)
            }
        )
        
        return [self._to_response(p) for p in photos]
    
    def _to_response(self, photo: CropLifecyclePhoto) -> CropPhotoResponse:
        """
        Convert photo model to response schema.
        
        Args:
            photo: CropLifecyclePhoto model
            
        Returns:
            Crop photo response schema
        """
        return CropPhotoResponse(
            id=str(photo.id),
            crop_id=str(photo.crop_id),
            file_url=photo.file_url,
            file_key=photo.file_key,
            caption=photo.caption,
            photo_date=photo.photo_date,
            uploaded_at=photo.uploaded_at,
            uploaded_by=str(photo.uploaded_by) if photo.uploaded_by else None
        )
