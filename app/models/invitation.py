"""
Invitation models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- OrgMemberInvitation (lines 165-180)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import InvitationStatus


class OrgMemberInvitation(Base):
    """
    Organization member invitation model - matches DDL lines 165-180 exactly.
    
    Manages email-based invitation workflow for adding members to organizations.
    """
    
    __tablename__ = "org_member_invitations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    invitee_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    
    # Invitation details
    invitee_email = Column(String(255), nullable=False, index=True)
    status = Column(SQLEnum(InvitationStatus, name='invitation_status'), default=InvitationStatus.PENDING, index=True)
    message = Column(Text)
    
    # Timestamps
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    responded_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[inviter_id])
    invitee_user = relationship("User", foreign_keys=[invitee_user_id])
    role = relationship("Role")
    
    def __repr__(self):
        return f"<OrgMemberInvitation(id={self.id}, email={self.invitee_email}, status={self.status})>"
