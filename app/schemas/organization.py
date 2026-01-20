"""
Organization schemas for Uzhathunai v2.0.

Schemas for organization CRUD operations including FSP service listings.
"""
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, validator, EmailStr
from app.models.enums import OrganizationType, OrganizationStatus


class FSPServiceListingCreate(BaseModel):
    """Schema for creating FSP service listing (nested in organization creation)."""
    service_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    service_area_districts: List[str] = Field(default_factory=list)
    pricing_model: Optional[str] = None  # PER_HOUR, PER_DAY, PER_ACRE, FIXED, CUSTOM
    base_price: Optional[float] = Field(None, ge=0)
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title is not empty."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('pricing_model')
    def validate_pricing_model(cls, v):
        """Validate pricing model."""
        if v is not None:
            valid_models = ['PER_HOUR', 'PER_DAY', 'PER_ACRE', 'FIXED', 'CUSTOM']
            if v not in valid_models:
                raise ValueError(f'Pricing model must be one of: {", ".join(valid_models)}')
        return v


class OrganizationCreate(BaseModel):
    """Schema for creating organization."""
    name: str = Field(..., min_length=1, max_length=200)
    organization_type: OrganizationType
    description: Optional[str] = None
    logo_url: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    # FSP-specific
    services: List[FSPServiceListingCreate] = Field(default_factory=list)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty."""
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('services')
    def validate_fsp_services(cls, v, values):
        """Validate FSP organizations must have at least one service."""
        if values.get('organization_type') == OrganizationType.FSP:
            if not v or len(v) == 0:
                raise ValueError('FSP organization must have at least one service')
        return v


class OrganizationUpdate(BaseModel):
    """Schema for updating organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = Field(None, max_length=20)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v


class OrganizationResponse(BaseModel):
    """Schema for organization response."""
    id: str
    name: str
    description: Optional[str]
    logo_url: Optional[str]
    organization_type: OrganizationType
    status: OrganizationStatus
    is_approved: bool
    registration_number: Optional[str]
    address: Optional[str]
    district: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    subscription_plan_id: Optional[str]
    subscription_start_date: Optional[date]
    subscription_end_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    
    @validator('id', 'subscription_plan_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }


class OrganizationListResponse(BaseModel):
    """Schema for paginated organization list response."""
    items: List[OrganizationResponse]
    total: int
    page: int
    limit: int
    total_pages: int

