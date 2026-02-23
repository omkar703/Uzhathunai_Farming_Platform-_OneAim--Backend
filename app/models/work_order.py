"""
Work Order models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- WorkOrder (lines 1076-1115)
- WorkOrderScope (lines 1117-1135)
"""
from datetime import datetime, date
from typing import Optional, List, Any
from sqlalchemy import Column, String, Text, Date, DateTime, Integer, Numeric, ForeignKey, Enum as SQLEnum, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import WorkOrderStatus, WorkOrderScopeType


class WorkOrder(Base):
    """
    Work order model - matches DDL lines 1076-1115 exactly.
    
    Represents a contract between farming and FSP organizations defining service scope,
    access permissions, and terms.
    """
    
    __tablename__ = "work_orders"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farming_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    fsp_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    service_listing_id = Column(UUID(as_uuid=True), ForeignKey('fsp_service_listings.id'))
    
    # Work order information
    work_order_number = Column(String(50), unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(WorkOrderStatus, name='work_order_status'), default=WorkOrderStatus.PENDING, index=True)
    terms_and_conditions = Column(Text)
    
    # Access control
    access_granted = Column(Boolean, default=True)
    
    # Scope metadata (JSONB summary)
    scope_metadata = Column(JSONB)
    
    # Duration
    start_date = Column(Date)
    end_date = Column(Date)
    
    # Payment information
    total_amount = Column(Numeric(15, 2))
    currency = Column(String(10), default='INR')
    pricing_unit = Column(String(50)) # Added for multiple pricing options
    
    # Service snapshot
    service_snapshot = Column(JSONB)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Status tracking
    accepted_at = Column(DateTime(timezone=True))
    accepted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    completed_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Completion details
    completion_notes = Column(Text)
    completion_photo_url = Column(String(500))
    
    # Assignment
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    farming_organization = relationship("Organization", foreign_keys=[farming_organization_id])
    fsp_organization = relationship("Organization", foreign_keys=[fsp_organization_id])
    service_listing = relationship("FSPServiceListing")
    scope_items = relationship("WorkOrderScope", back_populates="work_order", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="work_order", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    acceptor = relationship("User", foreign_keys=[accepted_by])
    assigned_member = relationship("User", foreign_keys=[assigned_to_user_id])
    
    @property
    def farming_organization_name(self) -> Optional[str]:
        """Get farming organization name."""
        return self.farming_organization.name if self.farming_organization else None

    @property
    def pricing_unit_label(self) -> str:
        """Get human-readable pricing unit label."""
        if not self.pricing_unit:
            return ""
            
        mapping = {
            'PER_HOUR': 'hour',
            'PER_DAY': 'day',
            'PER_ACRE': 'acre',
            'PER_YEAR': 'year',
            'PER_CROP': 'crop',
            'FIXED': 'fixed',
            'CUSTOM': 'custom'
        }
        return mapping.get(self.pricing_unit, self.pricing_unit.lower().replace('_', ' '))

    @property
    def fsp_organization_name(self) -> Optional[str]:
        """Get FSP organization name."""
        return self.fsp_organization.name if self.fsp_organization else None

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, number={self.work_order_number}, status={self.status})>"


class WorkOrderScope(Base):
    """
    Work order scope model - matches DDL lines 1117-1135 exactly.
    
    Defines specific resources (organization, farms, plots, crops) covered by a work order
    with associated access permissions.
    """
    
    __tablename__ = "work_order_scope"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    work_order_id = Column(UUID(as_uuid=True), ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Scope definition
    scope = Column(SQLEnum(WorkOrderScopeType, name='work_order_scope_type'), nullable=False, index=True)
    scope_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Access permissions (JSONB) - matches DDL default
    access_permissions = Column(JSONB, server_default='{"read": true, "write": false, "track": false}')
    
    # Ordering
    sort_order = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('work_order_id', 'scope', 'scope_id', name='uq_work_order_scope'),
    )
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="scope_items")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<WorkOrderScope(id={self.id}, work_order_id={self.work_order_id}, scope={self.scope})>"
