"""
Input Item schemas for Uzhathunai v2.0.

Schemas for input item categories and items (system-defined and org-specific).
"""
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.enums import InputItemType


class ItemMetadata(BaseModel):
    """Schema for input item metadata structure."""
    brand: Optional[str] = Field(None, description="Brand name")
    composition: Optional[str] = Field(None, description="Chemical composition")
    npk_ratio: Optional[str] = Field(None, description="NPK ratio (e.g., 19-19-19)")
    form: Optional[str] = Field(None, description="Form (LIQUID, POWDER, GRANULAR, etc.)")
    solubility: Optional[str] = Field(None, description="Solubility (WATER_SOLUBLE, etc.)")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    batch_number: Optional[str] = Field(None, description="Batch number")
    expiry_date: Optional[str] = Field(None, description="Expiry date")
    storage_instructions: Optional[str] = Field(None, description="Storage instructions")
    application_methods: Optional[list[str]] = Field(default_factory=list, description="Application methods")
    
    class Config:
        extra = "allow"  # Allow additional fields


class InputItemCategoryTranslationResponse(BaseModel):
    """Schema for input item category translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class InputItemCategoryCreate(BaseModel):
    """Schema for creating input item category (org-specific only)."""
    code: str = Field(..., min_length=1, max_length=50)
    translations: list[dict] = Field(..., min_items=1, description="Translations (at least one required)")
    sort_order: int = Field(default=0)
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code is not empty."""
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v.strip().upper()
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations structure."""
        if not v:
            raise ValueError('At least one translation is required')
        for trans in v:
            if 'language_code' not in trans or 'name' not in trans:
                raise ValueError('Each translation must have language_code and name')
            if not trans['name'].strip():
                raise ValueError('Translation name cannot be empty')
        return v


class InputItemCategoryUpdate(BaseModel):
    """Schema for updating input item category (org-specific only)."""
    translations: Optional[list[dict]] = Field(None, description="Translations to update")
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations structure if provided."""
        if v is not None:
            for trans in v:
                if 'language_code' not in trans or 'name' not in trans:
                    raise ValueError('Each translation must have language_code and name')
                if not trans['name'].strip():
                    raise ValueError('Translation name cannot be empty')
        return v


class InputItemCategoryResponse(BaseModel):
    """Schema for input item category response."""
    id: str
    code: str
    is_system_defined: bool
    owner_org_id: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    translations: list[InputItemCategoryTranslationResponse] = Field(default_factory=list)
    # Translated fields (for requested language)
    name: Optional[str] = Field(None, description="Translated name for requested language")
    description: Optional[str] = Field(None, description="Translated description for requested language")
    
    @validator('id', 'owner_org_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class InputItemTranslationResponse(BaseModel):
    """Schema for input item translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class InputItemCreate(BaseModel):
    """Schema for creating input item (org-specific only)."""
    category_id: UUID = Field(..., description="Category ID")
    code: str = Field(..., min_length=1, max_length=50)
    translations: list[dict] = Field(..., min_items=1, description="Translations (at least one required)")
    item_metadata: Optional[Dict[str, Any]] = Field(None, description="Item metadata (brand, composition, NPK ratio, etc.)")
    sort_order: int = Field(default=0)
    type: Optional[InputItemType] = Field(None, description="Item type (FERTILIZER, PESTICIDE, OTHER)")
    default_unit_id: Optional[UUID] = Field(None, description="Default measurement unit ID")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate code is not empty."""
        if not v.strip():
            raise ValueError('Code cannot be empty')
        return v.strip().upper()
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations structure."""
        if not v:
            raise ValueError('At least one translation is required')
        for trans in v:
            if 'language_code' not in trans or 'name' not in trans:
                raise ValueError('Each translation must have language_code and name')
            if not trans['name'].strip():
                raise ValueError('Translation name cannot be empty')
        return v


class InputItemUpdate(BaseModel):
    """Schema for updating input item (org-specific only)."""
    translations: Optional[list[dict]] = Field(None, description="Translations to update")
    item_metadata: Optional[Dict[str, Any]] = Field(None, description="Item metadata to update")
    type: Optional[InputItemType] = Field(None, description="Item type")
    default_unit_id: Optional[UUID] = Field(None, description="Default measurement unit ID")
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None
    
    @validator('translations')
    def validate_translations(cls, v):
        """Validate translations structure if provided."""
        if v is not None:
            for trans in v:
                if 'language_code' not in trans or 'name' not in trans:
                    raise ValueError('Each translation must have language_code and name')
                if not trans['name'].strip():
                    raise ValueError('Translation name cannot be empty')
        return v


class InputItemResponse(BaseModel):
    """Schema for input item response."""
    id: str
    category_id: str
    code: str
    is_system_defined: bool
    owner_org_id: Optional[str]
    sort_order: int
    is_active: bool
    type: Optional[InputItemType] = None
    default_unit_id: Optional[UUID] = None
    item_metadata: Optional[Dict[str, Any]] = Field(None, description="Item metadata (brand, composition, NPK ratio, etc.)")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    translations: list[InputItemTranslationResponse] = Field(default_factory=list)
    # Translated fields (for requested language)
    name: Optional[str] = Field(None, description="Translated name for requested language")
    description: Optional[str] = Field(None, description="Translated description for requested language")
    # Category details
    category: Optional[InputItemCategoryResponse] = Field(None, description="Category details")
    
    @validator('id', 'category_id', 'owner_org_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class InputItemListResponse(BaseModel):
    """Schema for paginated input item list response."""
    success: bool = True
    data: Dict[str, Any] = Field(..., description="Contains items list and pagination metadata")
    
    # Example structure for documentation:
    # {
    #   "success": true,
    #   "data": {
    #     "items": [...],
    #     "total": 45474,
    #     "page": 1,
    #     "limit": 50,
    #     "total_pages": 910
    #   }
    # }
