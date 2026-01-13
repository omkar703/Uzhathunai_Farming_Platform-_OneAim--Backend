"""
Option Set models for Farm Audit Management in Uzhathunai v2.0.

Option sets are reusable collections of options that can be associated with parameters
for single-select or multi-select responses. Supports both system-defined and 
organization-specific option sets.

Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class OptionSet(Base):
    """
    Option sets - reusable collections of options for parameters.
    Supports both system-defined and organization-specific option sets.
    Matches DDL lines 1197-1211 for option_sets table.
    """
    __tablename__ = "option_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    is_system_defined = Column(Boolean, default=True)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    owner_organization = relationship("Organization", foreign_keys=[owner_org_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    options = relationship("Option", back_populates="option_set", cascade="all, delete-orphan")


class Option(Base):
    """
    Individual options within an option set.
    Each option has multilingual display text via option_translations.
    Matches DDL lines 1213-1223 for options table.
    """
    __tablename__ = "options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_set_id = Column(UUID(as_uuid=True), ForeignKey('option_sets.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    option_set = relationship("OptionSet", back_populates="options")
    translations = relationship("OptionTranslation", back_populates="option", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint("option_set_id", "code"),
    )


class OptionTranslation(Base):
    """
    Multilingual translations for options.
    Provides display text in different languages (English, Tamil, Malayalam).
    Matches DDL lines 1225-1234 for option_translations table.
    """
    __tablename__ = "option_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_id = Column(UUID(as_uuid=True), ForeignKey('options.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    display_text = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    option = relationship("Option", back_populates="translations")

    # Constraints
    __table_args__ = (
        UniqueConstraint("option_id", "language_code"),
    )
