"""
FSP Service models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- MasterService (lines 295-305)
- MasterServiceTranslation (lines 307-318)
- FSPServiceListing (lines 1070-1090)
- FSPApprovalDocument (new table for FSP approval workflow)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import ServiceStatus


class MasterService(Base):
    """
    Master services list model - matches DDL lines 295-305 exactly.
    
    System-defined list of services that FSP organizations can offer.
    """
    
    __tablename__ = "master_services"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Service information
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ServiceStatus, name='service_status'), default=ServiceStatus.ACTIVE)
    sort_order = Column(Integer, default=0)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    translations = relationship("MasterServiceTranslation", back_populates="service", cascade="all, delete-orphan")
    fsp_listings = relationship("FSPServiceListing", back_populates="service")
    
    def __repr__(self):
        return f"<MasterService(id={self.id}, code={self.code}, name={self.name})>"


class MasterServiceTranslation(Base):
    """
    Master service translations model - matches DDL lines 307-318 exactly.
    
    Multilingual translations for master services.
    """
    
    __tablename__ = "master_service_translations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    service_id = Column(UUID(as_uuid=True), ForeignKey('master_services.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Translation information
    language_code = Column(String(10), nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    service = relationship("MasterService", back_populates="translations")
    
    def __repr__(self):
        return f"<MasterServiceTranslation(id={self.id}, service_id={self.service_id}, lang={self.language_code})>"


class FSPServiceListing(Base):
    """
    FSP service listing model - matches DDL lines 1070-1090 exactly.
    
    Organization-specific service listings for FSP marketplace.
    """
    
    __tablename__ = "fsp_service_listings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    fsp_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey('master_services.id'), nullable=False, index=True)
    
    # Service details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    service_area_districts = Column(ARRAY(Text))  # PostgreSQL array of districts
    
    # Pricing information
    pricing_model = Column(String(50))  # PER_HOUR, PER_DAY, PER_ACRE, FIXED, CUSTOM
    pricing_variants = Column(JSONB, default=[])  # Detailed pricing options
    base_price = Column(Numeric(15, 2))
    currency = Column(String(10), default='INR')
    
    # Status
    status = Column(SQLEnum(ServiceStatus, name='service_status'), default=ServiceStatus.ACTIVE, index=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    organization = relationship("Organization", back_populates="fsp_services")
    service = relationship("MasterService", back_populates="fsp_listings")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    # Computed properties for response serialization
    @property
    def service_code(self) -> str:
        """Get service code from related master service."""
        return self.service.code if self.service else None
    
    @property
    def service_name(self) -> str:
        """Get service name from related master service."""
        return self.service.name if self.service else None
    
    @property
    def service_description(self) -> str:
        """Get service description from related master service."""
        return self.service.description if self.service else None
    
    @property
    def pricing_unit(self) -> str:
        """Get human-readable pricing unit based on pricing model."""
        if not self.pricing_model:
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
        return mapping.get(self.pricing_model, self.pricing_model.lower().replace('_', ' '))

    def __repr__(self):
        return f"<FSPServiceListing(id={self.id}, org_id={self.fsp_organization_id}, service_id={self.service_id})>"


class FSPApprovalDocument(Base):
    """
    FSP approval document model for FSP organization approval workflow.
    
    Stores documents uploaded by FSP organizations for SuperAdmin review.
    """
    
    __tablename__ = "fsp_approval_documents"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    fsp_organization_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Document information
    document_type = Column(String(100), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(500))
    file_name = Column(String(255))
    
    # Audit fields
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    organization = relationship("Organization")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<FSPApprovalDocument(id={self.id}, org_id={self.fsp_organization_id}, type={self.document_type})>"
