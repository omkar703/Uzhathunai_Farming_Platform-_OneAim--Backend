"""
Schedule Template schemas for Uzhathunai v2.0.
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import UUID


# Translation schemas
class ScheduleTemplateTranslationBase(BaseModel):
    """Base schema for schedule template translation."""
    language_code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ScheduleTemplateTranslationCreate(ScheduleTemplateTranslationBase):
    """Schema for creating schedule template translation."""
    pass


class ScheduleTemplateTranslationResponse(ScheduleTemplateTranslationBase):
    """Schema for schedule template translation response."""
    id: UUID
    schedule_template_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


# Template Task schemas
class ScheduleTemplateTaskBase(BaseModel):
    """Base schema for schedule template task."""
    task_id: Optional[UUID] = None
    task_name: Optional[str] = Field(None, max_length=200, description="Custom task name overriding the default")
    day_offset: int = Field(..., ge=0, description="Days from schedule start (0 = start date)")
    task_details_template: Dict[str, Any] = Field(..., description="JSONB with calculation formulas")
    sort_order: Optional[int] = Field(0, ge=0)
    notes: Optional[str] = None
    
    @validator('day_offset')
    def validate_day_offset(cls, v):
        """Validate day_offset is non-negative."""
        if v < 0:
            raise ValueError('day_offset must be non-negative')
        return v
    
        return v
    
    @validator('task_details_template')
    def validate_task_details_template(cls, v):
        """Validate task_details_template structure."""
        if not isinstance(v, dict):
            raise ValueError('task_details_template must be a dictionary')
        
        valid_calculation_basis = ['per_acre', 'per_plant', 'fixed']
        valid_dosage_per = ['ACRE', 'PLANT', 'LITER_WATER']
        
        # Validate input_items if present
        if 'input_items' in v:
            if not isinstance(v['input_items'], list):
                raise ValueError('input_items must be a list')
            
            for item in v['input_items']:
                # Support old calculation_basis
                if 'calculation_basis' in item and item['calculation_basis'] not in valid_calculation_basis:
                    raise ValueError(f"Invalid calculation_basis: {item['calculation_basis']}")
                
                # Support new dosage object
                if 'dosage' in item:
                    dosage = item['dosage']
                    if not isinstance(dosage, dict):
                        raise ValueError('dosage must be a dictionary')
                    
                    if 'amount' not in dosage:
                        raise ValueError('dosage missing amount')
                    
                    if 'per' in dosage and dosage['per'] not in valid_dosage_per:
                        raise ValueError(f"Invalid dosage per: {dosage['per']}")
        
        # Validate labor if present
        if 'labor' in v:
            if 'calculation_basis' in v['labor'] and v['labor']['calculation_basis'] not in valid_calculation_basis:
                raise ValueError(f"Invalid calculation_basis: {v['labor']['calculation_basis']}")
        
        # Validate machinery if present
        if 'machinery' in v:
            if 'calculation_basis' in v['machinery'] and v['machinery']['calculation_basis'] not in valid_calculation_basis:
                raise ValueError(f"Invalid calculation_basis: {v['machinery']['calculation_basis']}")
        
        # Validate concentration if present
        if 'concentration' in v:
            if 'calculation_basis' in v['concentration'] and v['concentration']['calculation_basis'] not in valid_calculation_basis:
                raise ValueError(f"Invalid calculation_basis: {v['concentration']['calculation_basis']}")
        
        return v


class ScheduleTemplateTaskCreate(ScheduleTemplateTaskBase):
    """Schema for creating schedule template task."""
    task_id: Optional[UUID] = None  # Make optional, will be inferred if missing


class ScheduleTemplateTaskUpdate(BaseModel):
    """Schema for updating schedule template task."""
    task_id: Optional[UUID] = None
    day_offset: Optional[int] = Field(None, ge=0)
    task_details_template: Optional[Dict[str, Any]] = None
    sort_order: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    
    @validator('day_offset')
    def validate_day_offset(cls, v):
        """Validate day_offset is non-negative."""
        if v is not None and v < 0:
            raise ValueError('day_offset must be non-negative')
        return v


class ScheduleTemplateTaskResponse(ScheduleTemplateTaskBase):
    """Schema for schedule template task response."""
    id: UUID
    schedule_template_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


# Template schemas
class ScheduleTemplateBase(BaseModel):
    """Base schema for schedule template."""
    name: Optional[str] = Field(None, description="Name (maps to default translation)")
    description: Optional[str] = Field(None, description="Description (maps to default translation)")
    code: str = Field(..., min_length=1, max_length=50)
    crop_type_id: Optional[UUID] = None
    crop_variety_id: Optional[UUID] = None
    is_system_defined: bool = False
    owner_org_id: Optional[UUID] = None
    notes: Optional[str] = None


class ScheduleTemplateCreate(ScheduleTemplateBase):
    """Schema for creating schedule template."""
    translations: Optional[List[ScheduleTemplateTranslationCreate]] = None
    tasks: Optional[List[ScheduleTemplateTaskCreate]] = None
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code is not empty."""
        if not v.strip():
            raise ValueError('code cannot be empty')
        return v.strip()


class ScheduleTemplateUpdate(BaseModel):
    """Schema for updating schedule template."""
    name: Optional[str] = Field(None, description="Name (maps to default translation)")
    description: Optional[str] = Field(None, description="Description (maps to default translation)")
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    crop_type_id: Optional[UUID] = None
    crop_variety_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    translations: Optional[List[ScheduleTemplateTranslationCreate]] = None
    tasks: Optional[List[ScheduleTemplateTaskCreate]] = None
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code is not empty."""
        if v is not None and not v.strip():
            raise ValueError('code cannot be empty')
        return v.strip() if v else v


class ScheduleTemplateCopy(BaseModel):
    """Schema for copying schedule template."""
    new_code: str = Field(..., min_length=1, max_length=50)
    is_system_defined: Optional[bool] = None
    
    @validator('new_code')
    def validate_new_code(cls, v):
        """Validate new_code is not empty."""
        if not v.strip():
            raise ValueError('new_code cannot be empty')
        return v.strip()


class ScheduleTemplateResponse(ScheduleTemplateBase):
    """Schema for schedule template response."""
    id: UUID
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    translations: List[ScheduleTemplateTranslationResponse] = []
    tasks: List[ScheduleTemplateTaskResponse] = []
    duration_days: int = 0
    
    @validator('duration_days', always=True)
    def calculate_duration_days(cls, v, values):
        """Calculate duration from tasks."""
        tasks = values.get('tasks', [])
        if not tasks:
            return 0
        return max((t.day_offset for t in tasks), default=0)
    
    class Config:
        from_attributes = True


class ScheduleTemplateListResponse(BaseModel):
    """Schema for schedule template list response with pagination."""
    items: List[ScheduleTemplateResponse]
    total: int
    page: int
    limit: int
    total_pages: int
