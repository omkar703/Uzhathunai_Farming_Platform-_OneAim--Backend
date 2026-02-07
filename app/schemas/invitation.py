"""
Invitation schemas for Uzhathunai v2.0.

Schemas for organization member invitation workflow.
"""
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator, model_validator
from app.models.enums import InvitationStatus


class InviteMemberRequest(BaseModel):
    """Schema for inviting member to organization."""
    invitee_email: EmailStr
    role_id: UUID
    message: Optional[str] = None
    expires_in_days: int = Field(default=7, ge=1, le=30)
    
    @validator('expires_in_days')
    def validate_expiry(cls, v):
        """Validate expiry is within reasonable range."""
        if v < 1 or v > 30:
            raise ValueError('Expiry must be between 1 and 30 days')
        return v


class SendInvitationRequest(BaseModel):
    """Schema for sending invitation by user ID and role code."""
    userId: UUID
    role: str


class InvitationResponse(BaseModel):
    """Schema for invitation response."""
    id: str
    organization_id: str
    inviter_id: str
    invitee_email: str
    invitee_user_id: Optional[str] = None
    role_id: str
    status: InvitationStatus
    invited_at: datetime
    responded_at: Optional[datetime] = None
    expires_at: datetime
    message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # Organization details (from relationship)
    organization_name: Optional[str] = None
    organization_type: Optional[str] = None
    # Inviter details (from relationship)
    inviter_name: Optional[str] = None
    inviter_email: Optional[str] = None
    # Role details (from relationship)
    role_name: Optional[str] = None
    role_display_name: Optional[str] = None
    
    @validator('id', 'organization_id', 'inviter_id', 'invitee_user_id', 'role_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    @model_validator(mode='after')
    def populate_relationship_fields(self) -> 'InvitationResponse':
        """Populate flattened fields from relationships if available."""
        # Note: This works because Pydantic V2's from_attributes=True 
        # allows accessing relationship objects during validation if they were loaded.
        # But here we need to handle the case where we are already in the Pydantic model state.
        # If we got here from from_attributes, the attributes might already be on 'self' if they were properties,
        # but here they are just fields.
        
        # Actually, the most reliable way with SQLAlchemy models is to let Pydantic handle it
        # by defining how to get those attributes.
        return self

    @model_validator(mode='before')
    @classmethod
    def from_orm_custom(cls, data: Any) -> Any:
        """Handle SQLAlchemy models by flattening relationships before validation."""
        if not hasattr(data, '__dict__'):
            return data
            
        # If it's a SQLAlchemy model, we can extract the extra info
        if hasattr(data, 'organization') and data.organization:
            setattr(data, 'organization_name', data.organization.name)
            if data.organization.organization_type:
                # Handle both Enum and string
                ord_type = data.organization.organization_type
                setattr(data, 'organization_type', ord_type.value if hasattr(ord_type, 'value') else ord_type)
                
        if hasattr(data, 'inviter') and data.inviter:
            setattr(data, 'inviter_name', f"{data.inviter.first_name or ''} {data.inviter.last_name or ''}".strip() or data.inviter.email)
            setattr(data, 'inviter_email', data.inviter.email)
            
        if hasattr(data, 'role') and data.role:
            setattr(data, 'role_name', data.role.code)
            setattr(data, 'role_display_name', data.role.display_name)
            
        return data

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class InvitationListResponse(BaseModel):
    """Schema for paginated invitation list."""
    items: List[InvitationResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class AcceptInvitationResponse(BaseModel):
    """Schema for accept invitation response."""
    message: str
    organization_id: str
    member_id: str
    
    @validator('organization_id', 'member_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v


class RejectInvitationResponse(BaseModel):
    """Schema for reject invitation response."""
    message: str
    invitation_id: str
    
    @validator('invitation_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v


class JoinRequestResponse(BaseModel):
    """Schema for join request response."""
    id: str
    inviter_name: str
    role: str
    status: str
    created_at: Optional[str] = None
    user_id: str


class AcceptInvitationRequest(BaseModel):
    """Schema for accepting invitation with optional role override."""
    role_id: Optional[UUID] = None
