"""
Section models for Farm Audit Management in Uzhathunai v2.0.

Sections are logical groupings of parameters within audit templates.
Supports both system-defined and organization-specific sections with multilingual content.

Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Section(Base):
    """
    Sections - logical groupings of parameters within templates.
    Supports both system-defined and organization-specific sections.
    Matches DDL lines 1285-1296 for sections table.
    """
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    is_system_defined = Column(Boolean, default=True)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    owner_organization = relationship("Organization", foreign_keys=[owner_org_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    translations = relationship("SectionTranslation", back_populates="section", cascade="all, delete-orphan")


class SectionTranslation(Base):
    """
    Multilingual translations for sections.
    Provides name and description in different languages (English, Tamil, Malayalam).
    Matches DDL lines 1301-1310 for section_translations table.
    """
    __tablename__ = "section_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey('sections.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    section = relationship("Section", back_populates="translations")

    # Constraints
    __table_args__ = (
        UniqueConstraint("section_id", "language_code"),
    )
