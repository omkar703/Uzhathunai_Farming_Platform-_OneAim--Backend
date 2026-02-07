"""
Work Order schemas for Uzhathunai v2.0.

Schemas for work order CRUD operations and scope management.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.enums import WorkOrderStatus, WorkOrderScopeType
from app.schemas.user import UserBasicInfo


class WorkOrderScopeCreate(BaseModel):
    """Schema for creating work order scope item."""
    scope: WorkOrderScopeType
    scope_id: UUID
    access_permissions: Dict[str, bool] = Field(
        default_factory=lambda: {"read": True, "write": False, "track": False}
    )
    sort_order: int = Field(default=0, ge=0)
    
    @validator('access_permissions')
    def validate_permissions(cls, v):
        """Validate permissions structure."""
        required_keys = {'read', 'write', 'track'}
        if not all(key in v for key in required_keys):
            raise ValueError(f'Permissions must include: {", ".join(required_keys)}')
        
        # Validate all values are boolean
        if not all(isinstance(val, bool) for val in v.values()):
            raise ValueError('All permission values must be boolean')
        
        return v


class WorkOrderScopeResponse(BaseModel):
    """Schema for work order scope response."""
    id: str
    work_order_id: str
    scope: WorkOrderScopeType
    scope_id: str
    access_permissions: Dict[str, bool]
    sort_order: int
    created_at: datetime
    created_by: Optional[str]
    
    @validator('id', 'work_order_id', 'scope_id', 'created_by', pre=True)
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


class WorkOrderCreate(BaseModel):
    """Schema for creating work order."""
    farming_organization_id: UUID
    fsp_organization_id: UUID
    service_listing_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: Optional[float] = Field(None, ge=0)
    currency: str = Field(default='INR', max_length=10)
    scope_items: List[WorkOrderScopeCreate] = Field(default_factory=list)
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title is not empty."""
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validate end_date is after start_date."""
        if v is not None and 'start_date' in values and values['start_date'] is not None:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency code."""
        valid_currencies = ['INR', 'USD', 'EUR', 'GBP']
        if v not in valid_currencies:
            raise ValueError(f'Currency must be one of: {", ".join(valid_currencies)}')
        return v


class WorkOrderUpdate(BaseModel):
    """Schema for updating work order."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_amount: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title is not empty if provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v


class WorkOrderStatusUpdate(BaseModel):
    """Schema for updating work order status."""
    status: WorkOrderStatus
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is a valid work order status."""
        if v not in WorkOrderStatus:
            raise ValueError(f'Invalid status: {v}')
        return v


class WorkOrderAssignRequest(BaseModel):
    """Schema for assigning work order."""
    assigned_to_user_id: UUID


class WorkOrderCompleteRequest(BaseModel):
    """Schema for completing work order."""
    completion_notes: Optional[str] = None
    completion_photo_url: Optional[str] = None
    actual_cost: Optional[float] = Field(None, ge=0)


class WorkOrderAccessUpdate(BaseModel):
    """Schema for updating work order access."""
    access_granted: bool


class ServiceSnapshot(BaseModel):
    """Schema for service snapshot."""
    name: str
    description: Optional[str] = None


class WorkOrderResponse(BaseModel):
    """Schema for work order response."""
    id: str
    farming_organization_id: str
    fsp_organization_id: str
    service_listing_id: Optional[str]
    work_order_number: str
    title: str
    description: Optional[str]
    status: WorkOrderStatus
    terms_and_conditions: Optional[str]
    scope_metadata: Optional[Dict[str, Any]]
    start_date: Optional[date]
    end_date: Optional[date]
    total_amount: Optional[float]
    currency: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    accepted_at: Optional[datetime]
    accepted_by: Optional[str]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    completion_notes: Optional[str] = None
    completion_photo_url: Optional[str] = None
    
    # New fields
    farming_organization_name: Optional[str] = None
    fsp_organization_name: Optional[str] = None
    assigned_member: Optional[UserBasicInfo] = None
    service_snapshot: Optional[ServiceSnapshot] = None
    access_granted: bool
    
    @validator(
        'id', 'farming_organization_id', 'fsp_organization_id', 
        'service_listing_id', 'created_by', 'updated_by', 'accepted_by',
        pre=True
    )
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


class WorkOrderWithScopeResponse(WorkOrderResponse):
    """Schema for work order response with scope items."""
    scope_items: List[WorkOrderScopeResponse] = Field(default_factory=list)


class WorkOrderListResponse(BaseModel):
    """Schema for paginated work order list response."""
    items: List[WorkOrderResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class WorkOrderScopePermissionsUpdate(BaseModel):
    """Schema for updating work order scope permissions."""
    access_permissions: Dict[str, bool]
    
    @validator('access_permissions')
    def validate_permissions(cls, v):
        """Validate permissions structure."""
        required_keys = {'read', 'write', 'track'}
        if not all(key in v for key in required_keys):
            raise ValueError(f'Permissions must include: {", ".join(required_keys)}')
        
        # Validate all values are boolean
        if not all(isinstance(val, bool) for val in v.values()):
            raise ValueError('All permission values must be boolean')
        
        return v


class AddWorkOrderScopeRequest(BaseModel):
    """Schema for adding scope items to work order."""
    scope_items: List[WorkOrderScopeCreate] = Field(..., min_items=1)
    
    @validator('scope_items')
    def validate_scope_items(cls, v):
        """Validate scope items list is not empty."""
        if not v:
            raise ValueError('At least one scope item is required')
        return v
