"""
Farming Service API endpoints.
Handles operations specific to Farming Organizations (Farmers).
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.enums import OrganizationType
from app.schemas.response import BaseResponse
from app.schemas.organization import ProviderResponse, ProviderListBaseResponse
from app.services.organization_service import OrganizationService
from app.core.exceptions import PermissionError
from app.core.organization_context import get_organization_id, validate_organization_type

router = APIRouter()

@router.get(
    "/providers",
    response_model=ProviderListBaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Farming Providers",
    description="Get list of Service Providers (FSPs) active with the current Farmer"
)
def get_farming_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of FSPs working with the current Farmer.
    
    Returns FSPs that have at least one PENDING, ACCEPTED, or ACTIVE Work Order.
    User must be an Admin/Owner of a Farming Organization.
    """
    
    # 1. Get organization ID from context with Smart Inference
    org_id = get_organization_id(current_user, db, expected_type=OrganizationType.FARMING)
    
    # 2. Validate this is a FARMING organization
    validate_organization_type(org_id, OrganizationType.FARMING, db)
    
    org_service = OrganizationService(db)
    providers = org_service.get_farming_providers(org_id, current_user.id)
    
    return {
        "success": True,
        "message": f"Retrieved {len(providers)} providers",
        "data": providers
    }
