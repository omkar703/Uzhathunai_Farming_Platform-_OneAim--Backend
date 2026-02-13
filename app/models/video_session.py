"""
Video Session model for Jitsi Meet integrations.
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
    Video Session model to track Jitsi Meet video calls.
    """
    __tablename__ = "video_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link to Work Order
    work_order_id = Column(UUID(as_uuid=True), ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Link to Audit (optional, for remote audits)
    audit_id = Column(UUID(as_uuid=True), ForeignKey('audits.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Jitsi Details
    room_name = Column(String(255), nullable=True, index=True)  # Jitsi room identifier
    join_url = Column(Text, nullable=True)  # Full Jitsi room URL (same for all participants)
    topic = Column(String(255), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # in minutes
    
    # Status
    status = Column(SQLEnum(VideoSessionStatus, name='video_session_status'), default=VideoSessionStatus.PENDING, index=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    work_order = relationship("WorkOrder")
    audit = relationship("Audit")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<VideoSession(id={self.id}, work_order={self.work_order_id}, status={self.status})>"
