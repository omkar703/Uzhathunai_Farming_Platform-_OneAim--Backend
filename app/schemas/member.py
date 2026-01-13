"""
Member schemas for Uzhathunai v2.0.

Schemas for organization member management including role assignments.
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.enums import MemberStatus


class MemberRoleAssignment(BaseModel):
    """Schema for assigning role to member."""
    role_id: UUID
    is_primary: bool = False


class MemberRoleResponse(BaseModel):
    """Schema for member role response."""
    role_id: str
    role_code: str
    role_name: str
    is_primary: bool
    assigned_at: Optional[datetime] = None
    
    @validator('role_id', pre=True)
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


class UpdateMemberRolesRequest(BaseModel):
    """Schema for updating member roles (supports multiple roles)."""
    roles: List[MemberRoleAssignment] = Field(..., min_items=1)
    reason: Optional[str] = None
    
    @validator('roles')
    def validate_primary_role(cls, v):
        """Validate exactly one role must be marked as primary."""
        primary_count = sum(1 for role in v if role.is_primary)
        if primary_count != 1:
            raise ValueError('Exactly one role must be marked as primary')
        return v


class MemberResponse(BaseModel):
    """Schema for member response."""
    id: str
    user_id: str
    organization_id: str
    status: MemberStatus
    roles: List[MemberRoleResponse]
    joined_at: datetime
    left_at: Optional[datetime] = None
    # User details (from relationship)
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    @validator('id', 'user_id', 'organization_id', pre=True)
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


class UpdateMemberStatusRequest(BaseModel):
    """Schema for updating member status."""
    status: MemberStatus
    reason: Optional[str] = None
