"""
Crop Data schemas for Uzhathunai v2.0.

Schemas for crop categories, types, and varieties.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class CropCategoryTranslationResponse(BaseModel):
    """Schema for crop category translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class CropCategoryResponse(BaseModel):
    """Schema for crop category response."""
    id: str
    code: str
    sort_order: int
    is_active: bool
    name: Optional[str] = None
    description: Optional[str] = None
    translations: list[CropCategoryTranslationResponse] = Field(default_factory=list)
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class CropTypeTranslationResponse(BaseModel):
    """Schema for crop type translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class CropTypeResponse(BaseModel):
    """Schema for crop type response."""
    id: str
    category_id: str
    code: str
    sort_order: int
    is_active: bool
    name: Optional[str] = None
    description: Optional[str] = None
    translations: list[CropTypeTranslationResponse] = Field(default_factory=list)
    
    @validator('id', 'category_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class CropTypeCreate(BaseModel):
    """Schema for creating a custom crop type."""
    name: str = Field(..., min_length=1, max_length=200, description="Display name of the crop type")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class VarietyMetadata(BaseModel):
    """Schema for crop variety metadata structure."""
    maturity_days: Optional[int] = Field(None, description="Days to maturity")
    yield_potential_kg_per_acre: Optional[float] = Field(None, description="Expected yield in kg per acre")
    plant_spacing_cm: Optional[int] = Field(None, description="Plant spacing in cm")
    row_spacing_cm: Optional[int] = Field(None, description="Row spacing in cm")
    water_requirement: Optional[str] = Field(None, description="Water requirement level (LOW, MEDIUM, HIGH)")
    disease_resistance: Optional[list[str]] = Field(default_factory=list, description="List of diseases resistant to")
    suitable_seasons: Optional[list[str]] = Field(default_factory=list, description="Suitable growing seasons")
    
    class Config:
        extra = "allow"  # Allow additional fields


class CropVarietyTranslationResponse(BaseModel):
    """Schema for crop variety translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class CropVarietyResponse(BaseModel):
    """Schema for crop variety response."""
    id: str
    crop_type_id: str
    code: str
    sort_order: int
    is_active: bool
    variety_metadata: Optional[Dict[str, Any]] = Field(None, description="Variety metadata (maturity days, yield potential, spacing, etc.)")
    translations: list[CropVarietyTranslationResponse] = Field(default_factory=list)
    
    @validator('id', 'crop_type_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
