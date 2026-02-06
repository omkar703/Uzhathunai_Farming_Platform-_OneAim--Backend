"""
Schedule schemas for Uzhathunai v2.0.

Pydantic schemas for schedule creation and responses.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from uuid import UUID

from app.models.enums import TaskStatus


class ScheduleFromTemplateCreate(BaseModel):
    """
    Schema for creating schedule from template.
    
    Validates: Requirement 6.5, 6.6
    """
    crop_id: UUID = Field(..., description="Target crop ID")
    template_id: UUID = Field(..., description="Schedule template ID")
    name: str = Field(..., min_length=1, max_length=200, description="Schedule name")
    template_parameters: Dict[str, Any] = Field(..., description="Template parameters (start_date, area, plant_count)")
    
    @validator('template_parameters')
    def validate_template_parameters(cls, v):
        """Validate template_parameters structure."""
        if not isinstance(v, dict):
            raise ValueError("template_parameters must be a dictionary")
        
        # start_date is always required (Requirement 6.6)
        if 'start_date' not in v:
            raise ValueError("start_date is required in template_parameters")
        
        # Validate start_date format
        try:
            date.fromisoformat(v['start_date'])
        except (ValueError, TypeError):
            raise ValueError("start_date must be in ISO format (YYYY-MM-DD)")
        
        # Support both old (area/plant_count) and new (total_acres/total_plants) parameters
        # Ensure units are provided if needed
        if 'area' in v and 'area_unit_id' not in v:
            raise ValueError("area_unit_id is required when area is provided")
        
        if 'area_unit_id' in v and 'area' not in v:
            raise ValueError("area is required when area_unit_id is provided")

        # Optional: Verify numeric types for scaling factors
        numeric_fields = ['area', 'plant_count', 'total_acres', 'total_plants', 'water_liters']
        for field in numeric_fields:
            if field in v and not isinstance(v[field], (int, float)):
                 raise ValueError(f"{field} must be a number")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "123e4567-e89b-12d3-a456-426614174000",
                "template_id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Tomato Schedule - Plot A",
                "template_parameters": {
                    "start_date": "2024-10-01",
                    "area": 2.5,
                    "area_unit_id": "123e4567-e89b-12d3-a456-426614174002",
                    "plant_count": 800
                }
            }
        }


class ScheduleFromScratchCreate(BaseModel):
    """
    Schema for creating schedule from scratch.
    
    Validates: Requirement 7.4
    """
    crop_id: UUID = Field(..., description="Target crop ID")
    name: str = Field(..., min_length=1, max_length=200, description="Schedule name")
    description: Optional[str] = Field(None, description="Schedule description")
    start_date: Optional[date] = Field(None, description="Schedule start date (for reference)")
    template_parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters (area, plant_count) for reference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Custom Tomato Schedule",
                "description": "Custom schedule for experimental plot"
            }
        }


class ScheduleCopyRequest(BaseModel):
    """
    Schema for copying schedule.
    
    Validates: Requirement 8.3
    """
    target_crop_id: UUID = Field(..., description="Target crop ID")
    new_start_date: date = Field(..., description="Start date for new schedule")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_crop_id": "123e4567-e89b-12d3-a456-426614174000",
                "new_start_date": "2024-11-01"
            }
        }


class ScheduleTaskCreate(BaseModel):
    """
    Schema for creating schedule task.
    
    Validates: Requirement 7.6
    """
    task_id: UUID = Field(..., description="Task ID")
    due_date: date = Field(..., description="Task due date")
    task_details: Optional[Dict[str, Any]] = Field(None, description="Task details JSONB")
    notes: Optional[str] = Field(None, description="Task notes")
    
    @validator('task_details')
    def validate_task_details(cls, v):
        """Validate task_details structure."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError("task_details must be a dictionary")
        
        # Validate input_items structure (Requirement 7.7)
        if 'input_items' in v:
            if not isinstance(v['input_items'], list):
                raise ValueError("input_items must be a list")
            
            for item in v['input_items']:
                if not isinstance(item, dict):
                    raise ValueError("Each input_item must be a dictionary")
                
                required_fields = ['input_item_id', 'quantity', 'quantity_unit_id']
                for field in required_fields:
                    if field not in item:
                        raise ValueError(f"input_item missing required field: {field}")
        
        # Validate labor structure (Requirement 7.8)
        if 'labor' in v:
            if not isinstance(v['labor'], dict):
                raise ValueError("labor must be a dictionary")
            
            if 'estimated_hours' not in v['labor']:
                raise ValueError("labor missing required field: estimated_hours")
        
        # Validate machinery structure (Requirement 7.9)
        if 'machinery' in v:
            if not isinstance(v['machinery'], dict):
                raise ValueError("machinery must be a dictionary")
            
            required_fields = ['equipment_type', 'estimated_hours']
            for field in required_fields:
                if field not in v['machinery']:
                    raise ValueError(f"machinery missing required field: {field}")
        
        # Validate concentration structure (Requirement 7.10, 7.11)
        if 'concentration' in v:
            if not isinstance(v['concentration'], dict):
                raise ValueError("concentration must be a dictionary")
            
            required_fields = ['total_solution_volume', 'total_solution_volume_unit_id', 'ingredients']
            for field in required_fields:
                if field not in v['concentration']:
                    raise ValueError(f"concentration missing required field: {field}")
            
            if not isinstance(v['concentration']['ingredients'], list):
                raise ValueError("concentration ingredients must be a list")
            
            for ing in v['concentration']['ingredients']:
                required_ing_fields = ['input_item_id', 'total_quantity', 'quantity_unit_id', 'concentration_per_liter']
                for field in required_ing_fields:
                    if field not in ing:
                        raise ValueError(f"concentration ingredient missing required field: {field}")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "due_date": "2024-10-15",
                "task_details": {
                    "input_items": [
                        {
                            "input_item_id": "123e4567-e89b-12d3-a456-426614174001",
                            "quantity": 250,
                            "quantity_unit_id": "123e4567-e89b-12d3-a456-426614174002"
                        }
                    ],
                    "labor": {
                        "estimated_hours": 20,
                        "worker_count": 3
                    }
                },
                "notes": "Apply in morning hours"
            }
        }


