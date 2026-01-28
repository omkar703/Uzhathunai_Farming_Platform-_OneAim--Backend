"""
Marketplace API endpoints for Uzhathunai v2.0.
Handles discovery of FSP providers.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.organization import OrganizationResponse, OrganizationBaseResponse
from app.schemas.response import BaseResponse
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.get(
    "/providers/{provider_id}",
    response_model=OrganizationBaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get marketplace provider details",
    description="Get public details of an FSP provider for browsing"
)
def get_provider_details(
    provider_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get marketplace provider details.
    
    Accessible by any authenticated user for browsing.
    """
    service = OrganizationService(db)
    provider = service.get_marketplace_provider_details(provider_id)
    
    return {
        "success": True,
        "message": "Provider details retrieved successfully",
        "data": provider
    }
