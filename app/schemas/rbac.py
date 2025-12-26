"""
RBAC schemas for Uzhathunai v2.0.

Schemas for Role-Based Access Control including roles, permissions, and overrides.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, validator
from app.models.enums import UserRoleScope, PermissionEffect


class PermissionResponse(BaseModel):
    """Schema for permission response."""
    id: str
    code: str
    name: str
    resource: str
    action: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
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


class RolePermissionResponse(BaseModel):
    """Schema for role permission mapping response."""
    permission: PermissionResponse
    effect: PermissionEffect
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Schema for role response."""
    id: str
    code: str
    name: str
    display_name: str
    scope: UserRoleScope
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Optional: include permissions if needed
    permissions: Optional[List[RolePermissionResponse]] = None
    
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


class CreateOrgRolePermissionOverrideRequest(BaseModel):
    """Schema for creating organization-level permission override."""
    role_id: UUID
    permission_id: UUID
    effect: PermissionEffect


class OrgRolePermissionOverrideResponse(BaseModel):
    """Schema for organization role permission override response."""
    id: str
    organization_id: str
    role_id: str
    permission_id: str
    effect: PermissionEffect
    created_at: datetime
    created_by: str
    # Role details (from relationship)
    role_code: Optional[str]
    role_name: Optional[str]
    # Permission details (from relationship)
    permission_code: Optional[str]
    permission_name: Optional[str]
    permission_resource: Optional[str]
    permission_action: Optional[str]
    
    @validator('id', 'organization_id', 'role_id', 'permission_id', 'created_by', pre=True)
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


class PermissionCheckRequest(BaseModel):
    """Schema for permission check request."""
    resource: str
    action: str


class PermissionCheckResponse(BaseModel):
    """Schema for permission check response."""
    allowed: bool
    resource: str
    action: str
    roles: List[str]
    evaluation_details: Optional[dict] = None
