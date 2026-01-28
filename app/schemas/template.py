"""
Pydantic schemas for Template models.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# Template Translation Schemas
class TemplateTranslationBase(BaseModel):
    language_code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TemplateTranslationCreate(TemplateTranslationBase):
    pass


class TemplateTranslationResponse(TemplateTranslationBase):
    id: UUID
    template_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Template Schemas
class TemplateBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=50)
    crop_type_id: Optional[UUID] = None
    is_active: bool = True


# Nested schemas for Template Creation
class TemplateParameterCreate(BaseModel):
    parameter_id: UUID
    is_required: bool = False
    sort_order: int = 0

class TemplateSectionCreate(BaseModel):
    section_id: UUID
    sort_order: int = 0
    parameters: List[TemplateParameterCreate] = []


class TemplateCreate(TemplateBase):
    translations: List[TemplateTranslationCreate] = Field(..., min_items=1)
    is_system_defined: Optional[bool] = None  # Set by service based on user role
    owner_org_id: Optional[UUID] = None  # Set by service based on user role
    sections: List[TemplateSectionCreate] = []

    @validator('translations')
    def validate_translations(cls, v):
        if not v:
            raise ValueError('At least one translation is required')
        # Check for duplicate language codes
        lang_codes = [t.language_code for t in v]
        if len(lang_codes) != len(set(lang_codes)):
            raise ValueError('Duplicate language codes not allowed')
        return v


class TemplateUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    crop_type_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    translations: Optional[List[TemplateTranslationCreate]] = None

    @validator('translations')
    def validate_translations(cls, v):
        if v is not None:
            if not v:
                raise ValueError('At least one translation is required')
            # Check for duplicate language codes
            lang_codes = [t.language_code for t in v]
            if len(lang_codes) != len(set(lang_codes)):
                raise ValueError('Duplicate language codes not allowed')
        return v


class TemplateResponse(TemplateBase):
    id: UUID
    name: str
    description: Optional[str]
    is_system_defined: bool
    owner_org_id: Optional[UUID]
    owner_org_name: Optional[str] = None
    version: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    translations: List[TemplateTranslationResponse]

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    items: List[TemplateResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Template Section Schemas
class TemplateSectionAdd(BaseModel):
    section_id: UUID
    sort_order: int = Field(default=0, ge=0)


class TemplateSectionResponse(BaseModel):
    id: UUID
    template_id: UUID
    section_id: UUID
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# Template Parameter Schemas
class TemplateParameterAdd(BaseModel):
    parameter_id: UUID
    is_required: bool = False
    sort_order: int = Field(default=0, ge=0)


class TemplateParameterResponse(BaseModel):
    id: UUID
    template_section_id: UUID
    parameter_id: UUID
    is_required: bool
    sort_order: int
    name: Optional[str] = None
    parameter_snapshot: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Template Copy Schemas
class TemplateCopy(BaseModel):
    new_code: str = Field(..., min_length=1, max_length=50)
    new_name_translations: Dict[str, str] = Field(..., min_items=1)
    crop_type_id: Optional[UUID] = None

    @validator('new_name_translations')
    def validate_translations(cls, v):
        if not v:
            raise ValueError('At least one translation is required')
        return v


# Template with Details (for GET endpoints)
class TemplateSectionDetail(BaseModel):
    id: UUID
    section_id: UUID
    section_code: str
    section_name: str  # Default language
    sort_order: int
    parameters: List[TemplateParameterResponse]

    class Config:
        from_attributes = True


class TemplateDetail(TemplateResponse):
    sections: List[TemplateSectionDetail]

    class Config:
        from_attributes = True
