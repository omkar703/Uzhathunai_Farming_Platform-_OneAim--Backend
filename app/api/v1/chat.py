"""
Chat API endpoints for Uzhathunai v2.0.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.response import BaseResponse
from app.schemas.chat import (
    ChatChannelCreate,
    ChatChannelResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageListResponse
)
from app.services.chat_service import ChatService
from app.models.enums import ChatContextType

router = APIRouter()


@router.post(
    "/channels",
    response_model=BaseResponse[ChatChannelResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create chat channel",
    description="Create a new chat channel for a specific context (e.g. WORK_ORDER)"
)
def create_channel(
    data: ChatChannelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a chat channel.
    
    If context is WORK_ORDER, automatically adds FSP and Farming Org as participants.
    """
    service = ChatService(db)
    
    # Logic to determine participants based on context
    participant_org_ids = []
    
    if data.context_type == ChatContextType.WORK_ORDER:
        from app.services.work_order_service import WorkOrderService
        wo_service = WorkOrderService(db)
        wo = wo_service.get_work_order(data.context_id, current_user.id)
        participant_org_ids = [wo.farming_organization_id, wo.fsp_organization_id]
        
    # Validation: Ensure user belongs to one of the participant orgs?
    # Service logic handles members creation.
    
    channel = service.create_channel(
        user_id=current_user.id,
        data=data,
        participant_org_ids=participant_org_ids
    )
    
    return {
        "success": True,
        "message": "Chat channel created successfully",
        "data": channel
    }


@router.get(
    "/channels",
    response_model=BaseResponse[List[ChatChannelResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get user channels",
    description="Get list of chat channels the user has access to"
)
def get_channels(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user channels."""
    service = ChatService(db)
    channels, total = service.get_user_channels(current_user.id, page, limit)
    
    return {
        "success": True,
        "message": "Channels retrieved successfully",
        "data": channels
    }


@router.post(
    "/channels/{channel_id}/messages",
    response_model=BaseResponse[ChatMessageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
    description="Send a message to a channel"
)
def send_message(
    channel_id: UUID,
    data: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send message."""
    service = ChatService(db)
    message = service.send_message(channel_id, current_user.id, data)
    
    # Enrich response with sender info
    # (Usually handled by schema from_orm / relationship loading, 
    # but explicit enrichment if simple schema mapping isn't enough - here relationships exist)
    
    return {
        "success": True,
        "message": "Message sent successfully",
        "data": message
    }


@router.get(
    "/channels/{channel_id}/messages",
    response_model=BaseResponse[ChatMessageListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get messages",
    description="Get messages from a channel"
)
def get_messages(
    channel_id: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages."""
    service = ChatService(db)
    messages, total = service.get_messages(channel_id, current_user.id, page, limit)
    
    return {
        "success": True,
        "message": "Messages retrieved successfully",
        "data": {
            "items": messages,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    }
