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
from app.services.work_order_scope_service import WorkOrderScopeService
from app.models.enums import WorkOrderScopeType

logger = get_logger(__name__)


class ScheduleService:
    """Service for managing schedules."""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculation_service = ScheduleCalculationService()
        self.rbac_service = RBACService(db)
        self.scope_service = WorkOrderScopeService(db)
    
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
        
        # Restriction: Farming organizations effectively cannot use templates (New Requirement 1)
        # Check user's organization type
        from app.models.organization import Organization
        from app.models.enums import OrganizationType
        
        org = self.db.query(Organization).filter(Organization.id == user.current_organization_id).first()
        if org and org.organization_type == OrganizationType.FARMING:
             raise PermissionError(
                message="Farming organizations are only allowed to create schedules from scratch.",
                error_code="TEMPLATE_ACCESS_DENIED",
                details={"organization_id": str(user.current_organization_id)}
            )
        
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
        
        schedule.status = 'ACTIVE' # Has tasks
        return schedule
    
    def create_schedule_from_scratch(
        self,
        crop_id: UUID,
        name: str,
        description: Optional[str],
        user: User,
        start_date: Optional[date] = None,
        template_parameters: Optional[Dict[str, Any]] = None
    ) -> Schedule:
        """
        Create schedule from scratch without template.
        
        Args:
            crop_id: Target crop ID
            name: Schedule name
            description: Schedule description
            user: User creating the schedule
            start_date: Optional start date
            template_parameters: Optional parameters (area, etc.)
        
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
            
        # If parameters provided, ensure start_date is in them if passed separately
        final_params = template_parameters or {}
        if start_date:
            final_params['start_date'] = start_date.isoformat()
        
        # Create schedule (Requirement 7.4, 7.5)
        schedule = Schedule(
            crop_id=crop_id,
            template_id=None,  # No template
            name=name,
            description=description,
            template_parameters=final_params if final_params else None,
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
        
        schedule.status = TaskStatus.NOT_STARTED.value
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
        # if user.is_system_user():
        #     # System users can see all schedules
        #     pass
        # else:
        # Get accessible crop IDs for user
        accessible_crop_ids = self._get_accessible_crop_ids(user)
        query = query.filter(Schedule.crop_id.in_(accessible_crop_ids))
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        schedules = query.order_by(Schedule.created_at.desc()).offset(offset).limit(limit).all()
        
        # Populate computed fields for response schema
        for schedule in schedules:
            # 1. Computed Status
            # Logic: If active -> ACTIVE, else CANCELLED. 
            # TODO: Add logic for COMPLETED based on all tasks being completed
            schedule.status = TaskStatus.NOT_STARTED.value if not schedule.tasks else 'ACTIVE' 
            # Use 'ACTIVE' as generic status string or map to Enum if needed.
            # Frontend expects: ACTIVE, COMPLETED, PENDING, CANCELLED
            if schedule.is_active:
                schedule.status = 'ACTIVE'
            else:
                schedule.status = 'CANCELLED'
                
            # 2. Farm, Plot, and Crop Names
            try:
                if schedule.crop:
                    schedule.crop_name = schedule.crop.name
                    if schedule.crop.plot:
                        schedule.field_name = schedule.crop.plot.name
                        if schedule.crop.plot.farm:
                            schedule.farm_name = schedule.crop.plot.farm.name
            except Exception as e:
                logger.warning(f"Error populating extra fields for schedule {schedule.id}: {e}")
            
            # 3. FSP Information
            try:
                if schedule.creator:
                    # A schedule is FSP-created if the creator is part of an FSP organization
                    # We check if the creator has a member record in an FSP org
                    from app.models.organization import Organization, OrgMember
                    from app.models.enums import OrganizationType
                    
                    creator_fsp_org = self.db.query(Organization).join(OrgMember).filter(
                        OrgMember.user_id == schedule.creator.id,
                        Organization.organization_type == OrganizationType.FSP
                    ).first()
                    
                    if creator_fsp_org:
                        schedule.fsp_name = creator_fsp_org.name
                        schedule.is_fsp_created = True
                    else:
                        schedule.is_fsp_created = False
            except Exception as e:
                logger.warning(f"Error populating FSP info for schedule {schedule.id}: {e}")

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

    def get_schedule_with_details(self, user: User, schedule_id: UUID) -> Schedule:
        """Get single schedule with all details populated."""
        schedule = self.db.query(Schedule).filter(
            Schedule.id == schedule_id,
            Schedule.is_active == True
        ).first()

        if not schedule:
            raise NotFoundError(
                message=f"Schedule {schedule_id} not found",
                error_code="SCHEDULE_NOT_FOUND"
            )

        # Populate computed fields (reuse logic from get_schedules or model properties)
        # Note: Model properties (total_tasks, completed_tasks, start_date) are automatic.
        schedule.status = 'ACTIVE' if schedule.is_active else 'CANCELLED'
        
        try:
            if schedule.crop:
                schedule.crop_name = schedule.crop.name
                if schedule.crop.plot:
                    schedule.field_name = schedule.crop.plot.name
                    if schedule.crop.plot.farm:
                        schedule.farm_name = schedule.crop.plot.farm.name
        except Exception as e:
            logger.warning(f"Error populating extra fields for schedule {schedule.id}: {e}")

        try:
            if schedule.creator:
                from app.models.organization import Organization
                from app.models.enums import OrganizationType
                
                creator_org = self.db.query(Organization).filter(
                    Organization.id == schedule.creator.current_organization_id
                ).first()
                
                if creator_org:
                    schedule.fsp_name = creator_org.name
                    schedule.is_fsp_created = creator_org.organization_type == OrganizationType.FSP
        except Exception as e:
            logger.warning(f"Error populating FSP info for schedule {schedule.id}: {e}")

        # Hydrate task details with names and units
        try:
            language_code = user.preferred_language if user.preferred_language else 'en'
            logger.info(f"[SCHEDULE_SERVICE] About to hydrate tasks for schedule {schedule.id}, lang={language_code}")
            self._hydrate_task_details(schedule.tasks, language_code)
            logger.info(f"[SCHEDULE_SERVICE] Hydration completed for schedule {schedule.id}")
        except Exception as e:
            logger.error(f"Error hydrating task details for schedule {schedule.id}: {e}", exc_info=True)

        return schedule
    
    def _validate_schedule_creation_access(self, user: User, crop_id: UUID) -> None:
        """
        Validate user can create schedule for crop.
        
        Validates: Requirements 6.1, 6.2, 6.4, 7.1, 7.2, 7.3
        """
        # System users can create schedules for any crop (Requirement 6.3, 7.3)
        # if user.is_system_user():
        #     return
        
        # Check if user is FSP with consultancy service
        if self._is_fsp_consultancy_user(user):
            # FSP users need active work order with write permission (Requirement 6.4, 7.2)
            try:
                self.scope_service.validate_fsp_access(
                    fsp_organization_id=user.current_organization_id,
                    resource_type=WorkOrderScopeType.CROP,
                    resource_id=crop_id,
                    required_permission='write'
                )
            except PermissionError:
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
        
        if str(farm.organization_id) != str(user.current_organization_id):
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
                # 1. Check Global Access (Grant Farm Access)
                if work_order.access_granted:
                    # Get all crops for the farming organization
                    org_farms = self.db.query(Farm).filter(Farm.organization_id == work_order.farming_organization_id).all()
                    for farm in org_farms:
                        farm_plots = self.db.query(Plot).filter(Plot.farm_id == farm.id).all()
                        for plot in farm_plots:
                            plot_crops = self.db.query(Crop).filter(Crop.plot_id == plot.id).all()
                            accessible_crop_ids.extend([c.id for c in plot_crops])
                    continue

                # 2. Check Scoped Access
                scope_items = self.db.query(WorkOrderScope).filter(
                    WorkOrderScope.work_order_id == work_order.id
                ).all()
                
                for item in scope_items:
                    if item.scope == WorkOrderScopeType.ORGANIZATION:
                        # Add all crops for this organization
                        org_farms = self.db.query(Farm).filter(Farm.organization_id == item.scope_id).all()
                        for farm in org_farms:
                            farm_plots = self.db.query(Plot).filter(Plot.farm_id == farm.id).all()
                            for plot in farm_plots:
                                plot_crops = self.db.query(Crop).filter(Crop.plot_id == plot.id).all()
                                accessible_crop_ids.extend([c.id for c in plot_crops])
                                
                    elif item.scope == WorkOrderScopeType.FARM:
                        # Add all crops for this farm
                        farm_plots = self.db.query(Plot).filter(Plot.farm_id == item.scope_id).all()
                        for plot in farm_plots:
                            plot_crops = self.db.query(Crop).filter(Crop.plot_id == plot.id).all()
                            accessible_crop_ids.extend([c.id for c in plot_crops])
                            
                    elif item.scope == WorkOrderScopeType.PLOT:
                         # Add all crops for this plot
                        plot_crops = self.db.query(Crop).filter(Crop.plot_id == item.scope_id).all()
                        accessible_crop_ids.extend([c.id for c in plot_crops])
                        
                    elif item.scope == WorkOrderScopeType.CROP:
                        accessible_crop_ids.append(item.scope_id)
        
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
        
        new_schedule.status = 'ACTIVE' # Has tasks (copied)
        return new_schedule

    def _hydrate_task_details(self, tasks: List[ScheduleTask], language_code: str = 'en') -> None:
        """
        Hydrate tasks with denormalized data (names, units) for API response.
        Populates: input_item_name, application_method_name, dosage
        """
        logger.info(f"[HYDRATION] Starting hydration for {len(tasks) if tasks else 0} tasks")
        
        if not tasks:
            logger.warning("[HYDRATION] No tasks to hydrate")
            return
            
        from app.models.input_item import InputItem, InputItemTranslation
        from app.models.measurement_unit import MeasurementUnit, MeasurementUnitTranslation
        from app.models.reference_data import ReferenceData, ReferenceDataTranslation
        from app.schemas.schedule import Dosage
        
        # 1. Collect IDs
        input_item_ids = set()
        unit_ids = set()
        # application_method_ids = set() # logic for this TBD based on storage
        
        for task in tasks:
            if not task.task_details or not isinstance(task.task_details, dict):
                continue
                
            td = task.task_details
            
            # Collect from input_items
            if 'input_items' in td and isinstance(td['input_items'], list):
                for item in td['input_items']:
                    if 'input_item_id' in item:
                        input_item_ids.add(item['input_item_id'])
                    if 'quantity_unit_id' in item:
                        unit_ids.add(item['quantity_unit_id'])

            # Collect from concentration
            if 'concentration' in td and isinstance(td['concentration'], dict):
                conc = td['concentration']
                if 'total_solution_volume_unit_id' in conc:
                    unit_ids.add(conc['total_solution_volume_unit_id'])
                if 'ingredients' in conc and isinstance(conc['ingredients'], list):
                    for ing in conc['ingredients']:
                        if 'input_item_id' in ing:
                            input_item_ids.add(ing['input_item_id'])
                        if 'quantity_unit_id' in ing:
                            unit_ids.add(ing['quantity_unit_id'])
                            
            # Collect dosage unit from direct fields if present
            if 'dosage_unit_id' in td: # Hypothesized field
                unit_ids.add(td['dosage_unit_id'])

        logger.info(f"[HYDRATION] Collected IDs - InputItems: {len(input_item_ids)}, Units: {len(unit_ids)}")
        
        # 2. Bulk Fetch
        input_item_map = {}
        if input_item_ids:
            # Prefer translation, fallback to code/default name
            # For simplicity, fetching code/name. A real robust solution joins translations.
            # Assuming 'en' for now or code.
            items = self.db.query(InputItem).filter(InputItem.id.in_(list(input_item_ids))).all()
            for item in items:
                # Naive name fetch: translation or code. 
                # Ideally: fetch translation.
                name = item.code # Fallback
                # Try to get translation
                # Logic: We can't easily join in this bulk fetch without complexity.
                # Let's rely on a property or specific fetch if needed.
                # Checking InputItem model... has 'translations'.
                # Accessing 'translations' might trigger N+1 if not eager loaded.
                # Let's just use a simple name fetch for now or rely on loaded translations if lazy=False (default is lazy)
                # To be improved: eager load.
                
                # Fetch translation manually or use helper
                # Using a quick query for translations for these items
                trans = self.db.query(InputItemTranslation).filter(
                    InputItemTranslation.input_item_id == item.id,
                    InputItemTranslation.language_code == language_code
                ).first()
                if trans:
                    name = trans.name
                
                input_item_map[str(item.id)] = name

        unit_map = {}
        if unit_ids:
            units = self.db.query(MeasurementUnit).filter(MeasurementUnit.id.in_(list(unit_ids))).all()
            for unit in units:
                unit_map[str(unit.id)] = unit.symbol or unit.code

        logger.info(f"[HYDRATION] Fetched {len(input_item_map)} input items, {len(unit_map)} units")
        
        # 3. Hydrate Objects
        from app.models.reference_data import TaskTranslation

        active_task_translations = {}
        # Optimization: Fetch task translations for all tasks in schedule if needed
        # (Assuming laziness is okay for now or relying on existing load)
        
        for task in tasks:
            # Initialize (Null by default)
            # Use __dict__ to bypass @property setters
            task.__dict__['input_item_name'] = None
            task.__dict__['application_method_name'] = None
            task.__dict__['dosage'] = None

            td = task.task_details if (task.task_details and isinstance(task.task_details, dict)) else {}
            
            # --- Input Item Name ---
            i_name = td.get('input_item_name') 
            
            if not i_name:
                # Try concentration
                if 'concentration' in td and isinstance(td['concentration'], dict):
                    ings = td['concentration'].get('ingredients', [])
                    if ings and isinstance(ings, list) and len(ings) > 0:
                        iid = ings[0].get('input_item_id')
                        if iid: i_name = input_item_map.get(str(iid))
                
                # Try input_items list
                if not i_name and 'input_items' in td and isinstance(td['input_items'], list):
                    items = td['input_items']
                    if items and len(items) > 0:
                        iid = items[0].get('input_item_id')
                        if iid: i_name = input_item_map.get(str(iid))
            
            task.__dict__['input_item_name'] = i_name

            # --- Application Method Name ---
            app_name = td.get('application_method_name')
            if not app_name:
                 # Fallback to Task Name (e.g. "Foliar Spray")
                 # Avoid using task.name as it might not exist.
                 if task.task:
                     # Try to get translation if loaded/available
                     # This is N+1 if not careful, but for <50 tasks valid.
                     # We can try to fetch translation for preferred lang.
                     # Or use code as last resort.
                     
                     # Check if we can find translation in loaded list?
                     # task.task.translations is a relationship.
                     # Prefer direct query or simplified property if avail.
                     
                     # Simple robust fallback: Code
                     resolved_name = task.task.code
                     
                     # Try translation
                     # We can query it if not too heavy, or rely on loaded translations
                     try:
                         # Manual query to avoid N+1 issue on large lists? 
                         # Actually we can trust lazy load or cache.
                         # Let's simple query for this task's translation.
                         t_trans = self.db.query(TaskTranslation).filter(
                             TaskTranslation.task_id == task.task_id,
                             TaskTranslation.language_code == language_code
                         ).first()
                         
                         if not t_trans and language_code != 'en':
                             t_trans = self.db.query(TaskTranslation).filter(
                                 TaskTranslation.task_id == task.task_id,
                                 TaskTranslation.language_code == 'en'
                             ).first()
                             
                         if t_trans:
                             resolved_name = t_trans.name
                     except:
                         pass
                     
                     app_name = resolved_name
            
            task.__dict__['application_method_name'] = app_name
            
            logger.debug(f"[HYDRATION] Task {task.id}: input={i_name}, method={app_name}, has_details={bool(td)}")

            # --- Dosage ---
            dosage_amt = None
            dosage_unit = None
            dosage_per = None 
            
            if 'concentration' in td and isinstance(td['concentration'], dict):
                conc = td['concentration']
                ings = conc.get('ingredients', [])
                if ings and len(ings) > 0:
                    ing = ings[0]
                    dosage_amt = ing.get('concentration_per_liter')
                    dosage_amt_val = dosage_amt
                    # If it's a string, try parse? Schema says float usually.
                    
                    dosage_unit = unit_map.get(str(ing.get('quantity_unit_id'))) if ing.get('quantity_unit_id') else None
                    if dosage_amt:
                        dosage_per = "LITER_WATER"
            
            if dosage_amt is None and 'input_items' in td and isinstance(td['input_items'], list):
                 items = td.get('input_items', [])
                 if items and len(items) > 0:
                     item = items[0]
                     # Check for rate first
                     if 'rate' in item:
                          dosage_amt = item['rate']
                          # Rate unit?
                          # Usually implies per acre/hectare if not specified?
                          # Or check rate_unit_id
                     elif 'quantity' in item:
                         # If no rate, maybe total quantity is shown.
                         # User asked for dosage. 
                         pass
            
            if dosage_amt is None:
                 dosage_amt = td.get('dosage_amount')
                 du_id = td.get('dosage_unit_id')
                 if du_id: dosage_unit = unit_map.get(str(du_id))
                 else: dosage_unit = td.get('dosage_unit')
                 dosage_per = td.get('dosage_per')

            if dosage_amt is not None:
                task.__dict__['dosage'] = Dosage(
                    amount=float(dosage_amt) if isinstance(dosage_amt, (int, float)) else None, # Safe cast
                    unit=dosage_unit,
                    per=dosage_per
                )
