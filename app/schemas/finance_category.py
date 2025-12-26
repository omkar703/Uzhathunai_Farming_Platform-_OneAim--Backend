"""
Finance Category schemas for Uzhathunai v2.0.

Schemas for finance categories (system-defined and org-specific).
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.enums import TransactionType


class FinanceCategoryTranslationResponse(BaseModel):
    """Schema for finance category translation response."""
    language_code: str
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class FinanceCategoryCreate(BaseModel):
    """Schema for creating finance category (org-specific only)."""
    transaction_type: TransactionType = Field(..., description="Transaction type (INCOME or EXPENSE)")
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


class FinanceCategoryUpdate(BaseModel):
    """Schema for updating finance category (org-specific only)."""
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


class FinanceCategoryResponse(BaseModel):
    """Schema for finance category response."""
    id: str
    transaction_type: TransactionType
    code: str
    is_system_defined: bool
    owner_org_id: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    translations: list[FinanceCategoryTranslationResponse] = Field(default_factory=list)
    
    @validator('id', 'owner_org_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
