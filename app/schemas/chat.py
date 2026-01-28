"""
Chat schemas for Uzhathunai v2.0.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

from app.models.enums import ChatContextType, MessageType, OrganizationType


class ChatChannelCreate(BaseModel):
    """Schema for creating a chat channel."""
    participant_org_id: UUID
    context_type: ChatContextType
    context_id: UUID
    name: Optional[str] = None


class ChatMessageCreate(BaseModel):
    """Schema for sending a chat message."""
    content: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None
    
    @validator('content')
    def validate_content(cls, v, values):
        """Validate content based on message type."""
        message_type = values.get('message_type')
        if message_type == MessageType.TEXT and not v:
            raise ValueError('Content is required for text messages')
        return v


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: str
    channel_id: str
    sender_id: str
    sender_org_id: Optional[str]
    sender_name: Optional[str] = None # Enriched field
    sender_org_name: Optional[str] = None # Enriched field
    message_type: MessageType
    content: Optional[str]
    media_url: Optional[str]
    is_system_message: bool
    created_at: datetime
    
    @validator('id', 'channel_id', 'sender_id', 'sender_org_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class ChatChannelResponse(BaseModel):
    """Schema for chat channel response."""
    id: str
    context_type: ChatContextType
    context_id: str
    name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message: Optional[ChatMessageResponse] = None
    participants: List[dict] = Field(default_factory=list) # List of organization info
    
    @validator('id', 'context_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class ChatMessageListResponse(BaseModel):
    """Schema for paginated message list."""
    items: List[ChatMessageResponse]
    total: int
    page: int
    limit: int
    total_pages: int
