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
    UpdateMemberRolesRequest,
    MemberDetailsResponse,
    MemberWorkHistoryResponse,
    MemberPaginatedResponse
)
from app.schemas.invitation import InviteMemberRequest, InvitationResponse, SendInvitationRequest
from app.schemas.response import BaseResponse
from app.services.member_service import MemberService
from app.services.invitation_service import InvitationService

router = APIRouter()


@router.post(
    "/organizations/{org_id}/members/invite",
    response_model=BaseResponse[InvitationResponse],
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
    return {
        "success": True,
        "message": "Invitation sent successfully",
        "data": invitation
    }


@router.post(
    "/organizations/{org_id}/invitations",
    response_model=BaseResponse[InvitationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send invitation by user ID",
    description="Send an invitation to a specific user with a specific role"
)
def send_invitation_by_id(
    org_id: UUID,
    data: SendInvitationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send invitation by user ID and role code.
    
    - **userId**: UUID of user to invite
    - **role**: Role code to assign (e.g. 'WORKER', 'FSP_ADMIN')
    """
    service = InvitationService(db)
    invitation = service.send_invitation_by_user_id(
        org_id=org_id,
        inviter_id=current_user.id,
        user_id=data.userId,
        role_code=data.role
    )
    
    return {
        "success": True,
        "message": "Invitation sent successfully",
        "data": invitation
    }


@router.get(
    "/organizations/{org_id}/members",
    response_model=BaseResponse[MemberPaginatedResponse],
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
        "success": True,
        "message": "Members retrieved successfully",
        "data": {
            "items": members,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.put(
    "/organizations/{org_id}/members/{user_id}/roles",
    response_model=BaseResponse[MemberResponse],
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
    return {
        "success": True,
        "message": "Member roles updated successfully",
        "data": member
    }


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


@router.get(
    "/organizations/{org_id}/members/{user_id}",
    response_model=BaseResponse[MemberDetailsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get member details",
    description="Get comprehensive details about a specific organization member"
)
def get_member_details(
    org_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get member details.
    
    Returns comprehensive details about a specific organization member including:
    - User profile information (name, email, phone, bio, address, profile picture)
    - Role information
    - Membership status and joined date
    
    All organization members can view member details.
    """
    service = MemberService(db)
    details = service.get_member_details(org_id, user_id, current_user.id)
    return {
        "success": True,
        "message": "Member details retrieved successfully",
        "data": details
    }


@router.get(
    "/organizations/{org_id}/members/{user_id}/work-history",
    response_model=BaseResponse[MemberWorkHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get member work history",
    description="Get timeline of member's activities within the organization"
)
def get_member_work_history(
    org_id: UUID,
    user_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get member work history.
    
    Returns a paginated list of member activities including:
    - Task completions
    - Farm visits
    - Consultations  
    - Training sessions
    - Reports submitted
    
    All organization members can view work history.
    
    Note: Currently returns mock data. Future versions will pull from actual work orders,
    audits, and other activity logs.
    """
    service = MemberService(db)
    items, total = service.get_member_work_history(org_id, user_id, current_user.id, limit, offset)
    
    return {
        "success": True,
        "message": "Work history retrieved successfully",
        "data": {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    }
