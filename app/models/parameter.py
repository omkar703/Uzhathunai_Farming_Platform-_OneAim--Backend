"""
Parameter models for Farm Audit Management in Uzhathunai v2.0.

Parameters are individual data points or questions within an audit, supporting multiple types
(text, numeric, single-select, multi-select, date). Supports both system-defined and 
organization-specific parameters.

Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class ParameterType(str, enum.Enum):
    """Parameter types matching DDL parameter_type ENUM."""
    TEXT = "TEXT"
    NUMERIC = "NUMERIC"
    SINGLE_SELECT = "SINGLE_SELECT"
    MULTI_SELECT = "MULTI_SELECT"
    DATE = "DATE"


class Parameter(Base):
    """
    Parameters library - individual data points or questions within an audit.
    Supports both system-defined and organization-specific parameters.
    Matches DDL lines 1238-1251 for parameters table.
    """
    __tablename__ = "parameters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    parameter_type = Column(Enum(ParameterType, name='parameter_type'), nullable=False)
    is_system_defined = Column(Boolean, default=True)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'))
    is_active = Column(Boolean, default=True)
    parameter_metadata = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # Relationships
    owner_organization = relationship("Organization", foreign_keys=[owner_org_id])
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    translations = relationship("ParameterTranslation", back_populates="parameter", cascade="all, delete-orphan")
    option_set_mappings = relationship("ParameterOptionSetMap", back_populates="parameter", cascade="all, delete-orphan")


class ParameterTranslation(Base):
    """
    Multilingual translations for parameters.
    Provides name, description, and help text in different languages (English, Tamil, Malayalam).
    Matches DDL lines 1259-1269 for parameter_translations table.
    """
    __tablename__ = "parameter_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey('parameters.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(String)
    help_text = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    parameter = relationship("Parameter", back_populates="translations")

    # Constraints
    __table_args__ = (
        UniqueConstraint("parameter_id", "language_code"),
    )


class ParameterOptionSetMap(Base):
    """
    Mapping between parameters and option sets.
    Associates option sets with SINGLE_SELECT and MULTI_SELECT parameters.
    Matches DDL lines 1273-1280 for parameter_option_set_map table.
    """
    __tablename__ = "parameter_option_set_map"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey('parameters.id', ondelete='CASCADE'), nullable=False)
    option_set_id = Column(UUID(as_uuid=True), ForeignKey('option_sets.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    parameter = relationship("Parameter", back_populates="option_set_mappings")
    option_set = relationship("OptionSet")

    # Constraints
    __table_args__ = (
        UniqueConstraint("parameter_id", "option_set_id"),
    )
