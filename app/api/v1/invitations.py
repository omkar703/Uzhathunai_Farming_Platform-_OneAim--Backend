"""
Invitation API endpoints for Uzhathunai v2.0.
Handles organization invitation operations.
"""
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import InvitationStatus
from app.schemas.invitation import InvitationResponse, AcceptInvitationRequest
from app.schemas.response import BaseResponse
from app.services.invitation_service import InvitationService

router = APIRouter()


@router.get(
    "/me",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get my invitations",
    description="Get invitations for current user"
)
def get_my_invitations(
    status_filter: Optional[InvitationStatus] = Query(None, description="Filter by invitation status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get invitations for current user.
    """
    service = InvitationService(db)
    invitations, total = service.get_user_invitations(
        current_user.email,
        status_filter=status_filter,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "message": "Invitations retrieved successfully",
        "data": {
            "items": invitations,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if total > 0 else 0
        }
    }


@router.get(
    "/my-invitations",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
def get_my_invitations_alias(
    status_filter: Optional[InvitationStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Alias for /me endpoint to match frontend expectation."""
    return get_my_invitations(status_filter, page, limit, current_user, db)


@router.post(
    "/{invitation_id}/accept",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Accept invitation",
    description="Accept organization invitation or approve join request with optional role assignment"
)
def accept_invitation(
    invitation_id: UUID,
    request: AcceptInvitationRequest = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Accept organization invitation or approve join request.
    
    Creates organization membership and assigns role.
    
    **For Join Requests (Admin approving):**
    - Can optionally specify role_id to override default role
    - If no role_id provided, uses invitation's default role
    
    **For Standard Invitations (User accepting):**
    - role_id parameter is ignored (uses invitation's role)
    
    Invitation must be PENDING and not expired.
    """
    service = InvitationService(db)
    role_id = request.role_id if request else None
    result = service.accept_invitation(invitation_id, current_user.id, role_id=role_id)
    return {
        "success": True,
        "message": "Invitation accepted successfully",
        "data": result
    }


@router.post(
    "/{invitation_id}/reject",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Reject invitation",
    description="Reject organization invitation"
)
def reject_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reject organization invitation.
    
    Updates invitation status to REJECTED.
    
    Invitation must be PENDING.
    """
    service = InvitationService(db)
    result = service.reject_invitation(invitation_id, current_user.id)
    return {
        "success": True,
        "message": "Invitation rejected successfully",
        "data": result
    }
