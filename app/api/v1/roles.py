"""
Role API endpoints for Uzhathunai v2.0.
Handles role retrieval for RBAC system.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.enums import OrganizationType
from app.schemas.rbac import RoleResponse
from app.services.role_service import RoleService

router = APIRouter()


@router.get(
    "",
    response_model=List[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="Get roles",
    description="Get available roles, optionally filtered by organization type"
)
def get_roles(
    org_type: Optional[OrganizationType] = Query(None, description="Filter by organization type"),
    db: Session = Depends(get_db)
):
    """
    Get available roles.
    
    Used for populating role selectors in UI.
    
    - **org_type**: Filter by organization type (FARMING or FSP)
      - FARMING: Returns OWNER, ADMIN, SUPERVISOR, MEMBER
      - FSP: Returns FSP_OWNER, FSP_ADMIN, FSP_CONSULTANT
      - None: Returns all active roles
    """
    service = RoleService(db)
    return service.get_roles(org_type=org_type)


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get role details",
    description="Get role details by ID"
)
def get_role(
    role_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get role details by ID.
    """
    service = RoleService(db)
    return service.get_role(role_id)
