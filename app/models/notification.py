"""
Notification model for user notifications.
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Notification type: VIDEO_CALL, WORK_ORDER, INVITATION, etc.
    type = Column(String(50), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Additional data as JSON (e.g., video call URL, work order ID, etc.)
    data = Column(JSON, nullable=True)
    
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Notification {self.id} - {self.type} for user {self.user_id}>"
