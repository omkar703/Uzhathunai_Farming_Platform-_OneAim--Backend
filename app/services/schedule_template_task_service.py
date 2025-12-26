"""
Schedule Template Task service for Uzhathunai v2.0.
Handles schedule template task management with validation.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.schedule_template import ScheduleTemplateTask, ScheduleTemplate
from app.models.user import User
from app.schemas.schedule_template import ScheduleTemplateTaskCreate, ScheduleTemplateTaskUpdate
from app.core.logging import get_logger
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    PermissionError
)

logger = get_logger(__name__)


class ScheduleTemplateTaskService:
    """Service for schedule template task management."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
    
    def validate_task_details_template(self, task_details_template: dict) -> None:
        """
        Validate JSONB structure for task_details_template.
        
        Requirements 4.8, 4.9, 4.10, 4.11, 4.12:
        - Validates input_items structure with calculation_basis
        - Validates labor structure with calculation_basis
        - Validates machinery structure with calculation_basis
        - Validates concentration structure with ingredients
        
        Args:
            task_details_template: JSONB task details template
        
        Raises:
            ValidationError: If structure is invalid
        """
        self.logger.info("Validating task_details_template structure")
        
        if not isinstance(task_details_template, dict):
            raise ValidationError(
                message="task_details_template must be a dictionary",
                error_code="INVALID_TASK_DETAILS_TEMPLATE"
            )
        
        valid_calculation_basis = ['per_acre', 'per_plant', 'fixed']
        
        # Validate input_items if present
        if 'input_items' in task_details_template:
            if not isinstance(task_details_template['input_items'], list):
                raise ValidationError(
                    message="input_items must be a list",
                    error_code="INVALID_INPUT_ITEMS"
                )
            
            for item in task_details_template['input_items']:
                if not isinstance(item, dict):
                    raise ValidationError(
                        message="Each input_item must be a dictionary",
                        error_code="INVALID_INPUT_ITEM"
                    )
                
                # Required fields
                required_fields = ['input_item_id', 'quantity', 'quantity_unit_id', 'calculation_basis']
                for field in required_fields:
                    if field not in item:
                        raise ValidationError(
                            message=f"input_item missing required field: {field}",
                            error_code="MISSING_INPUT_ITEM_FIELD",
                            details={"field": field}
                        )
                
                # Validate calculation_basis
                if item['calculation_basis'] not in valid_calculation_basis:
                    raise ValidationError(
                        message=f"Invalid calculation_basis: {item['calculation_basis']}",
                        error_code="INVALID_CALCULATION_BASIS",
                        details={"valid_values": valid_calculation_basis}
                    )
                
                # Validate quantity is positive
                if not isinstance(item['quantity'], (int, float)) or item['quantity'] <= 0:
                    raise ValidationError(
                        message="quantity must be a positive number",
                        error_code="INVALID_QUANTITY"
                    )
        
        # Validate labor if present
        if 'labor' in task_details_template:
            labor = task_details_template['labor']
            if not isinstance(labor, dict):
                raise ValidationError(
                    message="labor must be a dictionary",
                    error_code="INVALID_LABOR"
                )
            
            # Required fields
            if 'estimated_hours' not in labor:
                raise ValidationError(
                    message="labor missing required field: estimated_hours",
                    error_code="MISSING_LABOR_FIELD"
                )
            
            if 'calculation_basis' not in labor:
                raise ValidationError(
                    message="labor missing required field: calculation_basis",
                    error_code="MISSING_LABOR_FIELD"
                )
            
            # Validate calculation_basis
            if labor['calculation_basis'] not in valid_calculation_basis:
                raise ValidationError(
                    message=f"Invalid calculation_basis: {labor['calculation_basis']}",
                    error_code="INVALID_CALCULATION_BASIS",
                    details={"valid_values": valid_calculation_basis}
                )
            
            # Validate estimated_hours is positive
            if not isinstance(labor['estimated_hours'], (int, float)) or labor['estimated_hours'] <= 0:
                raise ValidationError(
                    message="estimated_hours must be a positive number",
                    error_code="INVALID_ESTIMATED_HOURS"
                )
        
        # Validate machinery if present
        if 'machinery' in task_details_template:
            machinery = task_details_template['machinery']
            if not isinstance(machinery, dict):
                raise ValidationError(
                    message="machinery must be a dictionary",
                    error_code="INVALID_MACHINERY"
                )
            
            # Required fields
            required_fields = ['equipment_type', 'estimated_hours', 'calculation_basis']
            for field in required_fields:
                if field not in machinery:
                    raise ValidationError(
                        message=f"machinery missing required field: {field}",
                        error_code="MISSING_MACHINERY_FIELD",
                        details={"field": field}
                    )
            
            # Validate calculation_basis
            if machinery['calculation_basis'] not in valid_calculation_basis:
                raise ValidationError(
                    message=f"Invalid calculation_basis: {machinery['calculation_basis']}",
                    error_code="INVALID_CALCULATION_BASIS",
                    details={"valid_values": valid_calculation_basis}
                )
            
            # Validate estimated_hours is positive
            if not isinstance(machinery['estimated_hours'], (int, float)) or machinery['estimated_hours'] <= 0:
                raise ValidationError(
                    message="estimated_hours must be a positive number",
                    error_code="INVALID_ESTIMATED_HOURS"
                )
        
        # Validate concentration if present
        if 'concentration' in task_details_template:
            concentration = task_details_template['concentration']
            if not isinstance(concentration, dict):
                raise ValidationError(
                    message="concentration must be a dictionary",
                    error_code="INVALID_CONCENTRATION"
                )
            
            # Required fields
            required_fields = ['solution_volume', 'solution_volume_unit_id', 'calculation_basis', 'ingredients']
            for field in required_fields:
                if field not in concentration:
                    raise ValidationError(
                        message=f"concentration missing required field: {field}",
                        error_code="MISSING_CONCENTRATION_FIELD",
                        details={"field": field}
                    )
            
            # Validate calculation_basis
            if concentration['calculation_basis'] not in valid_calculation_basis:
                raise ValidationError(
                    message=f"Invalid calculation_basis: {concentration['calculation_basis']}",
                    error_code="INVALID_CALCULATION_BASIS",
                    details={"valid_values": valid_calculation_basis}
                )
            
            # Validate solution_volume is positive
            if not isinstance(concentration['solution_volume'], (int, float)) or concentration['solution_volume'] <= 0:
                raise ValidationError(
                    message="solution_volume must be a positive number",
                    error_code="INVALID_SOLUTION_VOLUME"
                )
            
            # Validate ingredients
            if not isinstance(concentration['ingredients'], list):
                raise ValidationError(
                    message="ingredients must be a list",
                    error_code="INVALID_INGREDIENTS"
                )
            
            if len(concentration['ingredients']) == 0:
                raise ValidationError(
                    message="ingredients list cannot be empty",
                    error_code="EMPTY_INGREDIENTS"
                )
            
            for ingredient in concentration['ingredients']:
                if not isinstance(ingredient, dict):
                    raise ValidationError(
                        message="Each ingredient must be a dictionary",
                        error_code="INVALID_INGREDIENT"
                    )
                
                # Required fields
                required_fields = ['input_item_id', 'concentration_per_liter', 'concentration_unit_id']
                for field in required_fields:
                    if field not in ingredient:
                        raise ValidationError(
                            message=f"ingredient missing required field: {field}",
                            error_code="MISSING_INGREDIENT_FIELD",
                            details={"field": field}
                        )
                
                # Validate concentration_per_liter is positive
                if not isinstance(ingredient['concentration_per_liter'], (int, float)) or ingredient['concentration_per_liter'] <= 0:
                    raise ValidationError(
                        message="concentration_per_liter must be a positive number",
                        error_code="INVALID_CONCENTRATION_PER_LITER"
                    )
        
        self.logger.info("task_details_template validation passed")
    
    def create_template_task(
        self,
        template_id: UUID,
        user_id: UUID,
        data: ScheduleTemplateTaskCreate
    ) -> ScheduleTemplateTask:
        """
        Create template task with day_offset and formulas.
        
        Requirements 4.7, 4.8, 4.9, 4.10, 4.11, 4.12:
        - Validates day_offset is non-negative
        - Validates task_details_template structure
        - Supports calculation_basis for all components
        
        Args:
            template_id: Template ID
            user_id: User ID
            data: Task data
        
        Returns:
            Created template task
        
        Raises:
            NotFoundError: If template not found
            ValidationError: If data is invalid
            PermissionError: If user cannot modify template
        """
        self.logger.info(
            "Creating template task",
            extra={
                "template_id": str(template_id),
                "user_id": str(user_id),
                "day_offset": data.day_offset
            }
        )
        
        # Get template and validate ownership
        from app.services.schedule_template_service import ScheduleTemplateService
        template_service = ScheduleTemplateService(self.db)
        template, can_modify = template_service.validate_template_ownership(template_id, user_id)
        
        # Validate day_offset is non-negative
        if data.day_offset < 0:
            raise ValidationError(
                message="day_offset must be non-negative",
                error_code="INVALID_DAY_OFFSET",
                details={"day_offset": data.day_offset}
            )
        
        # Validate task_details_template structure
        self.validate_task_details_template(data.task_details_template)
        
        try:
            # Create template task
            template_task = ScheduleTemplateTask(
                schedule_template_id=template_id,
                task_id=data.task_id,
                day_offset=data.day_offset,
                task_details_template=data.task_details_template,
                sort_order=data.sort_order if data.sort_order is not None else 0,
                notes=data.notes,
                created_by=user_id,
                updated_by=user_id
            )
            
            self.db.add(template_task)
            self.db.commit()
            self.db.refresh(template_task)
            
            self.logger.info(
                "Template task created successfully",
                extra={
                    "template_task_id": str(template_task.id),
                    "template_id": str(template_id),
                    "day_offset": template_task.day_offset,
                    "user_id": str(user_id)
                }
            )
            
            return template_task
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to create template task",
                extra={
                    "template_id": str(template_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def update_template_task(
        self,
        task_id: UUID,
        user_id: UUID,
        data: ScheduleTemplateTaskUpdate
    ) -> ScheduleTemplateTask:
        """
        Update template task.
        
        Args:
            task_id: Template task ID
            user_id: User ID
            data: Update data
        
        Returns:
            Updated template task
        
        Raises:
            NotFoundError: If template task not found
            ValidationError: If data is invalid
            PermissionError: If user cannot modify template
        """
        self.logger.info(
            "Updating template task",
            extra={
                "task_id": str(task_id),
                "user_id": str(user_id)
            }
        )
        
        # Get template task
        template_task = self.db.query(ScheduleTemplateTask).filter(
            ScheduleTemplateTask.id == task_id
        ).first()
        
        if not template_task:
            raise NotFoundError(
                message="Template task not found",
                error_code="TEMPLATE_TASK_NOT_FOUND"
            )
        
        # Validate ownership
        from app.services.schedule_template_service import ScheduleTemplateService
        template_service = ScheduleTemplateService(self.db)
        template, can_modify = template_service.validate_template_ownership(
            template_task.schedule_template_id,
            user_id
        )
        
        # Validate day_offset if provided
        if data.day_offset is not None and data.day_offset < 0:
            raise ValidationError(
                message="day_offset must be non-negative",
                error_code="INVALID_DAY_OFFSET",
                details={"day_offset": data.day_offset}
            )
        
        # Validate task_details_template if provided
        if data.task_details_template is not None:
            self.validate_task_details_template(data.task_details_template)
        
        try:
            # Update fields
            update_data = data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(template_task, field, value)
            
            template_task.updated_by = user_id
            template_task.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(template_task)
            
            self.logger.info(
                "Template task updated successfully",
                extra={
                    "task_id": str(task_id),
                    "user_id": str(user_id)
                }
            )
            
            return template_task
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to update template task",
                extra={
                    "task_id": str(task_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def get_template_tasks(
        self,
        template_id: UUID
    ) -> List[ScheduleTemplateTask]:
        """
        Get all tasks for a template.
        
        Args:
            template_id: Template ID
        
        Returns:
            List of template tasks ordered by sort_order and day_offset
        """
        self.logger.info(
            "Fetching template tasks",
            extra={"template_id": str(template_id)}
        )
        
        tasks = self.db.query(ScheduleTemplateTask).filter(
            ScheduleTemplateTask.schedule_template_id == template_id
        ).order_by(
            ScheduleTemplateTask.sort_order,
            ScheduleTemplateTask.day_offset
        ).all()
        
        self.logger.info(
            "Template tasks fetched",
            extra={
                "template_id": str(template_id),
                "count": len(tasks)
            }
        )
        
        return tasks
    
    def delete_template_task(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> None:
        """
        Delete template task.
        
        Args:
            task_id: Template task ID
            user_id: User ID
        
        Raises:
            NotFoundError: If template task not found
            PermissionError: If user cannot modify template
        """
        self.logger.info(
            "Deleting template task",
            extra={
                "task_id": str(task_id),
                "user_id": str(user_id)
            }
        )
        
        # Get template task
        template_task = self.db.query(ScheduleTemplateTask).filter(
            ScheduleTemplateTask.id == task_id
        ).first()
        
        if not template_task:
            raise NotFoundError(
                message="Template task not found",
                error_code="TEMPLATE_TASK_NOT_FOUND"
            )
        
        # Validate ownership
        from app.services.schedule_template_service import ScheduleTemplateService
        template_service = ScheduleTemplateService(self.db)
        template, can_modify = template_service.validate_template_ownership(
            template_task.schedule_template_id,
            user_id
        )
        
        try:
            self.db.delete(template_task)
            self.db.commit()
            
            self.logger.info(
                "Template task deleted successfully",
                extra={
                    "task_id": str(task_id),
                    "user_id": str(user_id)
                }
            )
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(
                "Failed to delete template task",
                extra={
                    "task_id": str(task_id),
                    "user_id": str(user_id),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
