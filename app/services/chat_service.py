"""
Chat service for Uzhathunai v2.0.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.chat import ChatChannel, ChatChannelMember, ChatMessage
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.enums import ChatContextType, MessageType, MemberStatus
from app.schemas.chat import ChatChannelCreate, ChatMessageCreate
from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, PermissionError, ValidationError

logger = get_logger(__name__)


class ChatService:
    """Service for In-App Chat."""
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(__name__)
        
    def create_channel(
        self,
        user_id: UUID,  # Creator
        data: ChatChannelCreate,
        participant_org_ids: List[UUID]
    ) -> ChatChannel:
        """
        Create a new chat channel and add participants.
        Ensure one channel per context (e.g. WorkOrder) usually.
        """
        # Validate User is member of one of the participant orgs with proper role?
        # For WorkOrder context, usually initiated by FSP or Farmer.
        
        # Check if channel already exists for this context
        existing = self.db.query(ChatChannel).filter(
            ChatChannel.context_type == data.context_type,
            ChatChannel.context_id == data.context_id
        ).first()
        
        if existing:
            return existing
            
        # Create Channel
        channel = ChatChannel(
            context_type=data.context_type,
            context_id=data.context_id,
            name=data.name,
            created_by=user_id,
            updated_by=user_id
        )
        self.db.add(channel)
        self.db.flush()
        
        # Add Members
        for org_id in participant_org_ids:
            member = ChatChannelMember(
                channel_id=channel.id,
                organization_id=org_id,
                added_by=user_id
            )
            self.db.add(member)
            
        self.db.commit()
        self.db.refresh(channel)
        return channel

    def get_user_channels(
        self,
        user_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[ChatChannel], int]:
        """
        Get channels for a user based on their organization memberships.
        """
        # 1. Get user's active organizations
        user_orgs = self.db.query(OrgMember.organization_id).filter(
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).subquery()
        
        # 2. Find channels where these organizations are members
        query = self.db.query(ChatChannel).join(
            ChatChannelMember,
            ChatChannel.members
        ).filter(
            ChatChannelMember.organization_id.in_(user_orgs),
            ChatChannel.is_active == True
        ).distinct()
        
        total = query.count()
        
        channels = query.order_by(
            ChatChannel.updated_at.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        return channels, total

    def send_message(
        self,
        channel_id: UUID,
        user_id: UUID,
        data: ChatMessageCreate
    ) -> ChatMessage:
        """
        Send a message to a channel.
        verify user is part of an organization that is a member of the channel.
        """
        # Verify Channel exists
        channel = self.db.query(ChatChannel).filter(ChatChannel.id == channel_id).first()
        if not channel:
            raise NotFoundError("Channel not found")
            
        # Identify User's Org in this channel
        # User must be an active member of an Org that is a member of this Channel
        user_org = self.db.query(Organization).join(
            OrgMember, Organization.id == OrgMember.organization_id
        ).join(
            ChatChannelMember, Organization.id == ChatChannelMember.organization_id
        ).filter(
            ChatChannelMember.channel_id == channel_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not user_org:
            raise PermissionError("User is not a member of this chat channel")
            
        # Create Message
        msg = ChatMessage(
            channel_id=channel_id,
            sender_id=user_id,
            sender_org_id=user_org.id,
            message_type=data.message_type,
            content=data.content,
            media_url=data.media_url
        )
        self.db.add(msg)
        
        # Update Channel timestamp
        channel.updated_at = msg.created_at
        channel.updated_by = user_id
        
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(
        self,
        channel_id: UUID,
        user_id: UUID,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[ChatMessage], int]:
        """
        Get messages for a channel.
        """
        # Validate Access (reuse logic or similar)
        # For read, just need to be in the channel
        has_access = self.db.query(ChatChannelMember).join(
            OrgMember, ChatChannelMember.organization_id == OrgMember.organization_id
        ).filter(
            ChatChannelMember.channel_id == channel_id,
            OrgMember.user_id == user_id,
            OrgMember.status == MemberStatus.ACTIVE
        ).first()
        
        if not has_access:
            raise PermissionError("Access denied")
            
        query = self.db.query(ChatMessage).filter(
            ChatMessage.channel_id == channel_id
        )
        
        total = query.count()
        
        # Messages usually loaded newest first (for UI to reverse) or oldest first?
        # API usually returns standard pagination. Let's do desc created_at
        messages = query.order_by(
            ChatMessage.created_at.desc()
        ).offset((page - 1) * limit).limit(limit).all()
        
        return messages, total
