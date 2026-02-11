"""
Crop schemas for Uzhathunai v2.0.

Schemas for crop CRUD operations, lifecycle management, yields, and photos.
"""
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.enums import CropLifecycle


class CropCreate(BaseModel):
    """Schema for creating crop."""
    plot_id: UUID = Field(..., description="Plot ID where crop will be planted")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    crop_type_id: Optional[UUID] = None
    crop_variety_id: Optional[UUID] = None
    variety_name: Optional[str] = Field(None, description="Variety name (alternative to crop_variety_id)")
    area: Optional[Decimal] = Field(None, ge=0)
    area_unit_id: Optional[UUID] = None
    plant_count: Optional[int] = Field(None, ge=0)
    planned_date: Optional[date] = None
    sowing_date: Optional[date] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('variety_name')
    def validate_variety_name(cls, v):
        """Validate variety_name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Variety name cannot be empty')
        return v.strip() if v else v


class CropUpdate(BaseModel):
    """Schema for updating crop."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    crop_type_id: Optional[UUID] = None
    crop_variety_id: Optional[UUID] = None
    area: Optional[Decimal] = Field(None, ge=0)
    area_unit_id: Optional[UUID] = None
    plant_count: Optional[int] = Field(None, ge=0)
    planted_date: Optional[date] = None
    
    # Frontend Aliases / Compatibility
    planted_area: Optional[Decimal] = Field(None, ge=0)
    sowing_date: Optional[date] = None
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v


class UpdateLifecycleRequest(BaseModel):
    """Schema for updating crop lifecycle."""
    new_lifecycle: CropLifecycle = Field(..., description="New lifecycle stage")


class CropTypeNested(BaseModel):
    """Nested crop type data for responses."""
    id: str
    code: str
    name: Optional[str]
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class CropVarietyNested(BaseModel):
    """Nested crop variety data for responses."""
    id: str
    code: str
    name: Optional[str]
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class CropResponse(BaseModel):
    """Schema for crop response."""
    id: str
    plot_id: str
    name: str
    description: Optional[str]
    crop_type_id: Optional[str]
    crop_variety_id: Optional[str]
    crop_type: Optional[CropTypeNested] = None
    crop_variety: Optional[CropVarietyNested] = None
    variety_name: Optional[str] = None # Added for custom variety names
    area: Optional[Decimal]
    area_unit_id: Optional[str]
    plant_count: Optional[int]
    lifecycle: CropLifecycle
    planned_date: Optional[date]
    planted_date: Optional[date]
    transplanted_date: Optional[date]
    production_start_date: Optional[date]
    completed_date: Optional[date]
    terminated_date: Optional[date]
    closed_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    # Validation Aliases for specific frontend requirements
    variety: Optional[CropVarietyNested] = Field(None, description="Alias for crop_variety")
    sowing_date: Optional[date] = Field(None, description="Alias for planted_date")
    status: Optional[str] = Field(None, description="Alias for lifecycle value")
    expected_harvest_date: Optional[date] = Field(None, description="Calculated harvest date")
    planted_area: Optional[Decimal] = Field(None, description="Alias for area")
    planned_area: Optional[Decimal] = Field(None, description="Alias for area")
    estimated_yield: Optional[float] = Field(None, description="Estimated yield")
    yield_unit: Optional[str] = Field(None, description="Unit for estimated yield")
    season: Optional[str] = Field(None, description="Calculated season (e.g. Kharif 2024)")
    
    @validator('id', 'plot_id', 'crop_type_id', 'crop_variety_id', 'area_unit_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class CropYieldCreate(BaseModel):
    """Schema for creating crop yield."""
    yield_type: str = Field(..., pattern="^(PLANNED|ACTUAL)$", description="Yield type (PLANNED or ACTUAL)")
    harvest_date: Optional[date] = Field(None, description="Harvest date (required for ACTUAL yields)")
    quantity: Decimal = Field(..., gt=0, description="Yield quantity")
    quantity_unit_id: UUID = Field(..., description="Quantity unit ID")
    harvest_area: Optional[Decimal] = Field(None, ge=0, description="Harvest area (optional for area-based yields)")
    harvest_area_unit_id: Optional[UUID] = Field(None, description="Harvest area unit ID")
    notes: Optional[str] = None
    
    @validator('harvest_date')
    def validate_harvest_date(cls, v, values):
        """Validate harvest date is required for ACTUAL yields."""
        if values.get('yield_type') == 'ACTUAL' and v is None:
            raise ValueError('Harvest date is required for ACTUAL yields')
        return v
    
    @validator('harvest_area_unit_id')
    def validate_harvest_area_unit(cls, v, values):
        """Validate harvest area and unit are both provided or both null."""
        harvest_area = values.get('harvest_area')
        if (harvest_area is None and v is not None) or (harvest_area is not None and v is None):
            raise ValueError('Harvest area and harvest area unit must both be provided or both be null')
        return v


class CropYieldUpdate(BaseModel):
    """Schema for updating crop yield."""
    harvest_date: Optional[date] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    quantity_unit_id: Optional[UUID] = None
    harvest_area: Optional[Decimal] = Field(None, ge=0)
    harvest_area_unit_id: Optional[UUID] = None
    notes: Optional[str] = None


class CropYieldResponse(BaseModel):
    """Schema for crop yield response."""
    id: str
    crop_id: str
    yield_type: str
    harvest_date: Optional[date]
    quantity: Decimal
    quantity_unit_id: str
    harvest_area: Optional[Decimal]
    harvest_area_unit_id: Optional[str]
    notes: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    
    @validator('id', 'crop_id', 'quantity_unit_id', 'harvest_area_unit_id', 'created_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class YieldComparisonResponse(BaseModel):
    """Schema for yield comparison response."""
    total_planned: Decimal
    total_actual: Decimal
    variance: Decimal
    variance_percentage: float
    achievement_rate: float
    planned_yields: list[CropYieldResponse]
    actual_yields: list[CropYieldResponse]


class CropPhotoUpload(BaseModel):
    """Schema for crop photo upload."""
    file_url: str = Field(..., max_length=500, description="Photo file URL")
    file_key: Optional[str] = Field(None, max_length=500, description="Photo file key (S3 key)")
    caption: Optional[str] = None
    photo_date: Optional[date] = None
    
    @validator('file_url')
    def validate_file_url(cls, v):
        """Validate file URL is not empty."""
        if not v.strip():
            raise ValueError('File URL cannot be empty')
        return v.strip()


class CropPhotoResponse(BaseModel):
    """Schema for crop photo response."""
    id: str
    crop_id: str
    file_url: str
    file_key: Optional[str]
    caption: Optional[str]
    photo_date: Optional[date]
    uploaded_at: datetime
    uploaded_by: Optional[str]
    
    @validator('id', 'crop_id', 'uploaded_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
