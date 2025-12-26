"""
Pydantic schemas for Parameter management in Farm Audit Management.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.models.parameter import ParameterType


# Translation schemas
class ParameterTranslationBase(BaseModel):
    """Base schema for parameter translation."""
    language_code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    help_text: Optional[str] = None


class ParameterTranslationResponse(ParameterTranslationBase):
    """Response schema for parameter translation."""
    id: UUID
    parameter_id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True


# Parameter schemas
class ParameterBase(BaseModel):
    """Base schema for parameter."""
    code: str = Field(..., min_length=1, max_length=50)
    parameter_type: ParameterType
    is_active: bool = Field(default=True)
    parameter_metadata: Optional[Dict[str, Any]] = Field(default={})
    
    @validator('parameter_metadata')
    def validate_parameter_metadata(cls, v, values):
        """Validate parameter_metadata based on parameter_type."""
        if not v:
            return v
        
        # Validate min_photos and max_photos if present
        if 'min_photos' in v:
            if not isinstance(v['min_photos'], int) or v['min_photos'] < 0:
                raise ValueError('min_photos must be a non-negative integer')
        
        if 'max_photos' in v:
            if not isinstance(v['max_photos'], int) or v['max_photos'] < 0:
                raise ValueError('max_photos must be a non-negative integer')
        
        # Validate min_photos <= max_photos
        if 'min_photos' in v and 'max_photos' in v:
            if v['min_photos'] > v['max_photos']:
                raise ValueError('min_photos cannot be greater than max_photos')
        
        # Validate numeric metadata
        if 'parameter_type' in values and values['parameter_type'] == ParameterType.NUMERIC:
            if 'min_value' in v and 'max_value' in v:
                if v['min_value'] > v['max_value']:
                    raise ValueError('min_value cannot be greater than max_value')
            
            if 'decimal_places' in v:
                if not isinstance(v['decimal_places'], int) or v['decimal_places'] < 0:
                    raise ValueError('decimal_places must be a non-negative integer')
        
        return v


class ParameterCreate(ParameterBase):
    """Schema for creating a parameter."""
    translations: List[Dict[str, Any]] = Field(..., min_items=1)
    option_set_ids: Optional[List[UUID]] = Field(default=[])
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations have required fields."""
        for trans in v:
            if 'language_code' not in trans or 'name' not in trans:
                raise ValueError('Each translation must have language_code and name')
        return v
    
    @validator('option_set_ids')
    def validate_option_sets(cls, v, values):
        """Validate option sets are provided for SELECT parameter types."""
        if 'parameter_type' in values:
            param_type = values['parameter_type']
            if param_type in [ParameterType.SINGLE_SELECT, ParameterType.MULTI_SELECT]:
                if not v or len(v) == 0:
                    raise ValueError(f'{param_type.value} parameters must have at least one option set')
        return v


class ParameterUpdate(BaseModel):
    """Schema for updating a parameter."""
    is_active: Optional[bool] = None
    parameter_metadata: Optional[Dict[str, Any]] = None
    translations: Optional[List[Dict[str, Any]]] = None
    option_set_ids: Optional[List[UUID]] = None
    
    @validator('parameter_metadata')
    def validate_parameter_metadata(cls, v):
        """Validate parameter_metadata."""
        if not v:
            return v
        
        # Validate min_photos and max_photos if present
        if 'min_photos' in v:
            if not isinstance(v['min_photos'], int) or v['min_photos'] < 0:
                raise ValueError('min_photos must be a non-negative integer')
        
        if 'max_photos' in v:
            if not isinstance(v['max_photos'], int) or v['max_photos'] < 0:
                raise ValueError('max_photos must be a non-negative integer')
        
        # Validate min_photos <= max_photos
        if 'min_photos' in v and 'max_photos' in v:
            if v['min_photos'] > v['max_photos']:
                raise ValueError('min_photos cannot be greater than max_photos')
        
        return v


class ParameterCopy(BaseModel):
    """Schema for copying a parameter."""
    new_code: str = Field(..., min_length=1, max_length=50)


class ParameterResponse(ParameterBase):
    """Response schema for parameter."""
    id: UUID
    is_system_defined: bool
    owner_org_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    translations: List[ParameterTranslationResponse] = []
    option_set_ids: List[UUID] = []
    
    class Config:
        orm_mode = True


class ParameterDetailResponse(ParameterResponse):
    """Detailed response schema for parameter with all translations and option sets."""
    pass

