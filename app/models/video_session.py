"""
Video Session model for Zoom integrations.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base

class VideoSessionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class VideoSession(Base):
    """
    Video Session model to track Zoom meetings.
    """
    __tablename__ = "video_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to Work Order
    work_order_id = Column(UUID(as_uuid=True), ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Zoom Details
    zoom_meeting_id = Column(String(50), nullable=True, index=True)
    join_url = Column(Text, nullable=True) # For participants
    start_url = Column(Text, nullable=True) # For host
    topic = Column(String(255), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True) # in minutes
    password = Column(String(50), nullable=True)
    
    # Status
    status = Column(SQLEnum(VideoSessionStatus, name='video_session_status'), default=VideoSessionStatus.PENDING, index=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    work_order = relationship("WorkOrder")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<VideoSession(id={self.id}, work_order={self.work_order_id}, status={self.status})>"
