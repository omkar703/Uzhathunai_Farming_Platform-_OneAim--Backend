"""
Recommendation Service for Farm Audit Management.

Handles creation and management of audit recommendations that are stored
in schedule_change_log with trigger_type='AUDIT'.
"""
from datetime import datetime, date
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.models.schedule import ScheduleChangeLog, Schedule
from app.models.audit import Audit
from app.models.enums import ScheduleChangeTrigger, AuditStatus
from app.services.schedule_change_log_service import ScheduleChangeLogService

logger = get_logger(__name__)


class RecommendationService:
    """Service for managing audit recommendations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.change_log_service = ScheduleChangeLogService(db)
    
    def create_recommendation(
        self,
        audit_id: UUID,
        schedule_id: UUID,
        change_type: str,
        task_id: Optional[UUID],
        task_details_before: Optional[dict],
        task_details_after: Optional[dict],
        change_description: str,
        user_id: UUID
    ) -> ScheduleChangeLog:
        """
        Create a recommendation for schedule changes based on audit findings.
        
        Recommendations are stored in schedule_change_log with:
        - trigger_type = 'AUDIT'
        - trigger_reference_id = audit_id
        - is_applied = False (pending approval)
        
        Args:
            audit_id: UUID of the audit
            schedule_id: UUID of the schedule to modify
            change_type: Type of change (ADD, MODIFY, DELETE)
            task_id: Optional UUID of the schedule task (for MODIFY/DELETE)
            task_details_before: JSONB with old values (NULL for ADD)
            task_details_after: JSONB with new values (NULL for DELETE)
            change_description: Human-readable description of the recommendation
            user_id: User creating the recommendation (reviewer)
        
        Returns:
            ScheduleChangeLog: Created recommendation entry
        
        Raises:
            NotFoundError: If audit or schedule not found
            ValidationError: If audit status invalid or data inconsistent
            PermissionError: If user lacks permission
        """
        # Validate audit exists and is in correct status
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND"
            )
        
        # Recommendations can only be created during SUBMITTED, REVIEWED, or FINALIZED status
        valid_statuses = [AuditStatus.SUBMITTED, AuditStatus.REVIEWED, AuditStatus.FINALIZED]
        if audit.status not in valid_statuses:
            raise ValidationError(
                message=f"Recommendations can only be created for audits in SUBMITTED, REVIEWED, or FINALIZED status. Current status: {audit.status.value}",
                error_code="INVALID_AUDIT_STATUS"
            )
        
        if audit.status not in valid_statuses:
            raise ValidationError(
                message=f"Recommendations can only be created for audits in SUBMITTED, REVIEWED, or FINALIZED status. Current status: {audit.status.value}",
                error_code="INVALID_AUDIT_STATUS"
            )
        
        # If schedule_id is missing, try to find active schedule for the crop
        if not schedule_id:
            schedule = self.db.query(Schedule).filter(
                Schedule.crop_id == audit.crop_id,
                Schedule.is_active == True
            ).first()
            
            if not schedule:
                # Try finding any schedule for the crop
                schedule = self.db.query(Schedule).filter(
                    Schedule.crop_id == audit.crop_id
                ).order_by(Schedule.created_at.desc()).first()
                
            if not schedule:
                raise NotFoundError(
                    message=f"No associated schedule found for audit's crop {audit.crop_id}",
                    error_code="SCHEDULE_NOT_FOUND"
                )
            schedule_id = schedule.id
            logger.info(f"Auto-detected schedule {schedule_id} for audit {audit_id}")

        else:
            # Validate provided schedule exists
            schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if not schedule:
                raise NotFoundError(
                    message=f"Schedule {schedule_id} not found",
                    error_code="SCHEDULE_NOT_FOUND"
                )
            
            # Validate schedule belongs to the audit's crop
            if schedule.crop_id != audit.crop_id:
                raise ValidationError(
                    message="Schedule must belong to the audit's crop",
                    error_code="SCHEDULE_CROP_MISMATCH"
                )
        
        # Create recommendation using schedule_change_log_service
        # is_applied=False means it's a proposed change pending approval
        recommendation = self.change_log_service.log_schedule_change(
            schedule_id=schedule_id,
            change_type=change_type,
            task_id=task_id,
            task_details_before=task_details_before,
            task_details_after=task_details_after,
            change_description=change_description,
            trigger_type=ScheduleChangeTrigger.AUDIT,
            trigger_reference_id=audit_id,
            user_id=user_id,
            is_applied=False  # Pending approval
        )
        
        logger.info(
            "Audit recommendation created",
            extra={
                "recommendation_id": str(recommendation.id),
                "audit_id": str(audit_id),
                "schedule_id": str(schedule_id),
                "change_type": change_type,
                "user_id": str(user_id)
            }
        )
        
        return recommendation
    
    def get_audit_recommendations(
        self,
        audit_id: UUID,
        is_applied: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ScheduleChangeLog], int]:
        """
        Get all recommendations for a specific audit.
        
        Args:
            audit_id: UUID of the audit
            is_applied: Optional filter by applied status
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (recommendations list, total count)
        
        Raises:
            NotFoundError: If audit not found
        """
        # Validate audit exists
        audit = self.db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise NotFoundError(
                message=f"Audit {audit_id} not found",
                error_code="AUDIT_NOT_FOUND"
            )
        
        # Query recommendations
        query = self.db.query(ScheduleChangeLog).filter(
            ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT,
            ScheduleChangeLog.trigger_reference_id == audit_id
        )
        
        # Apply filter
        if is_applied is not None:
            query = query.filter(ScheduleChangeLog.is_applied == is_applied)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        recommendations = query.order_by(ScheduleChangeLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return recommendations, total
    
    def update_recommendation(
        self,
        recommendation_id: UUID,
        change_description: Optional[str] = None,
        task_details_after: Optional[dict] = None,
        user_id: UUID = None
    ) -> ScheduleChangeLog:
        """
        Update a recommendation before it's applied.
        
        Args:
            recommendation_id: UUID of the recommendation
            change_description: Optional new description
            task_details_after: Optional updated task details
            user_id: User updating the recommendation
        
        Returns:
            ScheduleChangeLog: Updated recommendation
        
        Raises:
            NotFoundError: If recommendation not found
            ValidationError: If recommendation already applied
        """
        # Get recommendation
        recommendation = self.db.query(ScheduleChangeLog).filter(
            ScheduleChangeLog.id == recommendation_id,
            ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT
        ).first()
        
        if not recommendation:
            raise NotFoundError(
                message=f"Recommendation {recommendation_id} not found",
                error_code="RECOMMENDATION_NOT_FOUND"
            )
        
        # Validate not already applied
        if recommendation.is_applied:
            raise ValidationError(
                message="Cannot update recommendation that has already been applied",
                error_code="RECOMMENDATION_ALREADY_APPLIED"
            )
        
        # Update fields
        if change_description is not None:
            recommendation.change_description = change_description
        
        if task_details_after is not None:
            # Validate change_type consistency
            if recommendation.change_type == 'DELETE':
                raise ValidationError(
                    message="Cannot update task_details_after for DELETE recommendations",
                    error_code="INVALID_UPDATE"
                )
            recommendation.task_details_after = task_details_after
        
        self.db.commit()
        self.db.refresh(recommendation)
        
        logger.info(
            "Recommendation updated",
            extra={
                "recommendation_id": str(recommendation_id),
                "user_id": str(user_id) if user_id else None
            }
        )
        
        return recommendation
    
    def delete_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete a recommendation before it's applied.
        
        Args:
            recommendation_id: UUID of the recommendation
            user_id: User deleting the recommendation
        
        Raises:
            NotFoundError: If recommendation not found
            ValidationError: If recommendation already applied
        """
        # Get recommendation
        recommendation = self.db.query(ScheduleChangeLog).filter(
            ScheduleChangeLog.id == recommendation_id,
            ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT
        ).first()
        
        if not recommendation:
            raise NotFoundError(
                message=f"Recommendation {recommendation_id} not found",
                error_code="RECOMMENDATION_NOT_FOUND"
            )
        
        # Validate not already applied
        if recommendation.is_applied:
            raise ValidationError(
                message="Cannot delete recommendation that has already been applied",
                error_code="RECOMMENDATION_ALREADY_APPLIED"
            )
        
        # Delete recommendation
        self.db.delete(recommendation)
        self.db.commit()
        
        logger.info(
            "Recommendation deleted",
            extra={
                "recommendation_id": str(recommendation_id),
                "user_id": str(user_id)
            }
        )
    
    def get_pending_recommendations_for_organization(
        self,
        farming_org_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ScheduleChangeLog], int]:
        """
        Get all pending recommendations for a farming organization.
        
        This is used by farming organization users to see all recommendations
        from audits that need their approval.
        
        Args:
            farming_org_id: UUID of the farming organization
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (recommendations list, total count)
        """
        from app.models.crop import Crop
        from app.models.plot import Plot
        from app.models.farm import Farm
        
        # Query pending recommendations for schedules belonging to the organization
        query = self.db.query(ScheduleChangeLog).join(
            Schedule, ScheduleChangeLog.schedule_id == Schedule.id
        ).join(
            Crop, Schedule.crop_id == Crop.id
        ).join(
            Plot, Crop.plot_id == Plot.id
        ).join(
            Farm, Plot.farm_id == Farm.id
        ).filter(
            Farm.organization_id == farming_org_id,
            ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT,
            ScheduleChangeLog.is_applied == False
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        recommendations = query.order_by(ScheduleChangeLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return recommendations, total
    
    def approve_recommendation(
        self,
        recommendation_id: UUID,
        user_id: UUID
    ) -> ScheduleChangeLog:
        """
        Approve a recommendation and apply it to the schedule.
        
        Sets is_applied=True and applies the recommended changes to the schedule.
        
        Args:
            recommendation_id: UUID of the recommendation
            user_id: User approving the recommendation (farming org user)
        
        Returns:
            ScheduleChangeLog: Approved recommendation
        
        Raises:
            NotFoundError: If recommendation not found
            ValidationError: If recommendation already applied
            PermissionError: If user lacks permission
        """
        # Get recommendation
        recommendation = self.db.query(ScheduleChangeLog).filter(
            ScheduleChangeLog.id == recommendation_id,
            ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT
        ).first()
        
        if not recommendation:
            raise NotFoundError(
                message=f"Recommendation {recommendation_id} not found",
                error_code="RECOMMENDATION_NOT_FOUND"
            )
        
        # Validate not already applied
        if recommendation.is_applied:
            raise ValidationError(
                message="Recommendation has already been applied",
                error_code="RECOMMENDATION_ALREADY_APPLIED"
            )
        
        # Apply the recommendation to the schedule
        self._apply_to_schedule(recommendation)
        
        # Mark as applied
        recommendation.is_applied = True
        recommendation.applied_at = datetime.utcnow()
        recommendation.applied_by = user_id
        
        self.db.commit()
        self.db.refresh(recommendation)
        
        logger.info(
            "Recommendation approved and applied",
            extra={
                "recommendation_id": str(recommendation_id),
                "schedule_id": str(recommendation.schedule_id),
                "change_type": recommendation.change_type,
                "user_id": str(user_id)
            }
        )
        
        return recommendation
    
    def reject_recommendation(
        self,
        recommendation_id: UUID,
        rejection_reason: Optional[str],
        user_id: UUID
    ) -> None:
        """
        Reject a recommendation without applying it.
        
        Deletes the recommendation from the change log.
        
        Args:
            recommendation_id: UUID of the recommendation
            rejection_reason: Optional reason for rejection
            user_id: User rejecting the recommendation (farming org user)
        
        Raises:
            NotFoundError: If recommendation not found
            ValidationError: If recommendation already applied
        """
        # Get recommendation
        recommendation = self.db.query(ScheduleChangeLog).filter(
            ScheduleChangeLog.id == recommendation_id,
            ScheduleChangeLog.trigger_type == ScheduleChangeTrigger.AUDIT
        ).first()
        
        if not recommendation:
            raise NotFoundError(
                message=f"Recommendation {recommendation_id} not found",
                error_code="RECOMMENDATION_NOT_FOUND"
            )
        
        # Validate not already applied
        if recommendation.is_applied:
            raise ValidationError(
                message="Cannot reject recommendation that has already been applied",
                error_code="RECOMMENDATION_ALREADY_APPLIED"
            )
        
        # Log rejection
        logger.info(
            "Recommendation rejected",
            extra={
                "recommendation_id": str(recommendation_id),
                "schedule_id": str(recommendation.schedule_id),
                "change_type": recommendation.change_type,
                "rejection_reason": rejection_reason,
                "user_id": str(user_id)
            }
        )
        
        # Delete recommendation
        self.db.delete(recommendation)
        self.db.commit()
    
    def _apply_to_schedule(self, recommendation: ScheduleChangeLog) -> None:
        """
        Apply a recommendation to the schedule.
        
        Implements the actual schedule changes based on change_type:
        - ADD: Create new schedule task
        - MODIFY: Update existing schedule task
        - DELETE: Delete schedule task
        
        Args:
            recommendation: ScheduleChangeLog to apply
        
        Raises:
            ValidationError: If change cannot be applied
        """
        from app.models.schedule import ScheduleTask
        
        if recommendation.change_type == 'ADD':
            # Create new schedule task from task_details_after
            if not recommendation.task_details_after:
                raise ValidationError(
                    message="task_details_after is required for ADD recommendations",
                    error_code="MISSING_TASK_DETAILS"
                )
            
            # Extract task details
            task_details = recommendation.task_details_after
            
            # Create new schedule task
            new_task = ScheduleTask(
                schedule_id=recommendation.schedule_id,
                task_id=task_details.get('task_id'),
                due_date=datetime.strptime(task_details.get('due_date'), '%Y-%m-%d').date() if isinstance(task_details.get('due_date'), str) else task_details.get('due_date'),
                status=task_details.get('status', 'NOT_STARTED'),
                task_details=task_details.get('task_details'),
                notes=task_details.get('notes'),
                created_by=recommendation.applied_by
            )
            
            self.db.add(new_task)
            
            logger.info(
                "Schedule task added from recommendation",
                extra={
                    "schedule_id": str(recommendation.schedule_id),
                    "task_id": str(task_details.get('task_id'))
                }
            )
        
        elif recommendation.change_type == 'MODIFY':
            # Update existing schedule task
            if not recommendation.task_id:
                raise ValidationError(
                    message="task_id is required for MODIFY recommendations",
                    error_code="MISSING_TASK_ID"
                )
            
            if not recommendation.task_details_after:
                raise ValidationError(
                    message="task_details_after is required for MODIFY recommendations",
                    error_code="MISSING_TASK_DETAILS"
                )
            
            # Get existing task
            task = self.db.query(ScheduleTask).filter(
                ScheduleTask.id == recommendation.task_id
            ).first()
            
            if not task:
                raise ValidationError(
                    message=f"Schedule task {recommendation.task_id} not found",
                    error_code="TASK_NOT_FOUND"
                )
            
            # Update task fields from task_details_after
            task_details = recommendation.task_details_after
            
            if 'due_date' in task_details:
                task.due_date = datetime.strptime(task_details['due_date'], '%Y-%m-%d').date() if isinstance(task_details['due_date'], str) else task_details['due_date']
            
            if 'status' in task_details:
                task.status = task_details['status']
            
            if 'task_details' in task_details:
                task.task_details = task_details['task_details']
            
            if 'notes' in task_details:
                task.notes = task_details['notes']
            
            task.updated_by = recommendation.applied_by
            task.updated_at = datetime.utcnow()
            
            logger.info(
                "Schedule task modified from recommendation",
                extra={
                    "schedule_id": str(recommendation.schedule_id),
                    "task_id": str(recommendation.task_id)
                }
            )
        
        elif recommendation.change_type == 'DELETE':
            # Delete schedule task
            if not recommendation.task_id:
                raise ValidationError(
                    message="task_id is required for DELETE recommendations",
                    error_code="MISSING_TASK_ID"
                )
            
            # Get existing task
            task = self.db.query(ScheduleTask).filter(
                ScheduleTask.id == recommendation.task_id
            ).first()
            
            if not task:
                raise ValidationError(
                    message=f"Schedule task {recommendation.task_id} not found",
                    error_code="TASK_NOT_FOUND"
                )
            
            # Delete task
            self.db.delete(task)
            
            logger.info(
                "Schedule task deleted from recommendation",
                extra={
                    "schedule_id": str(recommendation.schedule_id),
                    "task_id": str(recommendation.task_id)
                }
            )
        
        else:
            raise ValidationError(
                message=f"Invalid change_type: {recommendation.change_type}",
                error_code="INVALID_CHANGE_TYPE"
            )
