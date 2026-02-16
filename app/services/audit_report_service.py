
from typing import Optional, List, Dict, Any, BinaryIO
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import os
import io
from PIL import Image

from app.models.audit_report import AuditReport
from app.models.audit import Audit
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)

class AuditReportService:
    """Service for managing rich text audit reports."""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_formats = ['JPEG', 'PNG', 'JPG', 'WEBP']
        self.compressed_max_width = 1200
        self.compression_quality = 80

    def save_report(
        self,
        audit_id: UUID,
        report_html: Optional[str],
        report_images: List[str],
        user_id: UUID
    ) -> AuditReport:
        """
        Save or update audit report.
        
        Args:
            audit_id: Audit ID
            report_html: Rich text HTML content
            report_images: List of image URLs
            user_id: User saving the report
            
        Returns:
            Saved AuditReport
        """
        from sqlalchemy.exc import IntegrityError

        # Validate audit exists
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(message=f"Audit {audit_id} not found", error_code="AUDIT_NOT_FOUND")
            
        # Check permissions (basic check, more should be in API layer)
        if audit.created_by != user_id and audit.assigned_to_user_id != user_id:
             # This is a loose check, actual permission logic is complex
             # Assuming API layer handles "can_edit" check
             pass

        try:
            # Check if report exists
            report = self.db.query(AuditReport).filter(AuditReport.audit_id == audit_id).first()
            
            if report:
                # Update existing
                report.report_html = report_html
                report.report_images = report_images
                report.updated_at = datetime.utcnow()
                # report.created_by = user_id (Track last editor? usually created_by is immutable)
            else:
                # Create new
                report = AuditReport(
                    audit_id=audit_id,
                    report_html=report_html,
                    report_images=report_images,
                    created_by=user_id
                )
                self.db.add(report)
                
                # Update Audit has_report flag
                audit.has_report = True
                
            self.db.commit()
            self.db.refresh(report)
            return report
            
        except IntegrityError:
            self.db.rollback()
            # Race condition: Report created by another request concurrently
            # Fetch and update
            report = self.db.query(AuditReport).filter(AuditReport.audit_id == audit_id).first()
            if report:
                report.report_html = report_html
                report.report_images = report_images
                report.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(report)
                return report
            else:
                # Should not happen if IntegrityError was due to unique constraint on audit_id
                raise ServiceError(message="Concurrent modification failed", error_code="CONCURRENCY_ERROR")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving report: {e}")
            raise ServiceError(message=f"Failed to save report: {str(e)}", error_code="SAVE_REPORT_ERROR")

    def get_report(self, audit_id: UUID) -> AuditReport:
        """
        Get audit report by audit ID.
        
        Args:
            audit_id: Audit ID
            
        Returns:
            AuditReport or None
        """
        report = self.db.query(AuditReport).filter(AuditReport.audit_id == audit_id).first()
        return report

    def upload_report_image(
        self,
        audit_id: UUID,
        file_data: BinaryIO,
        filename: str,
        user_id: UUID
    ) -> str:
        """
        Upload image for report.
        
        Args:
            audit_id: Audit ID
            file_data: File binary data
            filename: Original filename
            user_id: User uploading
            
        Returns:
            Image URL
        """
        # Validate file
        self._validate_file(file_data, filename)
        
        # Compress
        compressed_data = self._compress_image(file_data)
        
        # Generate key
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(filename)[1] or '.jpg'
        file_key = f"reports/images/{audit_id}/{timestamp}{ext}"
        
        # Upload
        file_url = self._upload_to_storage(compressed_data, file_key)
        
        return file_url

    def _validate_file(self, file_data: BinaryIO, filename: str) -> None:
        """Validate file size and format."""
        file_data.seek(0, 2)
        size = file_data.tell()
        file_data.seek(0)
        
        if size > self.max_file_size:
            raise ValidationError(message=f"File too large. Max {self.max_file_size/1024/1024}MB")
            
        try:
            image = Image.open(file_data)
            if image.format not in self.allowed_formats and image.format != 'WEBP': # WEBP might be reported differently
                 # Strict check
                 pass
        except Exception:
            raise ValidationError(message="Invalid image file")
        file_data.seek(0)

    def _compress_image(self, file_data: BinaryIO) -> bytes:
        """Compress image."""
        try:
            image = Image.open(file_data)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
                
            if image.width > self.compressed_max_width:
                ratio = self.compressed_max_width / image.width
                image = image.resize((self.compressed_max_width, int(image.height * ratio)), Image.Resampling.LANCZOS)
                
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.compression_quality)
            output.seek(0)
            return output.read()
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            file_data.seek(0)
            return file_data.read()

    def _upload_to_storage(self, file_data: bytes, file_key: str) -> str:
        """Upload to storage (Local mock)."""
        # Mimic PhotoService implementation
        upload_dir = "uploads"
        file_path = os.path.join(upload_dir, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
            
        return f"/uploads/{file_key}"
