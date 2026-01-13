"""
Schedule Change Log Service for Uzhathunai v2.0.

Handles logging of all schedule modifications with trigger attribution.
Supports proposed changes that can be applied later.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.models.schedule import ScheduleChangeLog, Schedule, ScheduleTask
from app.models.enums import ScheduleChangeTrigger

logger = get_logger(__name__)


class ScheduleChangeLogService:
    """Service for managing schedule change logs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_schedule_change(
        self,
        schedule_id: UUID,
        change_type: str,
        task_id: Optional[UUID],
        task_details_before: Optional[dict],
        task_details_after: Optional[dict],
        change_description: str,
        trigger_type: ScheduleChangeTrigger,
        trigger_reference_id: Optional[UUID],
        user_id: UUID,
        is_applied: bool = True
    ) -> ScheduleChangeLog:
        """
        Log a schedule change with trigger attribution.
        
        Args:
            schedule_id: UUID of the schedule
            change_type: Type of change (ADD, MODIFY, DELETE)
            task_id: Optional UUID of the schedule task
            task_details_before: JSONB with old values (NULL for ADD)
            task_details_after: JSONB with new values (NULL for DELETE)
            change_description: Human-readable description
            trigger_type: MANUAL, QUERY, or AUDIT
            trigger_reference_id: Optional reference to query or audit
            user_id: User making the change
            is_applied: Whether change is applied (False for proposed changes)
        
        Returns:
            ScheduleChangeLog: Created change log entry
        
        Raises:
            NotFoundError: If schedule not found
            ValidationError: If change_type invalid
        """
        # Validate schedule exists
        schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise NotFoundError(
                message=f"Schedule {schedule_id} not found",
                error_code="SCHEDULE_NOT_FOUND"
            )
        
        # Validate change_type
        valid_change_types = ['ADD', 'MODIFY', 'DELETE']
        if change_type not in valid_change_types:
            raise ValidationError(
                message=f"Invalid change_type: {change_type}. Must be one of {valid_change_types}",
                error_code="INVALID_CHANGE_TYPE"
            )
        
        # Validate change_type consistency
        if change_type == 'ADD' and task_details_before is not None:
            raise ValidationError(
                message="ADD change type must have NULL task_details_before",
                error_code="INVALID_CHANGE_DATA"
            )
        
        if change_type == 'DELETE' and task_details_after is not None:
            raise ValidationError(
                message="DELETE change type must have NULL task_details_after",
                error_code="INVALID_CHANGE_DATA"
            )
        
        if change_type == 'MODIFY' and (task_details_before is None or task_details_after is None):
            raise ValidationError(
                message="MODIFY change type must have both task_details_before and task_details_after",
                error_code="INVALID_CHANGE_DATA"
            )
        
        # Create change log entry
        change_log = ScheduleChangeLog(
            schedule_id=schedule_id,
            task_id=task_id,
            trigger_type=trigger_type,
            trigger_reference_id=trigger_reference_id,
            change_type=change_type,
            task_details_before=task_details_before,
            task_details_after=task_details_after,
            change_description=change_description,
            is_applied=is_applied,
            created_by=user_id
        )
        
        self.db.add(change_log)
        self.db.commit()
        self.db.refresh(change_log)
        
        logger.info(
            "Schedule change logged",
            extra={
                "change_log_id": str(change_log.id),
                "schedule_id": str(schedule_id),
                "change_type": change_type,
                "trigger_type": trigger_type.value,
                "is_applied": is_applied,
                "user_id": str(user_id)
            }
        )
        
        return change_log
    
    def log_task_addition(
        self,
        schedule_id: UUID,
        task_id: UUID,
        task_details_after: dict,
        trigger_type: ScheduleChangeTrigger,
        trigger_reference_id: Optional[UUID],
        user_id: UUID,
        is_applied: bool = True
    ) -> ScheduleChangeLog:
        """
        Log addition of a task to schedule.
        
        Args:
            schedule_id: UUID of the schedule
            task_id: UUID of the schedule task
            task_details_after: JSONB with new task details
            trigger_type: MANUAL, QUERY, or AUDIT
            trigger_reference_id: Optional reference to query or audit
            user_id: User making the change
            is_applied: Whether change is applied
        
        Returns:
            ScheduleChangeLog: Created change log entry
        """
        return self.log_schedule_change(
            schedule_id=schedule_id,
            change_type='ADD',
            task_id=task_id,
            task_details_before=None,
            task_details_after=task_details_after,
            change_description=f"Task added to schedule",
            trigger_type=trigger_type,
            trigger_reference_id=trigger_reference_id,
            user_id=user_id,
            is_applied=is_applied
        )
    
    def log_task_modification(
        self,
        schedule_id: UUID,
        task_id: UUID,
        task_details_before: dict,
        task_details_after: dict,
        trigger_type: ScheduleChangeTrigger,
        trigger_reference_id: Optional[UUID],
        user_id: UUID,
        is_applied: bool = True
    ) -> ScheduleChangeLog:
        """
        Log modification of a schedule task.
        
        Args:
            schedule_id: UUID of the schedule
            task_id: UUID of the schedule task
            task_details_before: JSONB with old task details
            task_details_after: JSONB with new task details
            trigger_type: MANUAL, QUERY, or AUDIT
            trigger_reference_id: Optional reference to query or audit
            user_id: User making the change
            is_applied: Whether change is applied
        
        Returns:
            ScheduleChangeLog: Created change log entry
        """
        return self.log_schedule_change(
            schedule_id=schedule_id,
            change_type='MODIFY',
            task_id=task_id,
            task_details_before=task_details_before,
            task_details_after=task_details_after,
            change_description=f"Task modified in schedule",
            trigger_type=trigger_type,
            trigger_reference_id=trigger_reference_id,
            user_id=user_id,
            is_applied=is_applied
        )
    
    def log_task_deletion(
        self,
        schedule_id: UUID,
        task_id: UUID,
        task_details_before: dict,
        trigger_type: ScheduleChangeTrigger,
        trigger_reference_id: Optional[UUID],
        user_id: UUID,
        is_applied: bool = True
    ) -> ScheduleChangeLog:
        """
        Log deletion of a task from schedule.
        
        Args:
            schedule_id: UUID of the schedule
            task_id: UUID of the schedule task
            task_details_before: JSONB with deleted task details
            trigger_type: MANUAL, QUERY, or AUDIT
            trigger_reference_id: Optional reference to query or audit
            user_id: User making the change
            is_applied: Whether change is applied
        
        Returns:
            ScheduleChangeLog: Created change log entry
        """
        return self.log_schedule_change(
            schedule_id=schedule_id,
            change_type='DELETE',
            task_id=task_id,
            task_details_before=task_details_before,
            task_details_after=None,
            change_description=f"Task deleted from schedule",
            trigger_type=trigger_type,
            trigger_reference_id=trigger_reference_id,
            user_id=user_id,
            is_applied=is_applied
        )
    
    def get_change_history(
        self,
        schedule_id: UUID,
        trigger_type: Optional[ScheduleChangeTrigger] = None,
        change_type: Optional[str] = None,
        is_applied: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ScheduleChangeLog], int]:
        """
        Get change history for a schedule with filters.
        
        Args:
            schedule_id: UUID of the schedule
            trigger_type: Optional filter by trigger type
            change_type: Optional filter by change type (ADD, MODIFY, DELETE)
            is_applied: Optional filter by applied status
            start_date: Optional filter by date range start
            end_date: Optional filter by date range end
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (change logs list, total count)
        """
        query = self.db.query(ScheduleChangeLog).filter(
            ScheduleChangeLog.schedule_id == schedule_id
        )
        
        # Apply filters
        if trigger_type:
            query = query.filter(ScheduleChangeLog.trigger_type == trigger_type)
        if change_type:
            query = query.filter(ScheduleChangeLog.change_type == change_type)
        if is_applied is not None:
            query = query.filter(ScheduleChangeLog.is_applied == is_applied)
        if start_date:
            query = query.filter(ScheduleChangeLog.created_at >= start_date)
        if end_date:
            query = query.filter(ScheduleChangeLog.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        change_logs = query.order_by(ScheduleChangeLog.created_at.desc()).offset(offset).limit(limit).all()
        
        return change_logs, total
    
    def apply_proposed_changes(
        self,
        change_log_ids: List[UUID],
        user_id: UUID,
        user_org_id: UUID
    ) -> List[ScheduleChangeLog]:
        """
        Apply proposed schedule changes.
        
        Args:
            change_log_ids: List of change log IDs to apply
            user_id: User applying the changes
            user_org_id: Organization ID of the user
        
        Returns:
            List of applied change logs
        
        Raises:
            NotFoundError: If change log not found
            ValidationError: If change already applied
            PermissionError: If user lacks permission
        """
        applied_changes = []
        
        for change_log_id in change_log_ids:
            # Get change log
            change_log = self.db.query(ScheduleChangeLog).filter(
                ScheduleChangeLog.id == change_log_id
            ).first()
            
            if not change_log:
                raise NotFoundError(
                    message=f"Change log {change_log_id} not found",
                    error_code="CHANGE_LOG_NOT_FOUND"
                )
            
            # Validate not already applied
            if change_log.is_applied:
                raise ValidationError(
                    message=f"Change log {change_log_id} already applied",
                    error_code="CHANGE_ALREADY_APPLIED"
                )
            
            # Validate permission (user owns the schedule's crop's organization)
            schedule = self.db.query(Schedule).filter(
                Schedule.id == change_log.schedule_id
            ).first()
            
            from app.models.crop import Crop
            from app.models.plot import Plot
            from app.models.farm import Farm
            
            crop = self.db.query(Crop).filter(Crop.id == schedule.crop_id).first()
            plot = self.db.query(Plot).filter(Plot.id == crop.plot_id).first()
            farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
            
            if farm.organization_id != user_org_id:
                raise PermissionError(
                    message="Only schedule owner can apply proposed changes",
                    error_code="INSUFFICIENT_PERMISSIONS"
                )
            
            # Apply the change based on change_type
            if change_log.change_type == 'ADD':
                self._apply_task_addition(change_log, user_id)
            elif change_log.change_type == 'MODIFY':
                self._apply_task_modification(change_log, user_id)
            elif change_log.change_type == 'DELETE':
                self._apply_task_deletion(change_log, user_id)
            
            # Mark as applied
            change_log.is_applied = True
            change_log.applied_at = datetime.utcnow()
            change_log.applied_by = user_id
            
            applied_changes.append(change_log)
        
        self.db.commit()
        
        logger.info(
            "Proposed changes applied",
            extra={
                "change_log_ids": [str(id) for id in change_log_ids],
                "user_id": str(user_id)
            }
        )
        
        return applied_changes
    
    def _apply_task_addition(self, change_log: ScheduleChangeLog, user_id: UUID):
        """Apply a task addition change."""
        # Create new schedule task from task_details_after
        task_details = change_log.task_details_after
        
        schedule_task = ScheduleTask(
            schedule_id=change_log.schedule_id,
            task_id=task_details.get('task_id'),
            due_date=task_details.get('due_date'),
            task_details=task_details.get('task_details'),
            notes=task_details.get('notes'),
            created_by=user_id
        )
        
        self.db.add(schedule_task)
    
    def _apply_task_modification(self, change_log: ScheduleChangeLog, user_id: UUID):
        """Apply a task modification change."""
        # Update existing schedule task with task_details_after
        schedule_task = self.db.query(ScheduleTask).filter(
            ScheduleTask.id == change_log.task_id
        ).first()
        
        if schedule_task:
            task_details = change_log.task_details_after
            
            if 'due_date' in task_details:
                schedule_task.due_date = task_details['due_date']
            if 'task_details' in task_details:
                schedule_task.task_details = task_details['task_details']
            if 'notes' in task_details:
                schedule_task.notes = task_details['notes']
            
            schedule_task.updated_by = user_id
    
    def _apply_task_deletion(self, change_log: ScheduleChangeLog, user_id: UUID):
        """Apply a task deletion change."""
        # Delete schedule task
        schedule_task = self.db.query(ScheduleTask).filter(
            ScheduleTask.id == change_log.task_id
        ).first()
        
        if schedule_task:
            self.db.delete(schedule_task)
