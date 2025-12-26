"""
FSP Service schemas for Uzhathunai v2.0.

Schemas for Farm Service Provider service listings and master services.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.enums import ServiceStatus, OrganizationStatus


class MasterServiceTranslationResponse(BaseModel):
    """Schema for master service translation response."""
    language_code: str
    display_name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True


class MasterServiceResponse(BaseModel):
    """Schema for master service response."""
    id: str
    code: str
    name: str
    description: Optional[str]
    status: ServiceStatus
    sort_order: int
    created_at: datetime
    updated_at: datetime
    # Optional: include translations
    translations: Optional[List[MasterServiceTranslationResponse]] = None
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FSPServiceListingCreate(BaseModel):
    """Schema for creating FSP service listing."""
    service_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    service_area_districts: List[str] = Field(default_factory=list)
    pricing_model: Optional[str] = None  # PER_HOUR, PER_DAY, PER_ACRE, FIXED, CUSTOM
    base_price: Optional[float] = Field(None, ge=0)
    currency: str = Field(default='INR', max_length=10)
    
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


class FSPServiceListingUpdate(BaseModel):
    """Schema for updating FSP service listing."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    service_area_districts: Optional[List[str]] = None
    pricing_model: Optional[str] = None
    base_price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    status: Optional[ServiceStatus] = None
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v
    
    @validator('pricing_model')
    def validate_pricing_model(cls, v):
        """Validate pricing model if provided."""
        if v is not None:
            valid_models = ['PER_HOUR', 'PER_DAY', 'PER_ACRE', 'FIXED', 'CUSTOM']
            if v not in valid_models:
                raise ValueError(f'Pricing model must be one of: {", ".join(valid_models)}')
        return v


class FSPServiceListingResponse(BaseModel):
    """Schema for FSP service listing response."""
    id: str
    fsp_organization_id: str
    service_id: str
    title: str
    description: Optional[str]
    service_area_districts: List[str]
    pricing_model: Optional[str]
    base_price: Optional[float]
    currency: str
    status: ServiceStatus
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    # Master service details (from relationship)
    service_code: Optional[str]
    service_name: Optional[str]
    service_description: Optional[str]
    
    @validator('id', 'fsp_organization_id', 'service_id', 'created_by', 'updated_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }



class FSPApprovalDocumentCreate(BaseModel):
    """Schema for creating FSP approval document."""
    document_type: str = Field(..., min_length=1, max_length=100)
    file_url: str = Field(..., min_length=1, max_length=500)
    file_key: str = Field(..., min_length=1, max_length=500)
    file_name: str = Field(..., min_length=1, max_length=255)
    
    @validator('document_type', 'file_url', 'file_key', 'file_name')
    def validate_not_empty(cls, v):
        """Validate fields are not empty."""
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class FSPApprovalDocumentResponse(BaseModel):
    """Schema for FSP approval document response."""
    id: str
    fsp_organization_id: str
    document_type: str
    file_url: str
    file_key: str
    file_name: str
    uploaded_at: datetime
    uploaded_by: Optional[str]
    
    @validator('id', 'fsp_organization_id', 'uploaded_by', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FSPOrganizationApprovalResponse(BaseModel):
    """Schema for FSP organization in approval list."""
    id: str
    name: str
    description: Optional[str]
    status: OrganizationStatus
    registration_number: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    # Document count
    documents_count: Optional[int] = 0
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FSPApprovalReviewRequest(BaseModel):
    """Schema for FSP approval review request."""
    approve: bool
    notes: Optional[str] = None
    
    @validator('notes')
    def validate_notes(cls, v):
        """Validate notes if provided."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v


class ServiceListingFilters(BaseModel):
    """Schema for service listing filters."""
    service_type: Optional[UUID] = None
    district: Optional[str] = None
    pricing_model: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    @validator('pricing_model')
    def validate_pricing_model(cls, v):
        """Validate pricing model if provided."""
        if v is not None:
            valid_models = ['PER_HOUR', 'PER_DAY', 'PER_ACRE', 'FIXED', 'CUSTOM']
            if v not in valid_models:
                raise ValueError(f'Pricing model must be one of: {", ".join(valid_models)}')
        return v


class FSPServiceListingPaginatedResponse(BaseModel):
    """Schema for paginated service listing response."""
    items: List[FSPServiceListingResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class FSPOrganizationApprovalPaginatedResponse(BaseModel):
    """Schema for paginated FSP organization approval response."""
    items: List[FSPOrganizationApprovalResponse]
    total: int
    page: int
    limit: int
    total_pages: int
