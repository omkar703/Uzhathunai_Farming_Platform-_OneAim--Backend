"""
Organization switch schema.
"""
from uuid import UUID
from pydantic import BaseModel, Field


class OrganizationSwitch(BaseModel):
    """Schema for switching organization context."""
    organization_id: UUID = Field(..., description="Organization ID to switch to")
