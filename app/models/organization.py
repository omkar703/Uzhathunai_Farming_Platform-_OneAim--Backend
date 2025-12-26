"""
Organization models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- Organization (lines 115-135)
- OrgMember (lines 185-200)
- OrgMemberRole (lines 207-220)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Date, DateTime, Boolean, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus
)


class Organization(Base):
    """
    Organization model - matches DDL lines 115-135 exactly.
    
    Supports both FARMING and FSP organization types with multi-tenant operations.
    """
    
    __tablename__ = "organizations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    logo_url = Column(Text)
    organization_type = Column(SQLEnum(OrganizationType, name='organization_type'), nullable=False)
    status = Column(SQLEnum(OrganizationStatus, name='organization_status'), default=OrganizationStatus.NOT_STARTED)
    registration_number = Column(String(100))
    
    # Address information
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    
    # Contact information
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    
    # Subscription information
    subscription_plan_id = Column(UUID(as_uuid=True), ForeignKey('subscription_plans.id'))
    subscription_start_date = Column(Date)
    subscription_end_date = Column(Date)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    members = relationship("OrgMember", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("OrgMemberInvitation", back_populates="organization", cascade="all, delete-orphan")
    fsp_services = relationship("FSPServiceListing", back_populates="organization", cascade="all, delete-orphan")
    subscription_plan = relationship("SubscriptionPlan")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, type={self.organization_type})>"


class OrgMember(Base):
    """
    Organization member model - matches DDL lines 185-200 exactly.
    
    Represents membership of a user in an organization.
    """
    
    __tablename__ = "org_members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(MemberStatus, name='member_status'), default=MemberStatus.ACTIVE, index=True)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))
    
    # Invitation tracking
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    invitation_id = Column(UUID(as_uuid=True), ForeignKey('org_member_invitations.id'))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization", back_populates="members")
    roles = relationship(
        "OrgMemberRole",
        back_populates="member",
        cascade="all, delete-orphan",
        foreign_keys="[OrgMemberRole.user_id, OrgMemberRole.organization_id]",
        primaryjoin="and_(OrgMember.user_id==OrgMemberRole.user_id, OrgMember.organization_id==OrgMemberRole.organization_id)"
    )
    inviter = relationship("User", foreign_keys=[invited_by])
    invitation = relationship("OrgMemberInvitation")
    
    def __repr__(self):
        return f"<OrgMember(id={self.id}, user_id={self.user_id}, org_id={self.organization_id})>"


class OrgMemberRole(Base):
    """
    Organization member roles model - matches DDL lines 207-220 exactly.
    
    Supports multiple roles per member with primary role designation.
    """
    
    __tablename__ = "org_member_roles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    
    # Primary role flag
    is_primary = Column(Boolean, default=False)
    
    # Assignment tracking
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], overlaps="roles")
    organization = relationship("Organization", overlaps="roles")
    role = relationship("Role")
    assigner = relationship("User", foreign_keys=[assigned_by])
    member = relationship(
        "OrgMember",
        back_populates="roles",
        foreign_keys="[OrgMemberRole.user_id, OrgMemberRole.organization_id]",
        primaryjoin="and_(OrgMember.user_id==OrgMemberRole.user_id, OrgMember.organization_id==OrgMemberRole.organization_id)",
        viewonly=True
    )
    
    def __repr__(self):
        return f"<OrgMemberRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id}, is_primary={self.is_primary})>"
