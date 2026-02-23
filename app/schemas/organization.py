"""
Organization schemas for Uzhathunai v2.0.

Schemas for organization CRUD operations including FSP service listings.
"""
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, validator, EmailStr
from app.models.enums import OrganizationType, OrganizationStatus
from app.schemas.fsp_service import FSPServiceListingResponse


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
    specialization: Optional[str] = Field(None, max_length=200)
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
    specialization: Optional[str] = Field(None, max_length=200)
    
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
    specialization: Optional[str]
    subscription_plan_id: Optional[str]
    subscription_start_date: Optional[date]
    subscription_end_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    # Optional services for FSP profile
    services: Optional[list[FSPServiceListingResponse]] = None
    
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


class ClientResponse(BaseModel):
    """Schema for FSP client response."""
    id: str
    name: str
    type: OrganizationType
    status: OrganizationStatus
    relationship_status: str  # ACTIVE (has active WOs), PENDING (only pending WOs), INACTIVE (no active/pending WOs)
    contact_info: dict
    active_work_orders: int
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class ProviderResponse(BaseModel):
    """Schema for FSP provider response (for Farmers)."""
    id: str
    name: str
    logo_url: Optional[str] = None
    service_category: Optional[str] = None
    active_contracts_count: int
    total_contracts_history: int
    first_contract_date: Optional[datetime] = None
    contact: dict
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class OrganizationMemberResponse(BaseModel):
    """Schema for organization member summary."""
    user_id: str
    full_name: str
    email: str
    role: str
    status: str
    joined_at: datetime
    
    @validator('user_id', pre=True)
    def convert_uuid_to_str(cls, v):
        return str(v) if v else v
        
    class Config:
        from_attributes = True

class OrganizationAuditSummary(BaseModel):
    """Schema for organization audit summary."""
    id: str
    template_name: str
    status: str
    auditor_name: Optional[str] = None
    audit_date: datetime
    score: Optional[float] = None
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        return str(v) if v else v
        
    class Config:
        from_attributes = True

class OrganizationWorkOrderSummary(BaseModel):
    """Schema for organization work order summary."""
    id: str
    status: str
    service_name: str
    start_date: Optional[date] = None
    amount: Optional[float] = None
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        return str(v) if v else v
        
    class Config:
        from_attributes = True

class OrganizationStats(BaseModel):
    """Schema for organization statistics."""
    total_members: int = 0
    total_audits: int = 0
    active_work_orders: int = 0
    completed_work_orders: int = 0

class OrganizationDetailResponse(OrganizationResponse):
    """Extended schema for full organization details."""
    members: List[OrganizationMemberResponse] = []
    recent_audits: List[OrganizationAuditSummary] = []
    recent_work_orders: List[OrganizationWorkOrderSummary] = []
    stats: OrganizationStats = Field(default_factory=OrganizationStats)

class OrganizationListResponse(BaseModel):
    """Schema for paginated organization list response."""
    items: List[OrganizationResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class MarketplaceExploreItem(BaseModel):
    """Schema for unified marketplace discovery item."""
    id: str
    name: str
    description: str
    specialization: str
    rating: float
    is_verified: bool
    service_count: int
    logo_url: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None # Added for location fallback

    class Config:
        from_attributes = True

# Unified Response Schemas
class MarketplaceExploreResponse(BaseModel):
    """Schema for unified marketplace discovery response."""
    success: bool = True
    data: List[MarketplaceExploreItem]

class OrganizationBaseResponse(BaseModel):
    """Unified wrapper for a single organization."""
    success: bool = True
    data: OrganizationResponse

class OrganizationListBaseResponse(BaseModel):
    """Unified wrapper for organization list."""
    success: bool = True
    data: List[OrganizationResponse]

class ProviderListBaseResponse(BaseModel):
    """Unified wrapper for provider list."""
    success: bool = True
    data: List[ProviderResponse]

class ClientListBaseResponse(BaseModel):
    """Unified wrapper for client list."""
    success: bool = True
    data: List[ClientResponse]

