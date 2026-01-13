"""
Task Actual Pydantic schemas for Uzhathunai v2.0.

Schemas for task actual recording (planned and adhoc) with validation.
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator


# Task Details Schemas (JSONB structures)

class InputItemDetail(BaseModel):
    """Input item detail in task_details."""
    input_item_id: UUID
    quantity: float = Field(..., gt=0)
    quantity_unit_id: UUID


class LaborDetail(BaseModel):
    """Labor detail in task_details."""
    estimated_hours: Optional[float] = Field(None, gt=0)
    actual_hours: Optional[float] = Field(None, gt=0)
    worker_count: Optional[int] = Field(None, gt=0)


class MachineryDetail(BaseModel):
    """Machinery detail in task_details."""
    equipment_type: str
    estimated_hours: Optional[float] = Field(None, gt=0)
    actual_hours: Optional[float] = Field(None, gt=0)


class ConcentrationIngredient(BaseModel):
    """Ingredient in concentration detail."""
    input_item_id: UUID
    total_quantity: float = Field(..., gt=0)
    quantity_unit_id: UUID
    concentration_per_liter: float = Field(..., gt=0)


class ConcentrationDetail(BaseModel):
    """Concentration detail in task_details."""
    total_solution_volume: float = Field(..., gt=0)
    total_solution_volume_unit_id: UUID
    ingredients: List[ConcentrationIngredient]


class TaskDetailsSchema(BaseModel):
    """Task details JSONB structure."""
    input_items: Optional[List[InputItemDetail]] = None
    labor: Optional[LaborDetail] = None
    machinery: Optional[MachineryDetail] = None
    concentration: Optional[ConcentrationDetail] = None


# Task Actual Schemas

class PlannedTaskActualCreate(BaseModel):
    """Schema for creating planned task actual."""
    schedule_task_id: UUID
    actual_date: date
    task_details: dict  # JSONB structure
    notes: Optional[str] = None
    
    @validator('actual_date')
    def validate_actual_date(cls, v):
        """Validate actual_date is not in future."""
        if v > date.today():
            raise ValueError('Actual date cannot be in the future')
        return v


class AdhocTaskActualCreate(BaseModel):
    """Schema for creating adhoc task actual."""
    task_id: UUID
    crop_id: Optional[UUID] = None
    plot_id: Optional[UUID] = None
    actual_date: date
    task_details: dict  # JSONB structure
    notes: Optional[str] = None
    
    @validator('actual_date')
    def validate_actual_date(cls, v):
        """Validate actual_date is not in future."""
        if v > date.today():
            raise ValueError('Actual date cannot be in the future')
        return v
    
    @validator('crop_id', always=True)
    def validate_resource(cls, v, values):
        """Validate at least one of crop_id or plot_id is provided."""
        if not v and not values.get('plot_id'):
            raise ValueError('Either crop_id or plot_id must be provided')
        return v


class TaskPhotoCreate(BaseModel):
    """Schema for uploading task photo."""
    file_url: str = Field(..., max_length=500)
    file_key: str = Field(..., max_length=500)
    caption: Optional[str] = None


class TaskPhotoResponse(BaseModel):
    """Schema for task photo response."""
    id: UUID
    task_actual_id: UUID
    file_url: str
    file_key: str
    caption: Optional[str]
    uploaded_at: datetime
    uploaded_by: UUID
    
    class Config:
        orm_mode = True


class TaskActualResponse(BaseModel):
    """Schema for task actual response."""
    id: UUID
    schedule_id: Optional[UUID]
    schedule_task_id: Optional[UUID]
    task_id: UUID
    is_planned: bool
    crop_id: Optional[UUID]
    plot_id: Optional[UUID]
    actual_date: date
    task_details: dict
    notes: Optional[str]
    created_at: datetime
    created_by: UUID
    photos: List[TaskPhotoResponse] = []
    
    class Config:
        orm_mode = True


# Schedule Change Log Schemas

class ScheduleChangeLogResponse(BaseModel):
    """Schema for schedule change log response."""
    id: UUID
    schedule_id: UUID
    task_id: Optional[UUID]
    trigger_type: str
    trigger_reference_id: Optional[UUID]
    change_type: str
    task_details_before: Optional[dict]
    task_details_after: Optional[dict]
    change_description: Optional[str]
    is_applied: bool
    applied_at: Optional[datetime]
    applied_by: Optional[UUID]
    created_at: datetime
    created_by: UUID
    
    class Config:
        orm_mode = True


class ApplyProposedChangesRequest(BaseModel):
    """Schema for applying proposed changes."""
    change_log_ids: List[UUID] = Field(..., min_items=1)
    
    @validator('change_log_ids')
    def validate_unique_ids(cls, v):
        """Validate change_log_ids are unique."""
        if len(v) != len(set(v)):
            raise ValueError('change_log_ids must be unique')
        return v
