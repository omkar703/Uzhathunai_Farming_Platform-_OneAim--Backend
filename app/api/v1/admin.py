from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.organization import Organization, OrganizationStatus, OrgMemberRole
from app.models.rbac import Role
from app.core.auth import get_current_super_admin
from app.schemas.response import BaseResponse

router = APIRouter()

@router.post(
    "/organizations/{organization_id}/approve",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Approve an organization",
    description="Approve a pending organization. Only accessible by Super Admins."
)
async def approve_organization(
    organization_id: str,
    current_user: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Approve an organization.
    """
    # 1. Get Organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "message": "Organization not found",
                "error_code": "ORG_NOT_FOUND"
            }
        )
    
    # 2. Approve
    org.is_approved = True
    org.status = OrganizationStatus.ACTIVE
    db.commit()
    db.refresh(org)

    # 3. Clear Cache (Stub for now)
    # redis_client.delete(f"permissions:{organization_id}")

    return {
        "success": True,
        "message": f"Organization {org.name} approved successfully",
        "data": {
            "organization_id": str(org.id),
            "status": org.status.value,
            "is_approved": True
        }
    }

