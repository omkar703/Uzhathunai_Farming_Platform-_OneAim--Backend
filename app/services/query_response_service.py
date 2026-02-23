"""
Query response service for Uzhathunai v2.0.

Handles query responses, photo attachments, and schedule change proposals.
Supports back-and-forth conversation between farming org and FSP.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.query import Query, QueryResponse, QueryPhoto
from app.models.enums import QueryStatus
from app.services.schedule_change_log_service import ScheduleChangeLogService
from app.core.exceptions import NotFoundError, ValidationError, PermissionError, ServiceError
from app.core.logging import get_logger
from app.core.config import settings
import os
import io
import boto3
from PIL import Image
from typing import BinaryIO
from botocore.exceptions import ClientError

logger = get_logger(__name__)


class QueryResponseService:
    """Service for managing query responses."""
    
    def __init__(self, db: Session):
        self.db = db
        self.change_log_service = ScheduleChangeLogService(db)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_formats = ['JPEG', 'PNG', 'JPG']
        self.thumbnail_size = (300, 300)
        self.compressed_max_width = 1024
        self.compression_quality = 70
    
    def create_response(
        self,
        query_id: UUID,
        response_text: str,
        user_id: UUID,
        has_recommendation: bool = False,
        responder_role: str = None
    ) -> QueryResponse:
        """
        Create a response to a query.
        
        Supports back-and-forth conversation from both parties.
        Updates query status to IN_PROGRESS if currently OPEN.
        
        Requirements: 13.1, 13.2, 13.3, 13.10, 13.11, 13.12
        """
        # Validate query exists
        query = self.db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            raise NotFoundError(
                message=f"Query {query_id} not found",
                error_code="QUERY_NOT_FOUND",
                details={"query_id": str(query_id)}
            )
        
        # Validate response text
        if not response_text or not response_text.strip():
            raise ValidationError(
                message="Response text cannot be empty",
                error_code="EMPTY_RESPONSE_TEXT"
            )
        
        # Create response (Requirement 13.1)
        response = QueryResponse(
            query_id=query_id,
            response_text=response_text.strip(),
            has_recommendation=has_recommendation,  # Requirement 13.3
            responder_role=responder_role,
            created_by=user_id
        )
        
        self.db.add(response)
        
        # Update query status to IN_PROGRESS if currently OPEN (Requirement 13.2)
        if query.status == QueryStatus.OPEN:
            query.status = QueryStatus.IN_PROGRESS
            query.updated_by = user_id
        
        # Update query status back to IN_PROGRESS if PENDING_CLARIFICATION (Requirement 13.10)
        elif query.status == QueryStatus.PENDING_CLARIFICATION:
            query.status = QueryStatus.IN_PROGRESS
            query.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(response)
        
        logger.info(
            "Query response created",
            extra={
                "response_id": str(response.id),
                "query_id": str(query_id),
                "query_number": query.query_number,
                "has_recommendation": has_recommendation,
                "created_by": str(user_id)
            }
        )
        
        return response
    


    def upload_response_photo(
        self,
        response_id: UUID,
        file_data: BinaryIO,
        filename: str,
        user_id: UUID,
        caption: Optional[str] = None
    ) -> QueryPhoto:
        """
        Upload photo for query response with validation and compression.
        """
        # Validate response exists
        response = self.db.query(QueryResponse).filter(
            QueryResponse.id == response_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Query response {response_id} not found",
                error_code="QUERY_RESPONSE_NOT_FOUND",
                details={"response_id": str(response_id)}
            )
        
        # Validate file
        self._validate_file(file_data, filename)
        
        # Compress image
        compressed_data = self._compress_image(file_data)
        
        # Generate file key
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        ext = os.path.splitext(filename)[1] or '.jpg'
        file_key = f"queries/{response.query_id}/responses/{response_id}/{timestamp}{ext}"
        
        # Upload to storage
        file_url = self._upload_to_storage(compressed_data, file_key)
        
        # Create photo record
        photo = QueryPhoto(
            query_response_id=response_id,
            file_url=file_url,
            file_key=file_key,
            caption=caption,
            uploaded_by=user_id
        )
        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        logger.info(
            "Photo uploaded for query response",
            extra={
                "photo_id": str(photo.id),
                "response_id": str(response_id),
                "uploaded_by": str(user_id)
            }
        )
        
        return photo

    def _validate_file(self, file_data: BinaryIO, filename: str) -> None:
        """Validate file size and format."""
        file_data.seek(0, 2)
        file_size = file_data.tell()
        file_data.seek(0)
        
        if file_size > self.max_file_size:
            raise ValidationError(
                message=f"File size exceeds maximum {self.max_file_size / 1024 / 1024}MB",
                error_code="FILE_TOO_LARGE"
            )
        
        try:
            image = Image.open(file_data)
            if image.format not in self.allowed_formats:
                raise ValidationError(
                    message=f"Invalid file format. Allowed: {', '.join(self.allowed_formats)}",
                    error_code="INVALID_FILE_FORMAT"
                )
            file_data.seek(0)
        except Exception as e:
            raise ValidationError(
                message="Invalid image file",
                error_code="INVALID_IMAGE",
                details={"error": str(e)}
            )

    def _compress_image(self, file_data: BinaryIO) -> bytes:
        """Compress image."""
        try:
            image = Image.open(file_data)
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            
            if image.width > self.compressed_max_width:
                ratio = self.compressed_max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((self.compressed_max_width, new_height), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=self.compression_quality, optimize=True)
            output.seek(0)
            return output.read()
        except Exception:
            file_data.seek(0)
            return file_data.read()

    def _upload_to_storage(self, file_data: bytes, file_key: str) -> str:
        """Upload to S3 or local."""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION_NAME
                )
                s3_client.put_object(
                    Bucket=settings.AWS_S3_BUCKET,
                    Key=file_key,
                    Body=file_data,
                    ContentType='image/jpeg'
                )
                return f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file_key}"
            except ClientError as e:
                raise ServiceError(
                    message="Failed to upload photo to storage",
                    error_code="STORAGE_UPLOAD_FAILED",
                    details={"error": str(e)}
                )
        else:
            # Local storage fallback
            upload_dir = getattr(settings, 'UPLOAD_DIR', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, file_key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            return f"/uploads/{file_key}"
    
    def attach_photo_to_response(
        self,
        response_id: UUID,
        file_url: str,
        file_key: str,
        user_id: UUID,
        caption: Optional[str] = None
    ) -> QueryPhoto:
        """
        Attach photo to a query response.
        
        Requirements: 13.4
        """
        # Validate response exists
        response = self.db.query(QueryResponse).filter(
            QueryResponse.id == response_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Query response {response_id} not found",
                error_code="QUERY_RESPONSE_NOT_FOUND",
                details={"response_id": str(response_id)}
            )
        
        # Create photo
        photo = QueryPhoto(
            query_response_id=response_id,
            file_url=file_url,
            file_key=file_key,
            caption=caption,
            uploaded_by=user_id
        )
        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        logger.info(
            "Photo attached to query response",
            extra={
                "photo_id": str(photo.id),
                "response_id": str(response_id),
                "query_id": str(response.query_id),
                "uploaded_by": str(user_id)
            }
        )
        
        return photo
    
    def attach_photo_to_query(
        self,
        query_id: UUID,
        file_url: str,
        file_key: str,
        user_id: UUID,
        caption: Optional[str] = None
    ) -> QueryPhoto:
        """
        Attach photo to a query (when initially submitted).
        
        Requirements: 12.7
        """
        # Validate query exists
        query = self.db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            raise NotFoundError(
                message=f"Query {query_id} not found",
                error_code="QUERY_NOT_FOUND",
                details={"query_id": str(query_id)}
            )
        
        # Create photo
        photo = QueryPhoto(
            query_id=query_id,
            file_url=file_url,
            file_key=file_key,
            caption=caption,
            uploaded_by=user_id
        )
        
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        
        logger.info(
            "Photo attached to query",
            extra={
                "photo_id": str(photo.id),
                "query_id": str(query_id),
                "query_number": query.query_number,
                "uploaded_by": str(user_id)
            }
        )
        
        return photo
    
    def propose_schedule_changes(
        self,
        query_id: UUID,
        schedule_id: UUID,
        changes: List[dict],
        user_id: UUID
    ) -> List[dict]:
        """
        Propose schedule changes as part of query response.
        
        Creates change log entries with trigger_type=QUERY and is_applied=false.
        Requires FSP to have write permission via work order.
        
        Requirements: 13.5, 13.6, 13.7, 13.12
        
        Args:
            query_id: Query ID
            schedule_id: Schedule ID to propose changes for
            changes: List of change dictionaries with:
                - change_type: 'ADD', 'MODIFY', or 'DELETE'
                - task_id: Task ID (for ADD/MODIFY)
                - task_details_before: Previous task details (for MODIFY/DELETE)
                - task_details_after: New task details (for ADD/MODIFY)
                - change_description: Description of change
            user_id: User proposing changes
        
        Returns:
            List of created change log entries
        """
        # Validate query exists
        query = self.db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            raise NotFoundError(
                message=f"Query {query_id} not found",
                error_code="QUERY_NOT_FOUND",
                details={"query_id": str(query_id)}
            )
        
        # Create change log entries with trigger_type=QUERY
        change_logs = []
        
        for change in changes:
            change_log = self.change_log_service.log_schedule_change(
                schedule_id=schedule_id,
                trigger_type='QUERY',
                trigger_reference_id=query_id,
                change_type=change['change_type'],
                task_id=change.get('task_id'),
                task_details_before=change.get('task_details_before'),
                task_details_after=change.get('task_details_after'),
                change_description=change.get('change_description', ''),
                user_id=user_id,
                is_applied=False  # Proposed changes not yet applied (Requirement 13.6)
            )
            change_logs.append(change_log)
        
        logger.info(
            "Schedule changes proposed via query",
            extra={
                "query_id": str(query_id),
                "query_number": query.query_number,
                "schedule_id": str(schedule_id),
                "changes_count": len(changes),
                "proposed_by": str(user_id)
            }
        )
        
        return change_logs
    
    def get_query_conversation(self, query_id: UUID) -> List[QueryResponse]:
        """
        Get all responses for a query in chronological order.
        
        Supports viewing back-and-forth conversation.
        
        Requirements: 13.11, 13.12
        """
        # Validate query exists
        query = self.db.query(Query).filter(Query.id == query_id).first()
        
        if not query:
            raise NotFoundError(
                message=f"Query {query_id} not found",
                error_code="QUERY_NOT_FOUND",
                details={"query_id": str(query_id)}
            )
        
        # Get all responses ordered by creation time
        responses = self.db.query(QueryResponse).filter(
            QueryResponse.query_id == query_id
        ).order_by(QueryResponse.created_at.asc()).all()
        
        logger.info(
            "Query conversation retrieved",
            extra={
                "query_id": str(query_id),
                "query_number": query.query_number,
                "responses_count": len(responses)
            }
        )
        
        return responses
    
    def get_response(self, response_id: UUID) -> QueryResponse:
        """Get query response by ID."""
        response = self.db.query(QueryResponse).filter(
            QueryResponse.id == response_id
        ).first()
        
        if not response:
            raise NotFoundError(
                message=f"Query response {response_id} not found",
                error_code="QUERY_RESPONSE_NOT_FOUND",
                details={"response_id": str(response_id)}
            )
        
        return response
