"""
Pydantic schemas for Option Set management in Farm Audit Management.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime


# Translation schemas
class OptionTranslationBase(BaseModel):
    """Base schema for option translation."""
    language_code: str = Field(..., min_length=2, max_length=10)
    display_text: str = Field(..., min_length=1, max_length=200)


class OptionTranslationResponse(OptionTranslationBase):
    """Response schema for option translation."""
    id: UUID
    option_id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True


# Option schemas
class OptionBase(BaseModel):
    """Base schema for option."""
    code: str = Field(..., min_length=1, max_length=50)
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class OptionCreate(OptionBase):
    """Schema for creating an option."""
    translations: List[Dict[str, str]] = Field(..., min_items=1)
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations have required fields."""
        for trans in v:
            if 'language_code' not in trans or 'display_text' not in trans:
                raise ValueError('Each translation must have language_code and display_text')
        return v


class OptionUpdate(BaseModel):
    """Schema for updating an option."""
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    translations: Optional[List[Dict[str, str]]] = None


class OptionResponse(OptionBase):
    """Response schema for option."""
    id: UUID
    option_set_id: UUID
    created_at: datetime
    translations: List[OptionTranslationResponse]
    display_text: Optional[str] = None  # Translated display text for requested language
    
    class Config:
        orm_mode = True


# Option Set schemas
class OptionSetBase(BaseModel):
    """Base schema for option set."""
    code: str = Field(..., min_length=1, max_length=50)
    is_active: bool = Field(default=True)


class OptionSetCreate(OptionSetBase):
    """Schema for creating an option set."""
    options: Optional[List[OptionCreate]] = Field(default=[])


class OptionSetUpdate(BaseModel):
    """Schema for updating an option set."""
    is_active: Optional[bool] = None


class OptionSetResponse(OptionSetBase):
    """Response schema for option set."""
    id: UUID
    is_system_defined: bool
    owner_org_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    options: List[OptionResponse] = []
    
    class Config:
        orm_mode = True


class OptionSetDetailResponse(OptionSetResponse):
    """Detailed response schema for option set with all options."""
    pass
