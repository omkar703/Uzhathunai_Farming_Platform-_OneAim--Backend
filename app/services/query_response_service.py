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
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.core.logging import get_logger

logger = get_logger(__name__)


class QueryResponseService:
    """Service for managing query responses."""
    
    def __init__(self, db: Session):
        self.db = db
        self.change_log_service = ScheduleChangeLogService(db)
    
    def create_response(
        self,
        query_id: UUID,
        response_text: str,
        user_id: UUID,
        has_recommendation: bool = False
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
