"""
Schedule Task Service for Uzhathunai v2.0.

Handles schedule task management with status tracking and change logging.
"""
from typing import List, Optional, Dict, Any
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.schedule import Schedule, ScheduleTask, ScheduleChangeLog
from app.models.user import User
from app.models.organization import OrgMemberRole
from app.models.rbac import Role
from app.models.enums import TaskStatus, ScheduleChangeTrigger
from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError

logger = get_logger(__name__)


class ScheduleTaskService:
    """Service for managing schedule tasks."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Valid status transitions
    VALID_TRANSITIONS = {
        TaskStatus.NOT_STARTED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.ON_HOLD, TaskStatus.MISSED, TaskStatus.COMPLETED],
        TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED, TaskStatus.MISSED, TaskStatus.CANCELLED, TaskStatus.ON_HOLD],
        TaskStatus.ON_HOLD: [TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED, TaskStatus.MISSED, TaskStatus.COMPLETED],
        TaskStatus.COMPLETED: [],  # Terminal state
        TaskStatus.MISSED: [],  # Terminal state
        TaskStatus.CANCELLED: []  # Terminal state
    }
    
    def create_schedule_task(
        self,
        schedule_id: UUID,
        task_id: UUID,
        due_date: date,
        task_details: Optional[Dict[str, Any]],
        notes: Optional[str],
        user: User
    ) -> ScheduleTask:
        """
        Create a new schedule task.
        
        Args:
            schedule_id: Schedule ID
            task_id: Task ID
            due_date: Task due date
            task_details: Task details JSONB
            notes: Optional notes
            user: User creating the task
        
        Returns:
            ScheduleTask: Created task
        
        Validates: Requirement 7.6, 9.10
        """
        # Validate schedule exists
        schedule = self.db.query(Schedule).filter(
            Schedule.id == schedule_id,
            Schedule.is_active == True
        ).first()
        
        if not schedule:
            raise NotFoundError(
                message=f"Schedule {schedule_id} not found or inactive",
                error_code="SCHEDULE_NOT_FOUND",
                details={"schedule_id": str(schedule_id)}
            )
        
        # Validate access
        self._validate_task_access(user, schedule)
        
        # Create task (Requirement 7.6, 7.12)
        schedule_task = ScheduleTask(
            schedule_id=schedule_id,
            task_id=task_id,
            due_date=due_date,
            status=TaskStatus.NOT_STARTED,  # Initial status (Requirement 7.12)
            task_details=task_details,
            notes=notes,
            created_by=user.id,
            updated_by=user.id
        )
        
        self.db.add(schedule_task)
        
        # Log change (Requirement 11.1)
        self._log_task_addition(schedule_id, schedule_task, user)
        
        self.db.commit()
        self.db.refresh(schedule_task)
        
        logger.info(
            "Schedule task created",
            extra={
                "schedule_task_id": str(schedule_task.id),
                "schedule_id": str(schedule_id),
                "task_id": str(task_id),
                "due_date": str(due_date),
                "user_id": str(user.id)
            }
        )
        
        return schedule_task
    
    def update_schedule_task(
        self,
        task_id: UUID,
        due_date: Optional[date],
        task_details: Optional[Dict[str, Any]],
        notes: Optional[str],
        user: User
    ) -> ScheduleTask:
        """
        Update schedule task with change logging.
        
        Args:
            task_id: Schedule task ID
            due_date: New due date (optional)
            task_details: New task details (optional)
            notes: New notes (optional)
            user: User updating the task
        
        Returns:
            ScheduleTask: Updated task
        
        Validates: Requirement 9.7, 9.8, 11.2
        """
        # Get task
        schedule_task = self.db.query(ScheduleTask).filter(
            ScheduleTask.id == task_id
        ).first()
        
        if not schedule_task:
            raise NotFoundError(
                message=f"Schedule task {task_id} not found",
                error_code="SCHEDULE_TASK_NOT_FOUND",
                details={"task_id": str(task_id)}
            )
        
        # Get schedule
        schedule = self.db.query(Schedule).filter(
            Schedule.id == schedule_task.schedule_id
        ).first()
        
        # Validate access
        self._validate_task_access(user, schedule)
        
        # Capture before state for change log (Requirement 11.2)
        task_details_before = {
            "due_date": str(schedule_task.due_date),
            "task_details": schedule_task.task_details,
            "notes": schedule_task.notes
        }
        
        # Update fields (Requirement 9.7, 9.8)
        if due_date is not None:
            schedule_task.due_date = due_date
        
        if task_details is not None:
            schedule_task.task_details = task_details
        
        if notes is not None:
            schedule_task.notes = notes
        
        schedule_task.updated_by = user.id
        
        # Capture after state
        task_details_after = {
            "due_date": str(schedule_task.due_date),
            "task_details": schedule_task.task_details,
            "notes": schedule_task.notes
        }
        
        # Log change (Requirement 11.2)
        self._log_task_modification(
            schedule_task.schedule_id,
            schedule_task,
            task_details_before,
            task_details_after,
            user
        )
        
        self.db.commit()
        self.db.refresh(schedule_task)
        
        logger.info(
            "Schedule task updated",
            extra={
                "schedule_task_id": str(task_id),
                "schedule_id": str(schedule_task.schedule_id),
                "user_id": str(user.id)
            }
        )
        
        return schedule_task
    
    def update_task_status(
        self,
        task_id: UUID,
        new_status: TaskStatus,
        completed_date: Optional[date],
        user: User
    ) -> ScheduleTask:
        """
        Update task status with transition validation.
        
        Args:
            task_id: Schedule task ID
            new_status: New status
            completed_date: Completion date (required if status is COMPLETED)
            user: User updating the status
        
        Returns:
            ScheduleTask: Updated task
        
        Validates: Requirement 9.4, 9.5, 9.6
        """
        # Get task
        schedule_task = self.db.query(ScheduleTask).filter(
            ScheduleTask.id == task_id
        ).first()
        
        if not schedule_task:
            raise NotFoundError(
                message=f"Schedule task {task_id} not found",
                error_code="SCHEDULE_TASK_NOT_FOUND",
                details={"task_id": str(task_id)}
            )
        
        # Get schedule
        schedule = self.db.query(Schedule).filter(
            Schedule.id == schedule_task.schedule_id
        ).first()
        
        # Validate access
        self._validate_task_access(user, schedule)
        
        # Validate status transition (Requirement 9.4)
        current_status = schedule_task.status
        if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
            raise ValidationError(
                message=f"Invalid status transition from {current_status.value} to {new_status.value}",
                error_code="INVALID_STATUS_TRANSITION",
                details={
                    "current_status": current_status.value,
                    "new_status": new_status.value,
                    "valid_transitions": [s.value for s in self.VALID_TRANSITIONS.get(current_status, [])]
                }
            )
        
        # Update status
        schedule_task.status = new_status
        
        # Set completed date if status is COMPLETED (Requirement 9.5)
        if new_status == TaskStatus.COMPLETED:
            if completed_date is None:
                completed_date = date.today()
            schedule_task.completed_date = completed_date
        
        schedule_task.updated_by = user.id
        
        self.db.commit()
        self.db.refresh(schedule_task)
        
        logger.info(
            "Schedule task status updated",
            extra={
                "schedule_task_id": str(task_id),
                "old_status": current_status.value,
                "new_status": new_status.value,
                "user_id": str(user.id)
            }
        )
        
        return schedule_task
    
    def get_schedule_tasks(
        self,
        schedule_id: UUID,
        status: Optional[TaskStatus] = None
    ) -> List[ScheduleTask]:
        """
        Get schedule tasks ordered by due date.
        
        Args:
            schedule_id: Schedule ID
            status: Optional status filter
        
        Returns:
            List of schedule tasks
        
        Validates: Requirement 9.3
        """
        query = self.db.query(ScheduleTask).filter(
            ScheduleTask.schedule_id == schedule_id
        )
        
        if status:
            query = query.filter(ScheduleTask.status == status)
        
        # Order by due date (Requirement 9.3)
        tasks = query.order_by(ScheduleTask.due_date).all()
        
        return tasks
    
    def get_upcoming_tasks(
        self,
        user: User,
        days_ahead: int = 7,
        crop_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming incomplete tasks across all accessible schedules.
        """
        from app.models.schedule import Schedule
        from app.models.crop import Crop
        from app.models.plot import Plot
        from app.models.farm import Farm
        from datetime import date, timedelta
        
        today = date.today()
        future_limit = today + timedelta(days=days_ahead)
        
        # This is a bit complex because we need to filter by accessible schedules
        # Get accessible crop IDs
        from app.services.schedule_service import ScheduleService
        accessible_crop_ids = ScheduleService(self.db)._get_accessible_crop_ids(user)
        
        # Query tasks
        query = self.db.query(ScheduleTask).join(Schedule)
        
        if crop_id:
            query = query.filter(Schedule.crop_id == crop_id)
        else:
            query = query.filter(Schedule.crop_id.in_(accessible_crop_ids))
            
        tasks = query.filter(
            Schedule.is_active == True,
            ScheduleTask.status.in_([TaskStatus.NOT_STARTED, TaskStatus.IN_PROGRESS]),
            ScheduleTask.due_date >= today
        ).order_by(ScheduleTask.due_date.asc()).limit(50).all()
        
        result = []
        for task in tasks:
            # Populate extra info for frontend
            task_dict = {
                "id": str(task.id),
                "schedule_id": str(task.schedule_id),
                "schedule_name": task.schedule.name,
                "task_id": str(task.task_id),
                "due_date": task.due_date.isoformat(),
                "status": task.status.value,
                "task_details": task.task_details,
                "notes": task.notes,
                "input_item_name": task.task_details.get("input_item_name") if task.task_details else None,
                "application_method_name": task.task_details.get("application_method_name") if task.task_details else None,
                "dosage": {
                    "amount": task.task_details.get("dosage_amount"),
                    "unit": task.task_details.get("dosage_unit"),
                    "per": task.task_details.get("dosage_per")
                } if task.task_details else None
            }
            
            # Add farm/plot info
            try:
                crop = task.schedule.crop
                if crop:
                    task_dict["farm_name"] = crop.plot.farm.name
                    task_dict["field_name"] = crop.plot.name
            except:
                pass
                
            result.append(task_dict)
            
        return result

    def _validate_task_access(self, user: User, schedule: Schedule) -> None:
        """
        Validate user can manage tasks for schedule.
        
        Validates: Requirement 9.1, 9.2
        """
        # System users can manage all tasks
        # Check if system user (SuperAdmin, Billing Admin, Support Agent)
        system_roles = ['SUPER_ADMIN', 'BILLING_ADMIN', 'SUPPORT_AGENT']
        user_roles = self.db.query(OrgMemberRole).join(Role).filter(
            OrgMemberRole.user_id == user.id
        ).all()
        
        if any(mr.role.code in system_roles for mr in user_roles):
            return
        
        # Get crop and check ownership
        from app.models.crop import Crop
        from app.models.plot import Plot
        from app.models.farm import Farm
        
        crop = self.db.query(Crop).filter(Crop.id == schedule.crop_id).first()
        if not crop:
            raise NotFoundError(
                message="Crop not found for schedule",
                error_code="CROP_NOT_FOUND"
            )
        
        plot = self.db.query(Plot).filter(Plot.id == crop.plot_id).first()
        if not plot:
            raise NotFoundError(
                message="Plot not found for crop",
                error_code="PLOT_NOT_FOUND"
            )
        
        farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
        if not farm:
            raise NotFoundError(
                message="Farm not found for plot",
                error_code="FARM_NOT_FOUND"
            )
        
        # Farming organization users can manage their own tasks (Requirement 9.1)
        if str(farm.organization_id) == str(user.current_organization_id):
            return
        
        # FSP users need active work order with write permission (Requirement 9.2)
        from app.models.work_order import WorkOrder, WorkOrderScope
        from app.models.enums import WorkOrderStatus, WorkOrderScopeType
        
        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.fsp_organization_id == user.current_organization_id,
            WorkOrder.status == WorkOrderStatus.ACTIVE
        ).all()
        
        for work_order in work_orders:
            scope_item = self.db.query(WorkOrderScope).filter(
                WorkOrderScope.work_order_id == work_order.id,
                WorkOrderScope.scope == WorkOrderScopeType.CROP,
                WorkOrderScope.scope_id == schedule.crop_id
            ).first()
            
            if scope_item and scope_item.access_permissions.get('write'):
                return
        
        raise PermissionError(
            message="No permission to manage tasks for this schedule",
            error_code="NO_TASK_PERMISSION",
            details={"schedule_id": str(schedule.id)}
        )
    
    def _log_task_addition(
        self,
        schedule_id: UUID,
        schedule_task: ScheduleTask,
        user: User
    ) -> None:
        """
        Log task addition to change log.
        
        Validates: Requirement 11.1
        """
        change_log = ScheduleChangeLog(
            schedule_id=schedule_id,
            task_id=schedule_task.id,
            trigger_type=ScheduleChangeTrigger.MANUAL,
            trigger_reference_id=None,
            change_type="ADD",
            task_details_before=None,  # NULL for ADD
            task_details_after={
                "due_date": str(schedule_task.due_date),
                "task_details": schedule_task.task_details,
                "notes": schedule_task.notes
            },
            change_description=f"Task added: {schedule_task.task_id}",
            is_applied=True,  # Immediately applied
            created_by=user.id
        )
        
        self.db.add(change_log)
    
    def _log_task_modification(
        self,
        schedule_id: UUID,
        schedule_task: ScheduleTask,
        task_details_before: Dict[str, Any],
        task_details_after: Dict[str, Any],
        user: User
    ) -> None:
        """
        Log task modification to change log.
        
        Validates: Requirement 11.2
        """
        change_log = ScheduleChangeLog(
            schedule_id=schedule_id,
            task_id=schedule_task.id,
            trigger_type=ScheduleChangeTrigger.MANUAL,
            trigger_reference_id=None,
            change_type="MODIFY",
            task_details_before=task_details_before,
            task_details_after=task_details_after,
            change_description=f"Task modified: {schedule_task.task_id}",
            is_applied=True,  # Immediately applied
            created_by=user.id
        )
        
        self.db.add(change_log)
