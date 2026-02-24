"""
Notification model for user notifications.
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base
from app.models.enums import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Notification type: VIDEO_CALL, WORK_ORDER, INVITATION, etc. (Internal reference)
    type = Column(String(100), nullable=True)
    
    # Database required notification_type enum: INFO, SUCCESS, WARNING, ALERT, REMINDER, ERROR
    notification_type = Column(SQLEnum(NotificationType, name="notification_type"), nullable=False, default=NotificationType.INFO, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Reference to entities
    reference_type = Column(String(50), nullable=True) # QUERY, WORK_ORDER, AUDIT, etc.
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Additional data as JSON
    data = Column(JSON, nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    
    is_push_sent = Column(Boolean, default=False)
    push_sent_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Notification {self.id} - {self.notification_type}:{self.type} for user {self.user_id}>"
