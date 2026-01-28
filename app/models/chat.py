"""
Chat models for Uzhathunai v2.0.

Models match database schema from 008_chat_module.sql.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import ChatContextType, MessageType


class ChatChannel(Base):
    """
    Chat Channel model - Represents a conversation thread.
    """
    __tablename__ = "chat_channels"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Context
    context_type = Column(SQLEnum(ChatContextType, name='chat_context_type'), nullable=False)
    context_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    members = relationship("ChatChannelMember", back_populates="channel", cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ChatChannel(id={self.id}, context={self.context_type})>"


class ChatChannelMember(Base):
    """
    Chat Channel Member model - Links Organizations to Channels.
    """
    __tablename__ = "chat_channel_members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Keys
    channel_id = Column(UUID(as_uuid=True), ForeignKey('chat_channels.id', ondelete='CASCADE'))
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'))
    
    # Metadata
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    added_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('channel_id', 'organization_id', name='uq_channel_member_org'),
    )
    
    # Relationships
    channel = relationship("ChatChannel", back_populates="members")
    organization = relationship("Organization")
    adder = relationship("User", foreign_keys=[added_by])
    
    def __repr__(self):
        return f"<ChatChannelMember(channel={self.channel_id}, org={self.organization_id})>"


class ChatMessage(Base):
    """
    Chat Message model.
    """
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Keys
    channel_id = Column(UUID(as_uuid=True), ForeignKey('chat_channels.id', ondelete='CASCADE'))
    sender_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    sender_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id'))
    
    # Content
    message_type = Column(SQLEnum(MessageType, name='message_type'), default=MessageType.TEXT)
    content = Column(Text)
    media_url = Column(Text)
    is_system_message = Column(Boolean, default=False)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    
    # Relationships
    channel = relationship("ChatChannel", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    sender_org = relationship("Organization", foreign_keys=[sender_org_id])
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender={self.sender_id})>"
