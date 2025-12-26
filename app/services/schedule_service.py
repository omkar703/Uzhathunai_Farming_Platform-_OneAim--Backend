"""
Schedule Service for Uzhathunai v2.0.

Handles schedule creation from templates and from scratch with access control.
"""
from typing import List, Tuple, Optional, Dict, Any
from datetime import date, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.schedule import Schedule, ScheduleTask
from app.models.schedule_template import ScheduleTemplate, ScheduleTemplateTask
from app.models.crop import Crop
from app.models.user import User
from app.models.enums import TaskStatus, WorkOrderStatus
from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError
from app.services.schedule_calculation_service import ScheduleCalculationService
from app.services.rbac_service import RBACService

logger = get_logger(__name__)


class ScheduleService:
    """Service for managing schedules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculation_service = ScheduleCalculationService()
        self.rbac_service = RBACService(db)
    
    def create_schedule_from_template(
        self,
        crop_id: UUID,
        template_id: UUID,
        name: str,
        template_parameters: Dict[str, Any],
        user: User
    ) -> Schedule:
        """
        Create schedule from template with automatic calculations.
        
        Args:
            crop_id: Target crop ID
            template_id: Schedule template ID
            name: Schedule name
            template_parameters: Parameters for calculations (start_date, area, plant_count)
            user: User creating the schedule
        
        Returns:
            Schedule: Created schedule with calculated tasks
        
        Validates: Requirements 6.1, 6.2, 6.3, 6.5, 6.14
        """
        # Validate access (Requirement 6.1, 6.2, 6.4)
        self._validate_schedule_creation_access(user, crop_id)
        
        # Get template
        template = self.db.query(ScheduleTemplate).filter(
            ScheduleTemplate.id == template_id,
            ScheduleTemplate.is_active == True
        ).first()
        
        if not template:
            raise NotFoundError(
                message=f"Schedule template {template_id} not found or inactive",
                error_code="TEMPLATE_NOT_FOUND",
                details={"template_id": str(template_id)}
            )
        
        # Get crop
        crop = self.db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Get template tasks
        template_tasks = self.db.query(ScheduleTemplateTask).filter(
            ScheduleTemplateTask.schedule_template_id == template_id
        ).order_by(ScheduleTemplateTask.sort_order).all()
        
        if not template_tasks:
            raise ValidationError(
                message="Template has no tasks",
                error_code="EMPTY_TEMPLATE",
                details={"template_id": str(template_id)}
            )
        
        # Validate template parameters (Requirement 6.14)
        # Check all template tasks to collect required parameters
        for template_task in template_tasks:
            self.calculation_service.validate_template_parameters(
                template_task.task_details_template,
                template_parameters
            )
        
        # Create schedule (Requirement 6.5, 6.13)
        schedule = Schedule(
            crop_id=crop_id,
            template_id=template_id,
            name=name,
            description=f"Created from template: {template.code}",
            template_parameters=template_parameters,
            is_active=True,
            created_by=user.id,
            updated_by=user.id
        )
        
        self.db.add(schedule)
        self.db.flush()
        
        # Create schedule tasks with calculations (Requirement 6.7, 6.8, 6.9, 6.10, 6.11, 6.12)
        start_date = date.fromisoformat(template_parameters['start_date'])
        
        for template_task in template_tasks:
            # Calculate due date (Requirement 6.7)
            due_date = start_date + timedelta(days=template_task.day_offset)
            
            # Calculate task quantities (Requirement 6.8, 6.9, 6.10, 6.11)
            task_details = self.calculation_service.calculate_task_quantities(
                template_task.task_details_template,
                template_parameters
            )
            
            # Create schedule task (Requirement 6.12)
            schedule_task = ScheduleTask(
                schedule_id=schedule.id,
                task_id=template_task.task_id,
                due_date=due_date,
                status=TaskStatus.NOT_STARTED,
                task_details=task_details,
                notes=template_task.notes,
                created_by=user.id,
                updated_by=user.id
            )
            
            self.db.add(schedule_task)
        
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(
            "Schedule created from template",
            extra={
                "schedule_id": str(schedule.id),
                "template_id": str(template_id),
                "crop_id": str(crop_id),
                "tasks_count": len(template_tasks),
                "user_id": str(user.id)
            }
        )
        
        return schedule
    
    def create_schedule_from_scratch(
        self,
        crop_id: UUID,
        name: str,
        description: Optional[str],
        user: User
    ) -> Schedule:
        """
        Create schedule from scratch without template.
        
        Args:
            crop_id: Target crop ID
            name: Schedule name
            description: Schedule description
            user: User creating the schedule
        
        Returns:
            Schedule: Created schedule (without tasks)
        
        Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5
        """
        # Validate access (Requirement 7.1, 7.2, 7.3)
        self._validate_schedule_creation_access(user, crop_id)
        
        # Get crop
        crop = self.db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Create schedule (Requirement 7.4, 7.5)
        schedule = Schedule(
            crop_id=crop_id,
            template_id=None,  # No template
            name=name,
            description=description,
            template_parameters=None,
            is_active=True,
            created_by=user.id,
            updated_by=user.id
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(
            "Schedule created from scratch",
            extra={
                "schedule_id": str(schedule.id),
                "crop_id": str(crop_id),
                "user_id": str(user.id)
            }
        )
        
        return schedule
    
    def get_schedules(
        self,
        user: User,
        crop_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Schedule], int]:
        """
        Get schedules with access control.
        
        Args:
            user: User requesting schedules
            crop_id: Optional filter by crop
            page: Page number
            limit: Items per page
        
        Returns:
            Tuple of (schedules list, total count)
        
        Validates: Requirements 6.3, 7.2, 7.3
        """
        offset = (page - 1) * limit
        
        # Build base query
        query = self.db.query(Schedule).filter(Schedule.is_active == True)
        
        # Filter by crop if specified
        if crop_id:
            query = query.filter(Schedule.crop_id == crop_id)
        
        # Apply access control
        if user.is_system_user():
            # System users can see all schedules
            pass
        else:
            # Get accessible crop IDs for user
            accessible_crop_ids = self._get_accessible_crop_ids(user)
            query = query.filter(Schedule.crop_id.in_(accessible_crop_ids))
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        schedules = query.order_by(Schedule.created_at.desc()).offset(offset).limit(limit).all()
        
        logger.info(
            "Schedules retrieved",
            extra={
                "user_id": str(user.id),
                "crop_id": str(crop_id) if crop_id else None,
                "count": len(schedules),
                "total": total
            }
        )
        
        return schedules, total
    
    def _validate_schedule_creation_access(self, user: User, crop_id: UUID) -> None:
        """
        Validate user can create schedule for crop.
        
        Validates: Requirements 6.1, 6.2, 6.4, 7.1, 7.2, 7.3
        """
        # System users can create schedules for any crop (Requirement 6.3, 7.3)
        if user.is_system_user():
            return
        
        # Check if user is FSP with consultancy service
        if self._is_fsp_consultancy_user(user):
            # FSP users need active work order with write permission (Requirement 6.4, 7.2)
            if not self._has_fsp_write_access(user, crop_id):
                raise PermissionError(
                    message="FSP requires active work order with write permission for this crop",
                    error_code="FSP_NO_WRITE_ACCESS",
                    details={"crop_id": str(crop_id)}
                )
            return
        
        # Farming organization users can create schedules for their own crops (Requirement 7.1)
        crop = self.db.query(Crop).filter(Crop.id == crop_id).first()
        if not crop:
            raise NotFoundError(
                message=f"Crop {crop_id} not found",
                error_code="CROP_NOT_FOUND",
                details={"crop_id": str(crop_id)}
            )
        
        # Check if crop belongs to user's organization
        from app.models.plot import Plot
        from app.models.farm import Farm
        
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
        
        if farm.organization_id != user.current_organization_id:
            raise PermissionError(
                message="Cannot create schedule for crop not owned by your organization",
                error_code="CROP_NOT_OWNED",
                details={"crop_id": str(crop_id)}
            )
    
    def _is_fsp_consultancy_user(self, user: User) -> bool:
        """Check if user is FSP with consultancy service."""
        from app.models.organization import Organization
        from app.models.enums import OrganizationType
        from app.models.fsp_service import FSPServiceListing
        
        # Check if user's organization is FSP
        org = self.db.query(Organization).filter(
            Organization.id == user.current_organization_id
        ).first()
        
        if not org or org.organization_type != OrganizationType.FSP:
            return False
        
        # Check if FSP has consultancy service
        # For now, assume all FSP organizations have consultancy capability
        # This can be enhanced to check for specific service listings
        return True
    
    def _has_fsp_write_access(self, user: User, crop_id: UUID) -> bool:
        """Check if FSP user has write access to crop via work order."""
        from app.models.work_order import WorkOrder, WorkOrderScope
        from app.models.enums import WorkOrderScopeType
        
        # Find active work orders for FSP
        work_orders = self.db.query(WorkOrder).filter(
            WorkOrder.fsp_organization_id == user.current_organization_id,
            WorkOrder.status == WorkOrderStatus.ACTIVE
        ).all()
        
        for work_order in work_orders:
            # Check if crop is in scope with write permission
            scope_item = self.db.query(WorkOrderScope).filter(
                WorkOrderScope.work_order_id == work_order.id,
                WorkOrderScope.scope == WorkOrderScopeType.CROP,
                WorkOrderScope.scope_id == crop_id
            ).first()
            
            if scope_item and scope_item.access_permissions.get('write'):
                return True
            
            # Check if crop is within broader scope (plot or farm)
            # This would require traversing the hierarchy
            # For now, only check direct crop scope
        
        return False
    
    def _get_accessible_crop_ids(self, user: User) -> List[UUID]:
        """Get list of crop IDs accessible to user."""
        from app.models.plot import Plot
        from app.models.farm import Farm
        from app.models.work_order import WorkOrder, WorkOrderScope
        from app.models.enums import WorkOrderScopeType
        
        accessible_crop_ids = []
        
        # Get crops from user's organization
        farms = self.db.query(Farm).filter(
            Farm.organization_id == user.current_organization_id
        ).all()
        
        for farm in farms:
            plots = self.db.query(Plot).filter(Plot.farm_id == farm.id).all()
            for plot in plots:
                crops = self.db.query(Crop).filter(Crop.plot_id == plot.id).all()
                accessible_crop_ids.extend([crop.id for crop in crops])
        
        # If FSP user, add crops from work orders
        if self._is_fsp_consultancy_user(user):
            work_orders = self.db.query(WorkOrder).filter(
                WorkOrder.fsp_organization_id == user.current_organization_id,
                WorkOrder.status == WorkOrderStatus.ACTIVE
            ).all()
            
            for work_order in work_orders:
                scope_items = self.db.query(WorkOrderScope).filter(
                    WorkOrderScope.work_order_id == work_order.id,
                    WorkOrderScope.scope == WorkOrderScopeType.CROP
                ).all()
                
                accessible_crop_ids.extend([item.scope_id for item in scope_items])
        
        return list(set(accessible_crop_ids))  # Remove duplicates
    
    def copy_schedule(
        self,
        source_schedule_id: UUID,
        target_crop_id: UUID,
        new_start_date: date,
        user: User
    ) -> Schedule:
        """
        Copy schedule to new crop with date adjustment.
        
        Args:
            source_schedule_id: UUID of source schedule
            target_crop_id: UUID of target crop
            new_start_date: Start date for new schedule
            user: User performing the copy
        
        Returns:
            Schedule: New schedule with adjusted dates
        
        Validates: Requirements 8.1, 8.3, 8.4, 8.5, 8.6, 8.7, 8.9
        """
        # Validate access (Requirement 8.1, 8.2)
        self._validate_schedule_creation_access(user, target_crop_id)
        
        # Get source schedule
        source_schedule = self.db.query(Schedule).filter(
            Schedule.id == source_schedule_id,
            Schedule.is_active == True
        ).first()
        
        if not source_schedule:
            raise NotFoundError(
                message=f"Source schedule {source_schedule_id} not found or inactive",
                error_code="SOURCE_SCHEDULE_NOT_FOUND",
                details={"schedule_id": str(source_schedule_id)}
            )
        
        # Get source tasks (Requirement 8.4)
        source_tasks = self.db.query(ScheduleTask).filter(
            ScheduleTask.schedule_id == source_schedule_id
        ).order_by(ScheduleTask.due_date).all()
        
        if not source_tasks:
            raise ValidationError(
                message="Source schedule has no tasks to copy",
                error_code="EMPTY_SOURCE_SCHEDULE",
                details={"schedule_id": str(source_schedule_id)}
            )
        
        # Get target crop
        target_crop = self.db.query(Crop).filter(Crop.id == target_crop_id).first()
        if not target_crop:
            raise NotFoundError(
                message=f"Target crop {target_crop_id} not found",
                error_code="TARGET_CROP_NOT_FOUND",
                details={"crop_id": str(target_crop_id)}
            )
        
        # Calculate date offset (Requirement 8.7, 8.8)
        source_start_date = min(task.due_date for task in source_tasks)
        date_offset = (new_start_date - source_start_date).days
        
        # Create new schedule (Requirement 8.9, 8.10)
        new_schedule = Schedule(
            crop_id=target_crop_id,
            template_id=None,  # Clear template reference (Requirement 8.10)
            name=f"{source_schedule.name} (Copy)",
            description=source_schedule.description,
            template_parameters=None,
            is_active=True,
            created_by=user.id,
            updated_by=user.id
        )
        
        self.db.add(new_schedule)
        self.db.flush()
        
        # Copy tasks with adjusted dates (Requirement 8.4, 8.5, 8.7, 8.9)
        for source_task in source_tasks:
            # Calculate new due date (Requirement 8.7, 8.8)
            new_due_date = source_task.due_date + timedelta(days=date_offset)
            
            # Create new task (Requirement 8.5, 8.9)
            new_task = ScheduleTask(
                schedule_id=new_schedule.id,
                task_id=source_task.task_id,
                due_date=new_due_date,
                status=TaskStatus.NOT_STARTED,  # Reset status (Requirement 8.5)
                task_details=source_task.task_details,  # Copy task details (Requirement 8.9)
                notes=source_task.notes,
                created_by=user.id,
                updated_by=user.id
            )
            
            self.db.add(new_task)
        
        # Note: Task actuals are NOT copied (Requirement 8.6)
        
        self.db.commit()
        self.db.refresh(new_schedule)
        
        logger.info(
            "Schedule copied",
            extra={
                "source_schedule_id": str(source_schedule_id),
                "new_schedule_id": str(new_schedule.id),
                "target_crop_id": str(target_crop_id),
                "date_offset_days": date_offset,
                "tasks_count": len(source_tasks),
                "user_id": str(user.id)
            }
        )
        
        return new_schedule
