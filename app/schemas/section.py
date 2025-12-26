"""
Pydantic schemas for Section management in Farm Audit Management.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime


# Translation schemas
class SectionTranslationBase(BaseModel):
    """Base schema for section translation."""
    language_code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class SectionTranslationResponse(SectionTranslationBase):
    """Response schema for section translation."""
    id: UUID
    section_id: UUID
    created_at: datetime
    
    class Config:
        orm_mode = True


# Section schemas
class SectionBase(BaseModel):
    """Base schema for section."""
    code: str = Field(..., min_length=1, max_length=50)
    is_active: bool = Field(default=True)


class SectionCreate(SectionBase):
    """Schema for creating a section."""
    translations: List[Dict[str, str]] = Field(..., min_items=1)
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations have required fields."""
        for trans in v:
            if 'language_code' not in trans or 'name' not in trans:
                raise ValueError('Each translation must have language_code and name')
        return v


class SectionUpdate(BaseModel):
    """Schema for updating a section."""
    is_active: Optional[bool] = None
    translations: Optional[List[Dict[str, str]]] = None


class SectionResponse(SectionBase):
    """Response schema for section."""
    id: UUID
    is_system_defined: bool
    owner_org_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    name: Optional[str] = None  # Translated name for requested language
    description: Optional[str] = None  # Translated description for requested language
    
    class Config:
        orm_mode = True


class SectionDetailResponse(SectionResponse):
    """Detailed response schema for section with all translations."""
    translations: List[SectionTranslationResponse] = []
    
    class Config:
        orm_mode = True
