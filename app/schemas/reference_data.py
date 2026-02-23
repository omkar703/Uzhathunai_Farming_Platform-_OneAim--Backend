"""
Reference Data and Task schemas for Uzhathunai v2.0.

Schemas for tasks and general reference data.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from app.models.enums import TaskCategory


class TaskTranslationResponse(BaseModel):
    """Schema for task translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Schema for task response."""
    id: str
    code: str
    category: TaskCategory
    requires_input_items: bool
    requires_concentration: bool
    requires_machinery: bool
    requires_labor: bool
    sort_order: int
    is_active: bool
    translations: list[TaskTranslationResponse] = Field(default_factory=list)
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class TaskTranslationCreate(BaseModel):
    """Schema for creating a task translation."""
    language_code: str
    name: str
    description: Optional[str] = None


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    code: str
    category: TaskCategory = TaskCategory.FARMING
    requires_input_items: bool = False
    requires_concentration: bool = False
    requires_machinery: bool = False
    requires_labor: bool = False
    sort_order: int = 0
    is_active: bool = True
    translations: list[TaskTranslationCreate] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    code: Optional[str] = None
    category: Optional[TaskCategory] = None
    requires_input_items: Optional[bool] = None
    requires_concentration: Optional[bool] = None
    requires_machinery: Optional[bool] = None
    requires_labor: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    translations: Optional[list[TaskTranslationCreate]] = None


class ReferenceDataTypeResponse(BaseModel):
    """Schema for reference data type response."""
    id: str
    code: str
    name: str
    description: Optional[str]
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class ReferenceMetadata(BaseModel):
    """Schema for reference data metadata structure."""
    capacity_liters: Optional[int] = Field(None, description="Capacity in liters (for water sources)")
    depth_meters: Optional[float] = Field(None, description="Depth in meters (for wells, borewells)")
    water_quality: Optional[str] = Field(None, description="Water quality (GOOD, MODERATE, POOR)")
    seasonal_availability: Optional[str] = Field(None, description="Seasonal availability")
    maintenance_requirements: Optional[str] = Field(None, description="Maintenance requirements")
    
    class Config:
        extra = "allow"  # Allow additional fields


class ReferenceDataTranslationResponse(BaseModel):
    """Schema for reference data translation response."""
    language_code: str
    display_name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class ReferenceDataResponse(BaseModel):
    """Schema for reference data response."""
    id: str
    type_id: str
    code: str
    sort_order: int
    is_active: bool
    reference_metadata: Optional[Dict[str, Any]] = Field(None, description="Reference metadata (capacity, depth, water quality, etc.)")
    translations: list[ReferenceDataTranslationResponse] = Field(default_factory=list)
    
    @validator('id', 'type_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class ApplicationMethodResponse(BaseModel):
    """Schema for application method response."""
    id: str
    name: str
    requires_concentration: bool
    
    class Config:
        from_attributes = True
