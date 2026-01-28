"""
Photo service for Farm Audit Management System.

Handles photo upload, validation, compression, and S3 storage for audit responses.
Validates photo count against parameter metadata (min_photos, max_photos).
"""
from typing import Optional, List, BinaryIO
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from PIL import Image
import io
import os

from app.models.audit import AuditResponse, AuditResponsePhoto, AuditParameterInstance
from app.models.enums import PhotoSourceType
from app.core.exceptions import ValidationError, NotFoundError, ServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class PhotoService:
    """Service for managing audit response photos."""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_formats = ['JPEG', 'PNG', 'JPG']
        self.thumbnail_size = (300, 300)
        self.compressed_max_width = 1024
        self.compression_quality = 70
    
    def upload_photo(
        self,
        audit_id: UUID,
        response_id: UUID,
        file_data: BinaryIO,
        filename: str,
        caption: Optional[str],
        user_id: UUID
    ) -> AuditResponsePhoto:
        """
        Upload photo for audit response with validation and compression.
        
        Args:
            audit_id: Audit ID
            response_id: Audit response ID
            file_data: File binary data
            filename: Original filename
            caption: Optional photo caption
            user_id: User uploading the photo
            
        Returns:
            Created AuditResponsePhoto
            
        Raises:
            NotFoundError: If response not found
            ValidationError: If validation fails
            ServiceError: If upload fails
        """
        # Get response and validate
        response = self.db.query(AuditResponse).filter(
            AuditResponse.id == response_id,
            AuditResponse.audit_id == audit_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Audit response {response_id} not found",
                error_code="RESPONSE_NOT_FOUND"
            )
        
        # Validate photo count against parameter metadata
        self._validate_photo_count(response)
        
        # Validate file
        self._validate_file(file_data, filename)
        
        # Compress image
        compressed_data = self._compress_image(file_data)
        
        # Generate file key
        file_key = self._generate_file_key(audit_id, response_id, filename)
        
        # Upload to S3 (or local storage for now)
        file_url = self._upload_to_storage(compressed_data, file_key)
        
        # Create photo record
        photo = AuditResponsePhoto(
            audit_id=audit_id,
            audit_response_id=response_id,
            file_url=file_url,
            file_key=file_key,
            caption=caption,
            uploaded_by=user_id
        )

        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        logger.info(
            "Photo uploaded",
            extra={
                "photo_id": str(photo.id),
                "response_id": str(response_id),
                "audit_id": str(audit_id),
                "user_id": str(user_id)
            }
        )
        
        return photo
    
    def upload_evidence(
        self,
        audit_id: UUID,
        file_data: BinaryIO,
        filename: str,
        caption: Optional[str],
        user_id: UUID
    ) -> AuditResponsePhoto:
        """
        Upload evidence photo for audit (without linking to response initially).
        
        Args:
            audit_id: Audit ID
            file_data: File binary data
            filename: Original filename
            caption: Optional photo caption
            user_id: User uploading the photo
            
        Returns:
            Created AuditResponsePhoto
        """
        # Validate audit exists
        from app.models.audit import Audit
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND"
            )

        # Validate file
        self._validate_file(file_data, filename)
        
        # Compress image
        compressed_data = self._compress_image(file_data)
        
        # Generate file key (use 'evidence' prefix or just handle missing response_id in path)
        # We'll use a specific path for unlinked evidence or just None for response_id part
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(filename)[1] or '.jpg'
        # Path: audits/{audit_id}/evidence/{timestamp}{ext}
        file_key = f"audits/{audit_id}/evidence/{timestamp}{ext}"
        
        # Upload to storage
        file_url = self._upload_to_storage(compressed_data, file_key)
        
        # Create photo record
        photo = AuditResponsePhoto(
            audit_id=audit_id,
            audit_response_id=None, # Not linked yet
            file_url=file_url,
            file_key=file_key,
            caption=caption,
            uploaded_by=user_id,
            source_type=PhotoSourceType.MANUAL_UPLOAD
        )
        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        logger.info(
            "Evidence uploaded",
            extra={
                "photo_id": str(photo.id),
                "audit_id": str(audit_id),
                "user_id": str(user_id)
            }
        )
        
        return photo
    
    def get_photos(
        self,
        audit_id: UUID,
        response_id: UUID
    ) -> List[AuditResponsePhoto]:
        """
        Get all photos for an audit response.
        
        Args:
            audit_id: Audit ID
            response_id: Audit response ID
            
        Returns:
            List of AuditResponsePhoto
        """
        # Verify response exists
        response = self.db.query(AuditResponse).filter(
            AuditResponse.id == response_id,
            AuditResponse.audit_id == audit_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Audit response {response_id} not found",
                error_code="RESPONSE_NOT_FOUND"
            )
        
        photos = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.audit_response_id == response_id
        ).order_by(AuditResponsePhoto.uploaded_at).all()
        
        return photos
    
    def delete_photo(
        self,
        audit_id: UUID,
        response_id: UUID,
        photo_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete a photo from audit response.
        
        Args:
            audit_id: Audit ID
            response_id: Audit response ID
            photo_id: Photo ID to delete
            user_id: User deleting the photo
            
        Raises:
            NotFoundError: If photo not found
        """
        # Get photo
        photo = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.id == photo_id,
            AuditResponsePhoto.audit_response_id == response_id
        ).first()
        
        if not photo:
            raise NotFoundError(
                message=f"Photo {photo_id} not found",
                error_code="PHOTO_NOT_FOUND"
            )
        
        # Verify response belongs to audit
        response = self.db.query(AuditResponse).filter(
            AuditResponse.id == response_id,
            AuditResponse.audit_id == audit_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Audit response {response_id} not found",
                error_code="RESPONSE_NOT_FOUND"
            )
        
        # Delete from storage
        self._delete_from_storage(photo.file_key)
        
        # Delete from database
        self.db.delete(photo)
        self.db.commit()
        
        logger.info(
            "Photo deleted",
            extra={
                "photo_id": str(photo_id),
                "response_id": str(response_id),
                "audit_id": str(audit_id),
                "user_id": str(user_id)
            }
        )
    
    def _validate_photo_count(self, response: AuditResponse) -> None:
        """
        Validate photo count against parameter metadata.
        
        Args:
            response: Audit response
            
        Raises:
            ValidationError: If max photos exceeded
        """
        # Get parameter instance
        param_instance = self.db.query(AuditParameterInstance).filter(
            AuditParameterInstance.id == response.audit_parameter_instance_id
        ).first()
        
        if not param_instance:
            return
        
        # Get parameter metadata from snapshot
        snapshot = param_instance.parameter_snapshot or {}
        metadata = snapshot.get('parameter_metadata', {})
        
        max_photos = metadata.get('max_photos', 3)  # Default to 3
        
        # Count existing photos
        current_count = self.db.query(AuditResponsePhoto).filter(
            AuditResponsePhoto.audit_response_id == response.id
        ).count()
        
        if current_count >= max_photos:
            raise ValidationError(
                message=f"Maximum {max_photos} photos allowed for this parameter",
                error_code="MAX_PHOTOS_EXCEEDED",
                details={"max_photos": max_photos, "current_count": current_count}
            )
    
    def _validate_file(self, file_data: BinaryIO, filename: str) -> None:
        """
        Validate file size and format.
        
        Args:
            file_data: File binary data
            filename: Original filename
            
        Raises:
            ValidationError: If validation fails
        """
        # Check file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Reset to beginning
        
        if file_size > self.max_file_size:
            raise ValidationError(
                message=f"File size exceeds maximum {self.max_file_size / 1024 / 1024}MB",
                error_code="FILE_TOO_LARGE",
                details={"max_size_mb": self.max_file_size / 1024 / 1024}
            )
        
        # Check file format
        try:
            image = Image.open(file_data)
            if image.format not in self.allowed_formats:
                raise ValidationError(
                    message=f"Invalid file format. Allowed: {', '.join(self.allowed_formats)}",
                    error_code="INVALID_FILE_FORMAT",
                    details={"allowed_formats": self.allowed_formats}
                )
            file_data.seek(0)  # Reset for later use
        except Exception as e:
            raise ValidationError(
                message="Invalid image file",
                error_code="INVALID_IMAGE",
                details={"error": str(e)}
            )
    
    def _compress_image(self, file_data: BinaryIO) -> bytes:
        """
        Compress image to reduce file size.
        
        Args:
            file_data: Original file data
            
        Returns:
            Compressed image bytes
        """
        try:
            image = Image.open(file_data)
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            # Resize if too large
            if image.width > self.compressed_max_width:
                ratio = self.compressed_max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((self.compressed_max_width, new_height), Image.Resampling.LANCZOS)
            
            # Compress
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.compression_quality, optimize=True)
            output.seek(0)
            
            return output.read()
        except Exception as e:
            logger.error(f"Image compression failed: {e}", exc_info=True)
            # Return original if compression fails
            file_data.seek(0)
            return file_data.read()
    
    def _generate_file_key(self, audit_id: UUID, response_id: UUID, filename: str) -> str:
        """
        Generate unique file key for storage.
        
        Args:
            audit_id: Audit ID
            response_id: Response ID
            filename: Original filename
            
        Returns:
            File key
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(filename)[1] or '.jpg'
        return f"audits/{audit_id}/responses/{response_id}/{timestamp}{ext}"
    
    def _upload_to_storage(self, file_data: bytes, file_key: str) -> str:
        """
        Upload file to storage (S3 or local).
        
        For now, this is a placeholder that stores locally.
        In production, this should upload to S3.
        
        Args:
            file_data: File bytes
            file_key: Storage key
            
        Returns:
            File URL
        """
        # TODO: Implement S3 upload when AWS credentials are configured
        # For now, store locally
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create subdirectories
        file_path = os.path.join(upload_dir, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Return URL (in production, this would be S3 URL)
        return f"/uploads/{file_key}"
    
    def _delete_from_storage(self, file_key: Optional[str]) -> None:
        """
        Delete file from storage.
        
        Args:
            file_key: Storage key
        """
        if not file_key:
            return
        
        # TODO: Implement S3 deletion when AWS credentials are configured
        # For now, delete locally
        try:
            file_path = os.path.join("uploads", file_key)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Failed to delete file {file_key}: {e}", exc_info=True)
    
    def generate_thumbnail(self, file_data: BinaryIO) -> bytes:
        """
        Generate thumbnail for image.
        
        Args:
            file_data: Original file data
            
        Returns:
            Thumbnail bytes
        """
        try:
            image = Image.open(file_data)
            image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            return output.read()
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}", exc_info=True)
            raise ServiceError(
                message="Failed to generate thumbnail",
                error_code="THUMBNAIL_GENERATION_FAILED"
            )
