
from sqlalchemy import Column, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class AuditReport(Base):
    """
    Audit Report model for storing rich text reports.
    
    Stores formatted HTML content and image references for an audit.
    One-to-one relationship with Audit.
    """
    __tablename__ = "audit_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False, unique=True)
    report_html = Column(Text, nullable=True)
    report_images = Column(JSONB, default=list, nullable=True) # List of image URLs
    pdf_url = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    audit = relationship("Audit", back_populates="report")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<AuditReport(id={self.id}, audit_id={self.audit_id})>"
