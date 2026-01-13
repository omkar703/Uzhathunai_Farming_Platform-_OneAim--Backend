"""
Member management API endpoints for Uzhathunai v2.0.
Handles organization member operations.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import MemberStatus
from app.schemas.member import (
    MemberResponse,
    UpdateMemberRolesRequest
)
from app.schemas.invitation import InviteMemberRequest, InvitationResponse
from app.services.member_service import MemberService
from app.services.invitation_service import InvitationService

router = APIRouter()


@router.post(
    "/organizations/{org_id}/members/invite",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite member",
    description="Invite a user to join organization"
)
def invite_member(
    org_id: UUID,
    data: InviteMemberRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Invite member to organization.
    
    Only OWNER/ADMIN can invite members.
    
    - **invitee_email**: Email address of user to invite (required)
    - **role_id**: Role to assign (required)
    - **message**: Optional message to include in invitation
    - **expires_in_days**: Days until invitation expires (default: 7)
    
    Sends invitation email to user.
    """
    service = InvitationService(db)
    invitation = service.send_invitation(org_id, current_user.id, data)
    return invitation


@router.get(
    "/organizations/{org_id}/members",
    status_code=status.HTTP_200_OK,
    summary="Get organization members",
    description="Get all members of an organization"
)
def get_organization_members(
    org_id: UUID,
    role_filter: Optional[UUID] = Query(None, description="Filter by role ID"),
    status_filter: Optional[MemberStatus] = Query(None, description="Filter by member status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get organization members.
    
    All organization members can view member list.
    
    Supports filtering by role and status.
    Returns paginated results with metadata.
    """
    service = MemberService(db)
    members, total = service.get_members(
        org_id,
        current_user.id,
        role_filter=role_filter,
        status_filter=status_filter,
        page=page,
        limit=limit
    )
    
    return {
        "items": members,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 0
    }


@router.put(
    "/organizations/{org_id}/members/{user_id}/roles",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Update member roles",
    description="Update member's roles (supports multiple roles)"
)
def update_member_roles(
    org_id: UUID,
    user_id: UUID,
    data: UpdateMemberRolesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update member roles.
    
    Only OWNER/ADMIN can update member roles.
    
    - **roles**: List of role assignments with primary designation
    - **reason**: Optional reason for role change
    
    Member can have multiple roles, but exactly one must be primary.
    Cannot change OWNER/FSP_OWNER role.
    """
    service = MemberService(db)
    member = service.update_member_roles(org_id, current_user.id, user_id, data)
    return member


@router.delete(
    "/organizations/{org_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove member",
    description="Remove member from organization"
)
def remove_member(
    org_id: UUID,
    user_id: UUID,
    reason: Optional[str] = Query(None, description="Reason for removal"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove member from organization.
    
    Only OWNER/ADMIN can remove members.
    
    Cannot remove OWNER/FSP_OWNER.
    Cannot remove self.
    """
    service = MemberService(db)
    service.remove_member(org_id, current_user.id, user_id, reason)
    return None
