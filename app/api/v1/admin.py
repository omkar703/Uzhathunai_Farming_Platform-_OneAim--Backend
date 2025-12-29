from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import verify_token
# Using dependencies defined in your project (Stubbed here based on context)
from app.models.user import User
from app.models.organization import Organization, OrganizationStatus, OrgMemberRole
from app.models.rbac import Role
# Assuming you have a dependency to get current user
from app.core.auth import get_current_user

router = APIRouter()

class OrganizationApprovalRequest(BaseModel):
    organization_id: str

@router.post("/approve-org", status_code=status.HTTP_200_OK)
async def approve_organization(
    request: OrganizationApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Approve an organization.
    Only SUPER_ADMIN can perform this action.
    """
    # 1. Verify Super Admin (This assumes your User model has 'role' or you check RBAC)
    # Based on seed_data.py, we assigned roles via OrgMemberRole, but there is also 'SUPER_ADMIN' logic 
    # typically handled by checking if user has a specific system role.
    
    # Simple check based on seed script convention (User -> OrgMember -> Role)
    # Ideally use a dedicated RBAC permission dependency like `deps.requires_system_role("SUPER_ADMIN")`
    # For now, implementing a manual check for "SUPER_ADMIN" role code on the user.
    
    is_super_admin = False
    # Check if user has ANY role with code 'SUPER_ADMIN' in ANY organization (or typically system scope)
    # The seed script assigned SUPER_ADMIN role to the user in the Default Org.
    
    # We need to query OrgMemberRole -> Role where user_id = current_user.id
    stmt = (
        select(Role)
        .join(OrgMemberRole, Role.id == OrgMemberRole.role_id)
        .where(OrgMemberRole.user_id == current_user.id)
        .where(Role.code == "SUPER_ADMIN")
    )
    result = db.execute(stmt)
    if result.scalars().first():
        is_super_admin = True
        
    if not is_super_admin:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Super Admins can approve organizations"
        )

    # 2. Get Organization
    org = db.query(Organization).filter(Organization.id == request.organization_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # 3. Approve
    org.is_approved = True
    org.status = OrganizationStatus.ACTIVE
    db.commit()
    db.refresh(org)

    return {"message": f"Organization {org.name} approved successfully", "status": "ACTIVE"}
