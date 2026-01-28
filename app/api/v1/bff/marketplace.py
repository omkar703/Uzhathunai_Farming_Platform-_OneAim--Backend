"""
Marketplace BFF endpoints for unified discovery.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.organization import MarketplaceExploreResponse
from app.services.organization_service import OrganizationService

router = APIRouter()

@router.get(
    "/explore",
    response_model=MarketplaceExploreResponse,
    status_code=status.HTTP_200_OK,
    summary="Explore marketplace providers",
    description="Unified discovery view for Farmers to find active FSPs with service listings"
)
def explore_marketplace(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Explore marketplace providers.
    
    Logic:
    - Only ACTIVE FSPs with at least one ACTIVE service listing.
    """
    service = OrganizationService(db)
    providers = service.get_marketplace_explore(current_user.id)
    
    return {
        "success": True,
        "data": providers
    }
