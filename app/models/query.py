"""
Query models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- Query (lines 1130-1152)
- QueryResponse (lines 1159-1168)
- QueryPhoto (lines 1170-1188)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import QueryStatus


class Query(Base):
    """
    Query model - matches DDL lines 1130-1152 exactly.
    
    Requests for consultation or advice from farming organization to FSP.
    """
    
    __tablename__ = "queries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    farming_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    fsp_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    work_order_id = Column(UUID(as_uuid=True), ForeignKey('work_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Query information
    query_number = Column(String(50), unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Resource associations (optional)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.id'))
    plot_id = Column(UUID(as_uuid=True), ForeignKey('plots.id'))
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id'), index=True)
    
    # Status and priority
    status = Column(SQLEnum(QueryStatus, name='query_status'), default=QueryStatus.OPEN, index=True)
    priority = Column(String(20), default='MEDIUM')
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Resolution tracking
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    farming_organization = relationship("Organization", foreign_keys=[farming_organization_id])
    fsp_organization = relationship("Organization", foreign_keys=[fsp_organization_id])
    work_order = relationship("WorkOrder", back_populates="queries")
    farm = relationship("Farm")
    plot = relationship("Plot")
    crop = relationship("Crop")
    responses = relationship("QueryResponse", back_populates="query", cascade="all, delete-orphan")
    photos = relationship("QueryPhoto", back_populates="query", cascade="all, delete-orphan", foreign_keys="[QueryPhoto.query_id]")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<Query(id={self.id}, number={self.query_number}, status={self.status})>"


class QueryResponse(Base):
    """
    Query response model - matches DDL lines 1159-1168 exactly.
    
    FSP responses to queries with optional recommendations.
    """
    
    __tablename__ = "query_responses"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Response information
    response_text = Column(Text, nullable=False)
    has_recommendation = Column(Boolean, default=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    query = relationship("Query", back_populates="responses")
    photos = relationship("QueryPhoto", back_populates="response", cascade="all, delete-orphan", foreign_keys="[QueryPhoto.query_response_id]")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<QueryResponse(id={self.id}, query_id={self.query_id})>"


class QueryPhoto(Base):
    """
    Query photo model - matches DDL lines 1170-1188 exactly.
    
    Photos attached to queries (when submitted) or query responses (when FSP responds).
    """
    
    __tablename__ = "query_photos"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys (one must be set, not both)
    query_id = Column(UUID(as_uuid=True), ForeignKey('queries.id', ondelete='CASCADE'), index=True)
    query_response_id = Column(UUID(as_uuid=True), ForeignKey('query_responses.id', ondelete='CASCADE'), index=True)
    
    # Photo information
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(500))
    caption = Column(Text)
    
    # Audit fields
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Constraint
    __table_args__ = (
        CheckConstraint(
            '(query_id IS NOT NULL AND query_response_id IS NULL) OR (query_id IS NULL AND query_response_id IS NOT NULL)',
            name='chk_query_photos_reference'
        ),
    )
    
    # Relationships
    query = relationship("Query", back_populates="photos", foreign_keys=[query_id])
    response = relationship("QueryResponse", back_populates="photos", foreign_keys=[query_response_id])
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<QueryPhoto(id={self.id}, query_id={self.query_id}, response_id={self.query_response_id})>"
