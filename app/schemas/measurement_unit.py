"""
Measurement Unit schemas for Uzhathunai v2.0.

Schemas for measurement unit operations and conversions.
"""
from typing import Optional
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.enums import MeasurementUnitCategory


class MeasurementUnitTranslationResponse(BaseModel):
    """Schema for measurement unit translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class MeasurementUnitResponse(BaseModel):
    """Schema for measurement unit response."""
    id: str
    category: MeasurementUnitCategory
    code: str
    symbol: Optional[str]
    is_base_unit: bool
    conversion_factor: Optional[Decimal]
    sort_order: int
    name: Optional[str] = None
    description: Optional[str] = None
    translations: list[MeasurementUnitTranslationResponse] = Field(default_factory=list)
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class ConvertQuantityRequest(BaseModel):
    """Schema for quantity conversion request."""
    value: Decimal = Field(..., description="Value to convert")
    from_unit_id: UUID = Field(..., description="Source unit ID")
    to_unit_id: UUID = Field(..., description="Target unit ID")
    
    @validator('value')
    def validate_value(cls, v):
        """Validate value is positive."""
        if v <= 0:
            raise ValueError('Value must be positive')
        return v


class ConvertQuantityResponse(BaseModel):
    """Schema for quantity conversion response."""
    original_value: Decimal
    converted_value: Decimal
    from_unit: MeasurementUnitResponse
    to_unit: MeasurementUnitResponse
    
    class Config:
        from_attributes = True
