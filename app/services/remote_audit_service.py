"""
Remote Audit Service for handling live snapshots during video calls.
"""
from typing import Optional, BinaryIO
from uuid import UUID
import io
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.models.audit import Audit, AuditResponsePhoto, AuditResponse
from app.models.video_session import VideoSession
from app.models.enums import PhotoSourceType
from app.services.photo_service import PhotoService
from app.core.exceptions import ValidationError, NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)

class RemoteAuditService:
    """Service for managing remote audit features like live snapshots."""

    def __init__(self, db: Session):
        self.db = db
        self.photo_service = PhotoService(db)

    def validate_snapshot_session(self, audit_id: UUID, session_id: UUID):
        """
        Validates that the audit and video session are linked to the same work order.
        """
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(message="Audit not found", error_code="AUDIT_NOT_FOUND")

        session = self.db.query(VideoSession).filter(VideoSession.id == session_id).first()
        if not session:
            raise NotFoundError(message="Video session not found", error_code="SESSION_NOT_FOUND")

        if audit.work_order_id != session.work_order_id:
            raise ValidationError(
                message="Audit and Video Session are not linked to the same Work Order",
                error_code="WORK_ORDER_MISMATCH"
            )
        
        # Link session to audit if not already linked
        if session.audit_id != audit_id:
            session.audit_id = audit_id
            self.db.commit()

        return audit, session

    async def process_snapshot(
        self,
        audit_id: UUID,
        session_id: UUID,
        file_data: bytes,
        user_id: UUID,
        response_id: Optional[UUID] = None
    ):
        """
        Background task to process, compress and save the snapshot.
        """
        try:
            filename = f"snapshot_{session_id}.jpg"
            
            # Compress image using PhotoService logic
            # PhotoService._compress_image expects BinaryIO, but it's a private method.
            # I'll use its logic or use public methods if available.
            
            # Generate file key
            timestamp_str = UUID(int=0) # dummy
            if response_id:
                 file_key = self.photo_service._generate_file_key(audit_id, response_id, filename)
            else:
                 import datetime
                 timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                 file_key = f"audits/{audit_id}/snapshots/{timestamp}.jpg"

            # Compress
            compressed_data = self.photo_service._compress_image(io.BytesIO(file_data))
            
            # Upload
            file_url = self.photo_service._upload_to_storage(compressed_data, file_key)

            # Create Record
            photo = AuditResponsePhoto(
                audit_id=audit_id,
                audit_response_id=response_id,
                file_url=file_url,
                file_key=file_key,
                caption="Live snapshot from video call",
                uploaded_by=user_id
            )
            
            self.db.add(photo)
            self.db.commit()
            
            logger.info(
                "Remote snapshot processed and saved",
                extra={
                    "photo_id": str(photo.id),
                    "audit_id": str(audit_id),
                    "session_id": str(session_id),
                    "user_id": str(user_id)
                }
            )
        except Exception as e:
            logger.error(f"Failed to process remote snapshot: {e}", exc_info=True)
            self.db.rollback()
