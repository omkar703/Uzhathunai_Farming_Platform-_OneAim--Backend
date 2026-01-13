"""
Audit models for Farm Audit Management System in Uzhathunai v2.0.

Audits are instances of templates created for specific crops. They support offline operations
with sync status tracking, immutable snapshots, and complete audit lifecycle management.

Models match the database schema exactly from 001_uzhathunai_ddl.sql and 003_audit_module_changes.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text, Date, Enum as SQLEnum, ARRAY, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import AuditStatus, SyncStatus, IssueSeverity, PhotoSourceType


class Audit(Base):
    """
    Audit model - Instance of a template created for a specific crop.
    
    Audits capture immutable snapshots of templates at creation time and track
    the complete audit lifecycle from DRAFT to SHARED. Supports offline operations
    with sync_status tracking.
    
    Matches DDL lines 1374-1398 from 001_uzhathunai_ddl.sql
    and sync_status addition from 003_audit_module_changes.sql
    """
    __tablename__ = "audits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fsp_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    farming_organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    work_order_id = Column(UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=True)  # Made nullable in 003
    crop_id = Column(UUID(as_uuid=True), ForeignKey("crops.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    audit_number = Column(String(50), unique=True, nullable=True)
    name = Column(String(200), nullable=False)
    status = Column(SQLEnum(AuditStatus, name='audit_status'), default=AuditStatus.DRAFT, nullable=False)
    template_snapshot = Column(JSONB, nullable=True)
    audit_date = Column(Date, nullable=True)
    sync_status = Column(SQLEnum(SyncStatus, name='sync_status'), default=SyncStatus.SYNCED, nullable=True)  # Added in 003
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    finalized_at = Column(TIMESTAMP(timezone=True), nullable=True)
    finalized_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    shared_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    fsp_organization = relationship("Organization", foreign_keys=[fsp_organization_id])
    farming_organization = relationship("Organization", foreign_keys=[farming_organization_id])
    work_order = relationship("WorkOrder", foreign_keys=[work_order_id])
    crop = relationship("Crop", foreign_keys=[crop_id])
    template = relationship("Template", foreign_keys=[template_id])
    creator = relationship("User", foreign_keys=[created_by])
    finalizer = relationship("User", foreign_keys=[finalized_by])
    parameter_instances = relationship("AuditParameterInstance", back_populates="audit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Audit(id={self.id}, audit_number={self.audit_number}, status={self.status})>"


class AuditParameterInstance(Base):
    """
    Audit parameter instance model - Snapshot of parameters for each audit.
    
    Each audit creates instances of all parameters from the template with complete
    configuration snapshots. This ensures audit data remains consistent even if
    the template or parameters are modified later.
    
    Matches DDL lines 1407-1424 from 001_uzhathunai_ddl.sql
    """
    __tablename__ = "audit_parameter_instances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    template_section_id = Column(UUID(as_uuid=True), ForeignKey("template_sections.id"), nullable=False)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey("parameters.id"), nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    parameter_snapshot = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    audit = relationship("Audit", back_populates="parameter_instances")
    template_section = relationship("TemplateSection", foreign_keys=[template_section_id])
    parameter = relationship("Parameter", foreign_keys=[parameter_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<AuditParameterInstance(id={self.id}, audit_id={self.audit_id}, parameter_id={self.parameter_id})>"


class AuditResponse(Base):
    """
    Audit response model - Auditor responses to audit parameters.
    
    Stores responses for different parameter types:
    - TEXT: response_text
    - NUMERIC: response_numeric
    - DATE: response_date
    - SINGLE_SELECT/MULTI_SELECT: response_options (array of option IDs)
    
    Matches DDL lines 1425-1442 from 001_uzhathunai_ddl.sql
    """
    __tablename__ = "audit_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    audit_parameter_instance_id = Column(UUID(as_uuid=True), ForeignKey("audit_parameter_instances.id", ondelete="CASCADE"), nullable=False)
    response_text = Column(Text, nullable=True)
    response_numeric = Column(DECIMAL(15, 4), nullable=True)
    response_date = Column(Date, nullable=True)
    response_options = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # Array of option IDs
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    audit = relationship("Audit", foreign_keys=[audit_id])
    parameter_instance = relationship("AuditParameterInstance", foreign_keys=[audit_parameter_instance_id])
    creator = relationship("User", foreign_keys=[created_by])
    photos = relationship("AuditResponsePhoto", back_populates="response", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AuditResponse(id={self.id}, audit_id={self.audit_id}, parameter_instance_id={self.audit_parameter_instance_id})>"


class AuditResponsePhoto(Base):
    """
    Audit response photo model - Photos attached by auditor to audit responses.
    
    Stores photo metadata including file URLs, captions, and upload information.
    Photos are stored in S3 with file_url and file_key references.
    
    Matches DDL lines 1445-1456 from 001_uzhathunai_ddl.sql
    """
    __tablename__ = "audit_response_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=True, index=True)
    audit_response_id = Column(UUID(as_uuid=True), ForeignKey("audit_responses.id", ondelete="CASCADE"), nullable=True)
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(500), nullable=True)
    caption = Column(Text, nullable=True)
    source_type = Column(SQLEnum(PhotoSourceType, name='photo_source_type'), default=PhotoSourceType.MANUAL_UPLOAD, nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    audit = relationship("Audit", foreign_keys=[audit_id])
    response = relationship("AuditResponse", back_populates="photos")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def __repr__(self):
        return f"<AuditResponsePhoto(id={self.id}, response_id={self.audit_response_id})>"


class AuditReview(Base):
    """
    Audit review model - Reviewer responses that override or supplement auditor responses.
    
    Reviewers can modify response values and flag responses for report inclusion.
    Enforces one review per audit response via UNIQUE constraint.
    
    Matches DDL lines 1460-1477 from 001_uzhathunai_ddl.sql
    """
    __tablename__ = "audit_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_response_id = Column(UUID(as_uuid=True), ForeignKey("audit_responses.id", ondelete="CASCADE"), nullable=False, unique=True)
    response_text = Column(Text, nullable=True)
    response_numeric = Column(DECIMAL(15, 4), nullable=True)
    response_date = Column(Date, nullable=True)
    response_option_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)  # Array of option IDs
    is_flagged_for_report = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    audit_response = relationship("AuditResponse", foreign_keys=[audit_response_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<AuditReview(id={self.id}, response_id={self.audit_response_id}, flagged={self.is_flagged_for_report})>"


class AuditReviewPhoto(Base):
    """
    Audit review photo model - Reviewer annotations on auditor photos.
    
    Reviewers can flag photos for report inclusion and add/modify captions.
    
    Matches DDL lines 1480-1492 from 001_uzhathunai_ddl.sql
    """
    __tablename__ = "audit_review_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_response_photo_id = Column(UUID(as_uuid=True), ForeignKey("audit_response_photos.id", ondelete="CASCADE"), nullable=False)
    is_flagged_for_report = Column(Boolean, default=False, nullable=False)
    caption = Column(Text, nullable=True)
    reviewed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    audit_response_photo = relationship("AuditResponsePhoto", foreign_keys=[audit_response_photo_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<AuditReviewPhoto(id={self.id}, photo_id={self.audit_response_photo_id}, flagged={self.is_flagged_for_report})>"


class AuditIssue(Base):
    """
    Audit issue model - Problems or observations identified during audit review or finalization.
    
    Issues are categorized by severity (LOW, MEDIUM, HIGH, CRITICAL) and can be created
    during SUBMITTED, REVIEWED, and FINALIZED audit statuses.
    
    Matches DDL lines 1495-1505 from 001_uzhathunai_ddl.sql
    Modified by 003_audit_module_changes.sql to use issue_severity ENUM
    """
    __tablename__ = "audit_issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(SQLEnum(IssueSeverity, name='issue_severity'), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    audit = relationship("Audit", foreign_keys=[audit_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<AuditIssue(id={self.id}, audit_id={self.audit_id}, severity={self.severity}, title={self.title})>"
