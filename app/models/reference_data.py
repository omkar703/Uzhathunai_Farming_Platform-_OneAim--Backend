"""
Reference Data and Task models for Uzhathunai v2.0.

Models match the database schema exactly from 001_uzhathunai_ddl.sql.
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import TaskCategory


class Task(Base):
    """
    Predefined farming tasks (e.g., ploughing, weeding, fertigation).
    Matches DDL lines for tasks table.
    """
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    category = Column(SQLEnum(TaskCategory, name='task_category'), nullable=False)
    requires_input_items = Column(Boolean, default=False)
    requires_concentration = Column(Boolean, default=False)
    requires_machinery = Column(Boolean, default=False)
    requires_labor = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    translations = relationship("TaskTranslation", back_populates="task", cascade="all, delete-orphan")

    @property
    def name(self):
        """
        Return the display name from translations.
        Prioritizes English ('en'), then falls back to the first available translation.
        """
        if not self.translations:
            return self.code
        
        # Try to find English translation
        for t in self.translations:
            if t.language_code == 'en':
                return t.name
        
        # Fallback to first available translation
        return self.translations[0].name


class TaskTranslation(Base):
    """
    Multilingual translations for tasks.
    Matches DDL lines for task_translations table.
    """
    __tablename__ = "task_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Relationships
    task = relationship("Task", back_populates="translations")


class ReferenceDataType(Base):
    """
    Reference data types (e.g., soil_types, water_sources, irrigation_modes).
    Matches DDL lines for reference_data_types table.
    """
    __tablename__ = "reference_data_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    reference_data = relationship("ReferenceData", back_populates="type", cascade="all, delete-orphan")


class ReferenceData(Base):
    """
    Reference data values (e.g., specific soil types, water sources).
    Includes reference_metadata JSONB for type-specific attributes.
    Matches DDL lines for reference_data table.
    """
    __tablename__ = "reference_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_id = Column(UUID(as_uuid=True), ForeignKey('reference_data_types.id', ondelete='CASCADE'), nullable=False)
    code = Column(String(100), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    reference_metadata = Column(JSONB)  # {"capacity_liters": 50000, "depth_meters": 15, ...}
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    type = relationship("ReferenceDataType", back_populates="reference_data")
    translations = relationship("ReferenceDataTranslation", back_populates="reference_data", cascade="all, delete-orphan")

    @property
    def display_name(self):
        """
        Return the display name from translations.
        Prioritizes English ('en'), then falls back to the first available translation.
        """
        if not self.translations:
            return self.code  # Fallback to code if no translations
            
        # Try to find English translation
        for t in self.translations:
            if t.language_code == 'en':
                return t.display_name
                
        # Fallback to first available translation
        return self.translations[0].display_name


class ReferenceDataTranslation(Base):
    """
    Multilingual translations for reference data.
    Matches DDL lines for reference_data_translations table.
    """
    __tablename__ = "reference_data_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reference_data_id = Column(UUID(as_uuid=True), ForeignKey('reference_data.id', ondelete='CASCADE'), nullable=False)
    language_code = Column(String(10), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    reference_data = relationship("ReferenceData", back_populates="translations")