class ScheduleTaskUpdate(BaseModel):
    """Schema for updating schedule task."""
    due_date: Optional[date] = Field(None, description="New due date")
    task_details: Optional[Dict[str, Any]] = Field(None, description="New task details")
    notes: Optional[str] = Field(None, description="New notes")
    
    @validator('task_details')
    def validate_task_details(cls, v):
        """Validate task_details structure."""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError("task_details must be a dictionary")
        
        return v


class ScheduleTaskStatusUpdate(BaseModel):
    """Schema for updating schedule task status."""
    status: TaskStatus = Field(..., description="New task status")
    completed_date: Optional[date] = Field(None, description="Completion date (required if status is COMPLETED)")
    
    @validator('completed_date', always=True)
    def validate_completed_date(cls, v, values):
        """Validate completed_date is provided when status is COMPLETED."""
        if 'status' in values and values['status'] == TaskStatus.COMPLETED:
            if v is None:
                # Will be set to today by service
                pass
        return v


class ScheduleTaskResponse(BaseModel):
    """Schema for schedule task response."""
    id: UUID
    schedule_id: UUID
    task_id: UUID
    due_date: date
    status: TaskStatus
    completed_date: Optional[date]
    task_details: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    scheduled_date: Optional[date] = None
    task_name: Optional[str] = None
    input_item_name: Optional[str] = None
    application_method_name: Optional[str] = None
    total_quantity_required: Optional[float] = None
    dosage: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    id: UUID
    crop_id: UUID
    template_id: Optional[UUID]
    name: str
    description: Optional[str]
    template_parameters: Optional[Dict[str, Any]]
    is_active: bool
    status: Optional[str] = None # Changed to str to allow 'ACTIVE'
    farm_name: Optional[str] = None
    crop_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    start_date: Optional[date] = None
    field_name: Optional[str] = None
    fsp_name: Optional[str] = None
    is_fsp_created: bool = False
    total_tasks: int = 0
    completed_tasks: int = 0
    area: Optional[float] = None
    area_unit: Optional[str] = None
    
    class Config:
        from_attributes = True

    @validator('farm_name', always=True, pre=True, check_fields=False)
    def get_farm_name(cls, v, values):
        # Handle ORM object access
        if v: return v
        # Access validation context or object if possible? 
        # Pydantic v1 with ORM mode is tricky for nested relationships if not loaded.
        # But we can try to rely on the object passed.
        # However, 'values' only contains already validated fields. 
        # The 'v' here is the value from the object attribute 'farm_name' which doesn't exist.
        return None

    # Actually, simpler approach for ORM computed fields in Pydantic v1/v2 compat:
    # We rely on the service to populate, OR we add properties to the Model.
    # For now, let's just add the fields so they CAN be returned.
    # status is on the model, so it will work.
    # farm_name/crop_name might need Backend Service update.


class ScheduleWithTasksResponse(BaseModel):
    """Schema for schedule with tasks response."""
    id: UUID
    crop_id: UUID
    template_id: Optional[UUID]
    name: str
    description: Optional[str]
    template_parameters: Optional[Dict[str, Any]]
    is_active: bool
    tasks: List[ScheduleTaskResponse]
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: UUID
    start_date: Optional[date] = None
    farm_name: Optional[str] = None
    crop_name: Optional[str] = None
    field_name: Optional[str] = None
    fsp_name: Optional[str] = None
    is_fsp_created: bool = False
    total_tasks: int = 0
    completed_tasks: int = 0
    items: Optional[List[ScheduleTaskResponse]] = None
    area: Optional[float] = None
    area_unit: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaginatedScheduleResponse(BaseModel):
    """Schema for paginated schedule response."""
    items: List[ScheduleResponse]
    total: int
    page: int
    limit: int
    total_pages: int

