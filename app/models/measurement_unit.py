"""
Measurement Unit models for Uzhathunai v2.0.

Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, Numeric, ForeignKey, TIMESTAMP, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import MeasurementUnitCategory


class MeasurementUnit(Base):
    """
    Measurement units with categories (AREA, VOLUME, WEIGHT, LENGTH, COUNT).
    Matches DDL lines for measurement_units table.
    """
    __tablename__ = "measurement_units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(SQLEnum(MeasurementUnitCategory, name='measurement_unit_category'), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    symbol = Column(String(20))
    is_base_unit = Column(Boolean, default=False)
    conversion_factor = Column(Numeric(20, 10))  # Factor to convert to base unit
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    translations = relationship("MeasurementUnitTranslation", back_populates="measurement_unit", cascade="all, delete-orphan")


class MeasurementUnitTranslation(Base):
    """
    Multilingual translations for measurement units.
    Matches DDL lines for measurement_unit_translations table.
    """
    __tablename__ = "measurement_unit_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    measurement_unit_id = Column(UUID(as_uuid=True), ForeignKey('measurement_units.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    measurement_unit = relationship("MeasurementUnit", back_populates="translations")

    __table_args__ = (
        {'schema': None}  # Use default schema
    )
