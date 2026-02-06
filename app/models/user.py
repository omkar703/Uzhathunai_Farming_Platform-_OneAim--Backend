"""
User model and related authentication models for Uzhathunai v2.0.
"""
from datetime import datetime
from typing import Optional, ClassVar
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """
    User model for authentication and profile management.
    
    Matches database schema from 001_uzhathunai_ddl.sql:
    - first_name, last_name (not full_name)
    - phone (not phone_number)
    - preferred_language (not language_preference)
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20), index=True)
    bio = Column(Text)
    address = Column(Text)
    specialization = Column(String(200))
    profile_picture_url = Column(String(500))
    
    # Preferences
    preferred_language = Column(String(10), default='en')
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Runtime attributes (not persisted)
    _is_system_user: ClassVar[bool] = False
    current_organization_id: ClassVar[Optional[uuid.UUID]] = None
    
    def is_system_user(self) -> bool:
        """Check if user has system-level privileges."""
        return getattr(self, '_is_system_user', False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"
    
    @property
    def full_name(self) -> str:
        """Get full name from first_name and last_name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        from app.core.security import verify_password as verify_pwd
        return verify_pwd(password, self.password_hash)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses."""
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "bio": self.bio,
            "address": self.address,
            "specialization": self.specialization,
            "profile_picture_url": self.profile_picture_url,
            "preferred_language": self.preferred_language,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class RefreshToken(Base):
    """
    Refresh token model for JWT token management.
    
    Matches database schema from 002_create_refresh_tokens_table.sql
    """
    
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Token data
    token_hash = Column(String(255), nullable=False)
    device_info = Column(JSONB, default={})
    
    # Expiry and revocation
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, index=True)
    revoked_at = Column(DateTime(timezone=True))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() < self.expires_at.replace(tzinfo=None) if self.expires_at else True
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)."""
        return not self.is_revoked and not self.is_expired
