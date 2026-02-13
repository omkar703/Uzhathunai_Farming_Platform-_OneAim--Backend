"""
Schedule Service for Uzhathunai v2.0.

Handles schedule creation from templates and from scratch with access control.
"""
from typing import List, Tuple, Optional, Dict, Any
from datetime import date, datetime, timedelta
import uuid
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.schedule import Schedule, ScheduleTask
from app.models.schedule_template import ScheduleTemplate, ScheduleTemplateTask
from app.models.crop import Crop
from app.models.user import User
from app.models.enums import TaskStatus, WorkOrderStatus
from app.models.input_item import InputItem
from app.models.reference_data import Task, ReferenceData
from app.schemas.schedule import ScheduleWithTasksResponse, ScheduleTaskCreate
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
                task_name=template_task.task_name,
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
        template_parameters: Optional[Dict[str, Any]] = None,
        items: Optional[List[ScheduleTaskCreate]] = None
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
            items: Optional tasks to create
        
        Returns:
            Schedule: Created schedule with tasks
        
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
        self.db.flush()
        
        # Add tasks if provided
        if items:
            for item in items:
                # Consolidate task_details from top-level fields if needed
                td = item.task_details or {}
                if item.input_item_id:
                    td['input_item_id'] = str(item.input_item_id)
                if item.application_method_id:
                    td['application_method_id'] = str(item.application_method_id)
                if item.dosage:
                    td['dosage'] = item.dosage
                
                # If task_id is missing, try to map from input item
                task_id = item.task_id
                if not task_id and td:
                    input_item_id = td.get('input_item_id')
                    if input_item_id:
                        input_item = self.db.query(InputItem).filter(InputItem.id == input_item_id).first()
                        if input_item:
                            target_code = 'GENERAL_FARMING' # Default fallback
                            if input_item.type == 'FERTILIZER':
                                target_code = 'FERTIGATION'
                            elif input_item.type == 'PESTICIDE':
                                target_code = 'FOLIAR_SPRAY'
                            
                            mapped_task = self.db.query(Task).filter(Task.code == target_code).first()
                            if mapped_task:
                                task_id = mapped_task.id
                
                if not task_id:
                    fallback_task = self.db.query(Task).order_by(Task.sort_order).first()
                    if fallback_task:
                        task_id = fallback_task.id

                # Create schedule task
                schedule_task = ScheduleTask(
                    schedule_id=schedule.id,
                    task_id=task_id,
                    due_date=item.due_date or start_date or date.today(),
                    status=TaskStatus.NOT_STARTED.value,
                    task_details=td,
                    notes=item.notes,
                    created_by=user.id,
                    updated_by=user.id
                )
                self.db.add(schedule_task)

        self.db.commit()
        self.db.refresh(schedule)
        
        logger.info(
            "Schedule created from scratch with tasks",
            extra={
                "schedule_id": str(schedule.id),
                "crop_id": str(crop_id),
                "user_id": str(user.id),
                "task_count": len(items) if items else 0
            }
        )
        
        schedule.status = TaskStatus.NOT_STARTED.value
        return schedule
    
    def get_schedules(
        self,
        user: User,
        crop_id: Optional[UUID] = None,
        fsp_id: Optional[UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Schedule], int]:
        """
        Get schedules with access control.
        
        Args:
            user: User requesting schedules
            crop_id: Optional filter by crop
            fsp_id: Optional filter by Service Partner organization
            status: Optional filter by status (ACTIVE, CANCELLED)
            page: Page number
            limit: Items per page
        
        Returns:
            Tuple of (schedules list, total count)
        
        Validates: Requirements 6.3, 7.2, 7.3
        """
        offset = (page - 1) * limit
        
        # Build base query
        query = self.db.query(Schedule)
        
        # Filter by status if specified
        if status:
            if status == 'ACTIVE':
                query = query.filter(Schedule.is_active == True)
            elif status == 'CANCELLED':
                query = query.filter(Schedule.is_active == False)
        else:
            # Default to active schedules unless explicitly filtered
            query = query.filter(Schedule.is_active == True)
            
        # Filter by crop if specified
        if crop_id:
            query = query.filter(Schedule.crop_id == crop_id)
            
        # Filter by FSP if specified
        if fsp_id:
            from app.models.organization import OrgMember
            # Find users who are members of the given FSP organization
            fsp_user_ids = self.db.query(OrgMember.user_id).filter(
                OrgMember.organization_id == fsp_id
            ).all()
            user_ids = [uid[0] for uid in fsp_user_ids]
            query = query.filter(Schedule.created_by.in_(user_ids))
        
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
        
        # Populate computed fields for response schema
        for schedule in schedules:
            # 0. Populate task counts for list view
            from app.models.schedule import ScheduleTask
            schedule.total_tasks = self.db.query(func.count(ScheduleTask.id)).filter(ScheduleTask.schedule_id == schedule.id).scalar()
            schedule.completed_tasks = self.db.query(func.count(ScheduleTask.id)).filter(
                ScheduleTask.schedule_id == schedule.id,
                ScheduleTask.status == TaskStatus.COMPLETED
            ).scalar()

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

    def get_schedule_with_details(self, user: User, schedule_id: UUID) -> ScheduleWithTasksResponse:
        """
        Get single schedule with all details populated.
        
        Populates extra fields: input_item_name, application_method_name, total_quantity_required, dosage, area
        """
        schedule = self.db.query(Schedule).filter(
            Schedule.id == schedule_id,
            Schedule.is_active == True
        ).first()

        if not schedule:
            raise NotFoundError(
                message=f"Schedule {schedule_id} not found",
                error_code="SCHEDULE_NOT_FOUND"
            )

        # Populate computed fields
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

        # Convert to Pydantic model
        response = ScheduleWithTasksResponse.from_orm(schedule)
        
        # --- 1. Populate Area Details ---
        area_unit_id = None
        if schedule.template_parameters and isinstance(schedule.template_parameters, dict):
            params = schedule.template_parameters
            
            # Extract Area
            # Priority: area (common) > total_acres (legacy) > total_plants (legacy/count)
            if 'area' in params:
                 response.area = float(params['area'])
                 area_unit_id = params.get('area_unit_id')
            elif 'total_acres' in params:
                 response.area = float(params['total_acres'])
                 # Implicitly acre? Should check if unit ID exists
                 area_unit_id = params.get('area_unit_id')
            elif 'total_plants' in params:
                 response.area = float(params['total_plants'])
                 # Implicitly count?
                 
            # Fallback for unit ID if not in params but we found area
            if not area_unit_id and response.area:
                 # Try to infer or leave null. We need to fetch unit name later.
                 pass

        # --- 2. Collect IDs for Bulk Fetch ---
        input_item_ids = set()
        method_ids = set()
        unit_ids = set()
        
        if area_unit_id:
            unit_ids.add(area_unit_id)
            
        task_data_map = {} # task_id -> {input_item_id, method_id, quantity, dosage_info}
        
        # CRITICAL FIX: If schedule has a template, fetch template tasks for fallback
        template_task_map = {}
        if schedule.template_id:
            from app.models.schedule_template import ScheduleTemplateTask
            template_tasks = self.db.query(ScheduleTemplateTask).filter(
                ScheduleTemplateTask.schedule_template_id == schedule.template_id
            ).all()
            
            for tt in template_tasks:
                template_task_map[str(tt.task_id)] = tt
        
        for task in response.tasks:
            details = task.task_details or {}
            
            # CRITICAL FIX: If task_details is empty, try to get from template
            if not details and str(task.task_id) in template_task_map:
                template_task = template_task_map[str(task.task_id)]
                template_details = template_task.task_details_template or {}
                
                # Also fetch task_name from template if missing from schedule_task
                if not task.task_name:
                     task.task_name = template_task.task_name
                
                # Calculate the details using the same service used during creation
                try:
                    details = self.calculation_service.calculate_task_quantities(
                        template_details,
                        schedule.template_parameters or {}
                    )
                except Exception as e:
                    logger.warning(f"Failed to calculate task quantities from template: {e}")
                    details = template_details  # Use template as-is if calculation fails
            
            # Final fallback for task_name if still null (for old schedules or missing template name)
            if not task.task_name:
                # Find the matching ORM task to get its display_task_name (which handles fallback to task type name)
                orm_task = next((t for t in schedule.tasks if t.id == task.id), None)
                if orm_task:
                    task.task_name = orm_task.display_task_name
                else:
                    task.task_name = "Generic Task"
            
            # Data structure to hold extraction results
            extracted = {
                 'input_item_id': None,
                 'method_id': None,
                 'quantity': None,
                 'dosage_raw': None
            }

            # Check input_items
            if 'input_items' in details and isinstance(details['input_items'], list) and details['input_items']:
                item = details['input_items'][0]
                extracted['input_item_id'] = item.get('input_item_id')
                extracted['quantity'] = item.get('quantity')
                extracted['method_id'] = item.get('application_method_id')
                extracted['dosage_raw'] = item.get('dosage')
                
                if item.get('quantity_unit_id'):
                     unit_ids.add(item.get('quantity_unit_id'))
                     
            # Check concentration
            elif 'concentration' in details and isinstance(details['concentration'], dict):
                conc = details['concentration']
                if 'ingredients' in conc and isinstance(conc['ingredients'], list) and conc['ingredients']:
                    ing = conc['ingredients'][0]
                    extracted['input_item_id'] = ing.get('input_item_id')
                    extracted['quantity'] = ing.get('total_quantity')
                    # Concentration doesn't usually have method_id in ingredient, use task root if available
                    if 'application_method_id' in details:
                         extracted['method_id'] = details['application_method_id']
                    
                    if ing.get('quantity_unit_id'):
                         unit_ids.add(ing.get('quantity_unit_id'))
            
            # Collect IDs
            if extracted['input_item_id']: input_item_ids.add(extracted['input_item_id'])
            if extracted['method_id']: method_ids.add(extracted['method_id'])
            
            task_data_map[task.id] = extracted
        
        # --- 3. Bulk Fetch Names & Units ---
        input_item_names = {}
        if input_item_ids:
            items = self.db.query(InputItem).filter(InputItem.id.in_(input_item_ids)).all()
            for item in items:
                name = item.code # Default
                if item.translations:
                    # Prefer English, fallback to first
                    for t in item.translations:
                        if t.language_code == 'en':
                            name = t.name
                            break
                    else:
                        name = item.translations[0].name
                input_item_names[str(item.id)] = name
                
        method_names = {}
        if method_ids:
            methods = self.db.query(ReferenceData).filter(ReferenceData.id.in_(method_ids)).all()
            for method in methods:
                 method_names[str(method.id)] = method.display_name
        
        unit_map = {} # id -> symbol (or code)
        if unit_ids:
             from app.models.measurement_unit import MeasurementUnit
             
             # Filter out non-UUID values to avoid database errors
             valid_unit_uuids = []
             for uid in unit_ids:
                  try:
                       if uid:
                            uuid.UUID(str(uid))
                            valid_unit_uuids.append(uid)
                  except ValueError:
                       # Likely a code like 'kg', 'L', etc.
                       pass
             
             if valid_unit_uuids:
                 units = self.db.query(MeasurementUnit).filter(MeasurementUnit.id.in_(valid_unit_uuids)).all()
                 for unit in units:
                      # Prefer symbol, fallback to code
                      unit_map[str(unit.id)] = unit.symbol or unit.code

        # --- 4. Populate Response ---
        
        # Populate Area Unit
        if area_unit_id and str(area_unit_id) in unit_map:
             response.area_unit = unit_map[str(area_unit_id)]
        
        for task in response.tasks:
            if task.id in task_data_map:
                data = task_data_map[task.id]
                
                # A. Input Item Name
                if data['input_item_id'] and str(data['input_item_id']) in input_item_names:
                    task.input_item_name = input_item_names[str(data['input_item_id'])]
                else:
                    # Fallback validation: User requested no nulls. 
                    if data['input_item_id']:
                         task.input_item_name = "Unknown Item" 
                    elif task.task_name:
                         # Use task name if available as a proxy for what's happening
                         task.input_item_name = task.task_name
                    else:
                         task.input_item_name = "Generic Task"

                # B. Task Name Fallback (already handled above, but double check)
                if not task.task_name or task.task_name in ["Generic Task", "Unknown Task"]:
                     if task.input_item_name and task.input_item_name not in ["Generic Task", "Unknown Item"]:
                          task.task_name = task.input_item_name
                     elif not task.task_name or task.task_name == "Generic Task":
                          # Fallback to model's display_task_name if possible
                          orm_task = next((t for t in schedule.tasks if t.id == task.id), None)
                          task.task_name = orm_task.display_task_name if orm_task else "Generic Task"
                          
                # Ultimate fallback for task_name if still not set
                if not task.task_name:
                    task.task_name = "Generic Task"

                # B. Application Method Name
                if data['method_id'] and str(data['method_id']) in method_names:
                    task.application_method_name = method_names[str(data['method_id'])]
                elif task.task_details and 'application_method_name' in task.task_details:
                     task.application_method_name = task.task_details['application_method_name']
                else:
                     # Strict validation fallback
                     task.application_method_name = "Manual Application" # Safe default
                
                # C. Dosage & Total Quantity Calculation
                # Structure: { amount: float, unit: str, per: str }
                
                dosage_raw = data.get('dosage_raw')
                dosage_obj = None
                
                # If dosage not in details, try to construct it from quantity if we have area?
                # Or extracting it is primary.
                if dosage_raw and isinstance(dosage_raw, dict):
                     amount = dosage_raw.get('amount') or dosage_raw.get('quantity')
                     unit_id = dosage_raw.get('unit_id') or dosage_raw.get('unit')
                     
                     if amount is not None:
                           # Try to get unit string: either from unit_map or use the raw ID/Code if it's already a string
                           unit_str = "Units"
                           if unit_id:
                                if str(unit_id) in unit_map:
                                    unit_str = unit_map[str(unit_id)]
                                elif isinstance(unit_id, str) and len(unit_id) < 10: # Likely a code like 'Kg' or 'L'
                                    unit_str = unit_id
                           
                           per_str = "Application" 
                           basis = None
                           if schedule.template_parameters:
                                basis = schedule.template_parameters.get('calculation_basis')
                           
                           # Fallback per_str from basis if not in dosage_raw
                           per_raw = dosage_raw.get('per')
                           if per_raw:
                                per_str = str(per_raw).capitalize()
                           elif basis == 'per_acre':
                                per_str = "Acre"
                           elif basis == 'per_plant':
                                per_str = "Plant"
                                
                           dosage_obj = {
                                "amount": float(amount),
                                "unit": unit_str,
                                "per": per_str
                           }
                           
                           # CRITICAL: Use Dosage model here, not dict, to match schema?
                           # Schema in Remote said 'Dosage', I locally used Dict in HEAD.
                           # I merged Schema to Option[Dosage].
                           # So I must ensure I assign a Dosage object or a dict that Pydantic can convert?
                           # Pydantic in response mode usually handles dict->model conversion if 'from_attributes=True' (orm_mode)
                           # But task is a Pydantic model here (from response.tasks).
                           # Wait, response.tasks comes from `ScheduleWithTasksResponse.from_orm(schedule)`.
                           # So `task` is a `ScheduleTaskResponse` object (Pydantic model).
                           # I should assign a `Dosage` object or compatible dict.
                           # The `ScheduleTaskResponse` schema (merged) expects `Optional[Dosage]`.
                           # So I should create a Dosage object or dict.
                           from app.schemas.schedule import Dosage
                           task.dosage = Dosage(**dosage_obj)

                # Calculate Total Quantity if missing but we have Dosage & Area
                if task.total_quantity_required is None and data['quantity'] is not None:
                     try:
                        task.total_quantity_required = float(data['quantity'])
                     except (ValueError, TypeError):
                        pass

                if task.total_quantity_required is None and dosage_obj and response.area:
                     # Calculate: Dosage * Area
                     try:
                          task.total_quantity_required = float(dosage_obj['amount']) * float(response.area)
                     except Exception:
                          pass
        
        # CRITICAL FIX: Sync items with tasks because from_orm creates separate copies
        # The frontend uses 'items', so it needs the updated task objects
        response.items = response.tasks
        
        return response
    
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
                task_name=source_task.task_name, # Copy custom/overridden task name
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
