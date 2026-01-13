"""
Task Actual Service for Uzhathunai v2.0.

Handles recording of planned and adhoc task actuals with photo uploads.
Validates FSP track permissions via work orders.
"""
from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.models.schedule import TaskActual, TaskPhoto, ScheduleTask
from app.models.enums import TaskStatus
from app.services.work_order_scope_service import WorkOrderScopeService

logger = get_logger(__name__)


class TaskActualService:
    """Service for managing task actuals (planned and adhoc)."""
    
    def __init__(self, db: Session):
        self.db = db
        self.work_order_scope_service = WorkOrderScopeService(db)
    
    def record_planned_task_actual(
        self,
        schedule_task_id: UUID,
        actual_date: date,
        task_details: dict,
        notes: Optional[str],
        user_id: UUID,
        user_org_id: UUID
    ) -> TaskActual:
        """
        Record actual execution of a planned schedule task.
        
        Args:
            schedule_task_id: UUID of the schedule task
            actual_date: Date when task was actually performed
            task_details: JSONB with actual materials, labor, machinery used
            notes: Optional notes about execution
            user_id: User recording the actual
            user_org_id: Organization ID of the user
        
        Returns:
            TaskActual: Created task actual record
        
        Raises:
            NotFoundError: If schedule task not found
            PermissionError: If user lacks permission
        """
        # Get schedule task
        schedule_task = self.db.query(ScheduleTask).filter(
            ScheduleTask.id == schedule_task_id
        ).first()
        
        if not schedule_task:
            raise NotFoundError(
                message=f"Schedule task {schedule_task_id} not found",
                error_code="SCHEDULE_TASK_NOT_FOUND"
            )
        
        # Get crop from schedule
        from app.models.crop import Crop
        crop = self.db.query(Crop).filter(
            Crop.id == schedule_task.schedule.crop_id
        ).first()
        
        if not crop:
            raise NotFoundError(
                message="Crop not found for schedule",
                error_code="CROP_NOT_FOUND"
            )
        
        # Validate permission
        self._validate_task_actual_permission(crop, user_org_id)
        
        # Create task actual
        task_actual = TaskActual(
            schedule_id=schedule_task.schedule_id,
            schedule_task_id=schedule_task_id,
            task_id=schedule_task.task_id,
            is_planned=True,
            crop_id=crop.id,
            plot_id=crop.plot_id,
            actual_date=actual_date,
            task_details=task_details,
            notes=notes,
            created_by=user_id
        )
        
        self.db.add(task_actual)
        
        # Update schedule task status to COMPLETED
        schedule_task.status = TaskStatus.COMPLETED
        schedule_task.completed_date = actual_date
        schedule_task.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(task_actual)
        
        logger.info(
            "Planned task actual recorded",
            extra={
                "task_actual_id": str(task_actual.id),
                "schedule_task_id": str(schedule_task_id),
                "actual_date": str(actual_date),
                "user_id": str(user_id)
            }
        )
        
        return task_actual
    
    def record_adhoc_task_actual(
        self,
        task_id: UUID,
        crop_id: Optional[UUID],
        plot_id: Optional[UUID],
        actual_date: date,
        task_details: dict,
        notes: Optional[str],
        user_id: UUID,
        user_org_id: UUID
    ) -> TaskActual:
        """
        Record adhoc (unplanned) task execution.
        
        Args:
            task_id: UUID of the task type
            crop_id: Optional crop ID (for crop-level tasks)
            plot_id: Optional plot ID (for plot-level tasks)
            actual_date: Date when task was performed
            task_details: JSONB with actual materials, labor, machinery used
            notes: Optional notes about execution
            user_id: User recording the actual
            user_org_id: Organization ID of the user
        
        Returns:
            TaskActual: Created task actual record
        
        Raises:
            ValidationError: If neither crop_id nor plot_id provided
            NotFoundError: If crop or plot not found
            PermissionError: If user lacks permission
        """
        # Validate at least one resource is provided
        if not crop_id and not plot_id:
            raise ValidationError(
                message="Either crop_id or plot_id must be provided for adhoc task",
                error_code="RESOURCE_REQUIRED"
            )
        
        # Validate crop if provided
        if crop_id:
            from app.models.crop import Crop
            crop = self.db.query(Crop).filter(Crop.id == crop_id).first()
            if not crop:
                raise NotFoundError(
                    message=f"Crop {crop_id} not found",
                    error_code="CROP_NOT_FOUND"
                )
            
            # Validate permission
            self._validate_task_actual_permission(crop, user_org_id)
            
            # Use crop's plot_id if not provided
            if not plot_id:
                plot_id = crop.plot_id
        
        # Validate plot if provided (and no crop)
        if plot_id and not crop_id:
            from app.models.plot import Plot
            plot = self.db.query(Plot).filter(Plot.id == plot_id).first()
            if not plot:
                raise NotFoundError(
                    message=f"Plot {plot_id} not found",
                    error_code="PLOT_NOT_FOUND"
                )
            
            # Validate permission (check farm ownership)
            from app.models.farm import Farm
            farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
            if farm.organization_id != user_org_id:
                # Check if FSP has track permission via work order
                self._validate_fsp_track_permission(user_org_id, 'PLOT', plot_id)
        
        # Validate task exists
        from app.models.reference_data import Task
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise NotFoundError(
                message=f"Task {task_id} not found",
                error_code="TASK_NOT_FOUND"
            )
        
        # Create adhoc task actual
        task_actual = TaskActual(
            schedule_id=None,
            schedule_task_id=None,
            task_id=task_id,
            is_planned=False,
            crop_id=crop_id,
            plot_id=plot_id,
            actual_date=actual_date,
            task_details=task_details,
            notes=notes,
            created_by=user_id
        )
        
        self.db.add(task_actual)
        self.db.commit()
        self.db.refresh(task_actual)
        
        logger.info(
            "Adhoc task actual recorded",
            extra={
                "task_actual_id": str(task_actual.id),
                "task_id": str(task_id),
                "crop_id": str(crop_id) if crop_id else None,
                "plot_id": str(plot_id) if plot_id else None,
                "actual_date": str(actual_date),
                "user_id": str(user_id)
            }
        )
        
        return task_actual
    
    def upload_task_photo(
        self,
        task_actual_id: UUID,
        file_url: str,
        file_key: str,
        caption: Optional[str],
        user_id: UUID
    ) -> TaskPhoto:
        """
        Upload photo for task actual.
        
        Args:
            task_actual_id: UUID of the task actual
            file_url: URL of uploaded file
            file_key: Storage key for file
            caption: Optional photo caption
            user_id: User uploading the photo
        
        Returns:
            TaskPhoto: Created task photo record
        
        Raises:
            NotFoundError: If task actual not found
        """
        # Validate task actual exists
        task_actual = self.db.query(TaskActual).filter(
            TaskActual.id == task_actual_id
        ).first()
        
        if not task_actual:
            raise NotFoundError(
                message=f"Task actual {task_actual_id} not found",
                error_code="TASK_ACTUAL_NOT_FOUND"
            )
        
        # Create task photo
        task_photo = TaskPhoto(
            task_actual_id=task_actual_id,
            file_url=file_url,
            file_key=file_key,
            caption=caption,
            uploaded_by=user_id
        )
        
        self.db.add(task_photo)
        self.db.commit()
        self.db.refresh(task_photo)
        
        logger.info(
            "Task photo uploaded",
            extra={
                "task_photo_id": str(task_photo.id),
                "task_actual_id": str(task_actual_id),
                "user_id": str(user_id)
            }
        )
        
        return task_photo
    
    def get_task_actuals(
        self,
        schedule_id: Optional[UUID] = None,
        crop_id: Optional[UUID] = None,
        plot_id: Optional[UUID] = None,
        is_planned: Optional[bool] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[TaskActual], int]:
        """
        Get task actuals with filters and pagination.
        
        Args:
            schedule_id: Optional filter by schedule
            crop_id: Optional filter by crop
            plot_id: Optional filter by plot
            is_planned: Optional filter by planned/adhoc
            start_date: Optional filter by date range start
            end_date: Optional filter by date range end
            page: Page number (1-indexed)
            limit: Items per page
        
        Returns:
            Tuple of (task actuals list, total count)
        """
        query = self.db.query(TaskActual)
        
        # Apply filters
        if schedule_id:
            query = query.filter(TaskActual.schedule_id == schedule_id)
        if crop_id:
            query = query.filter(TaskActual.crop_id == crop_id)
        if plot_id:
            query = query.filter(TaskActual.plot_id == plot_id)
        if is_planned is not None:
            query = query.filter(TaskActual.is_planned == is_planned)
        if start_date:
            query = query.filter(TaskActual.actual_date >= start_date)
        if end_date:
            query = query.filter(TaskActual.actual_date <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        task_actuals = query.order_by(TaskActual.actual_date.desc()).offset(offset).limit(limit).all()
        
        return task_actuals, total
    
    def _validate_task_actual_permission(self, crop, user_org_id: UUID):
        """
        Validate user has permission to record task actual for crop.
        
        Checks:
        1. User owns the crop's organization
        2. OR user is FSP with track permission via work order
        """
        # Get farm and organization
        from app.models.plot import Plot
        from app.models.farm import Farm
        
        plot = self.db.query(Plot).filter(Plot.id == crop.plot_id).first()
        farm = self.db.query(Farm).filter(Farm.id == plot.farm_id).first()
        
        # Check if user owns the organization
        if farm.organization_id == user_org_id:
            return True
        
        # Check if FSP has track permission via work order
        self._validate_fsp_track_permission(user_org_id, 'CROP', crop.id)
    
    def _validate_fsp_track_permission(self, fsp_org_id: UUID, resource_type: str, resource_id: UUID):
        """
        Validate FSP has track permission for resource via work order.
        
        Raises:
            PermissionError: If FSP lacks track permission
        """
        has_permission = self.work_order_scope_service.validate_fsp_access(
            fsp_org_id=fsp_org_id,
            resource_type=resource_type,
            resource_id=resource_id,
            required_permission='track'
        )
        
        if not has_permission:
            raise PermissionError(
                message=f"FSP organization lacks track permission for {resource_type} {resource_id}",
                error_code="INSUFFICIENT_PERMISSIONS"
            )
