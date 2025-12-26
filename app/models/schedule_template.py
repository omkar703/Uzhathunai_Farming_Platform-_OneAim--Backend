"""
Schedule Template models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- ScheduleTemplate (lines 771-798)
- ScheduleTemplateTranslation (lines 800-813)
- ScheduleTemplateTask (lines 815-840)
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ScheduleTemplate(Base):
    """
    Schedule template model - matches DDL lines 771-798 exactly.
    
    Reusable schedule templates for crops (system-defined and organization-specific).
    """
    
    __tablename__ = "schedule_templates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template identification
    code = Column(String(50), nullable=False)
    
    # Foreign keys
    crop_type_id = Column(UUID(as_uuid=True), ForeignKey('crop_types.id'), index=True)
    crop_variety_id = Column(UUID(as_uuid=True), ForeignKey('crop_varieties.id'), index=True)
    
    # Ownership
    is_system_defined = Column(Boolean, default=True, index=True)
    owner_org_id = Column(UUID(as_uuid=True), ForeignKey('organizations.id', ondelete='CASCADE'), index=True)
    
    # Version control
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Notes
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            '(is_system_defined = true AND owner_org_id IS NULL) OR (is_system_defined = false AND owner_org_id IS NOT NULL)',
            name='chk_schedule_template_ownership'
        ),
        UniqueConstraint('code', 'is_system_defined', 'owner_org_id'),
    )
    
    # Relationships
    crop_type = relationship("CropType")
    crop_variety = relationship("CropVariety")
    owner_organization = relationship("Organization")
    tasks = relationship("ScheduleTemplateTask", back_populates="template", cascade="all, delete-orphan")
    translations = relationship("ScheduleTemplateTranslation", back_populates="template", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="template")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<ScheduleTemplate(id={self.id}, code={self.code}, is_system={self.is_system_defined})>"


class ScheduleTemplateTranslation(Base):
    """
    Schedule template translation model - matches DDL lines 800-813 exactly.
    
    Multilingual translations for schedule templates.
    """
    
    __tablename__ = "schedule_template_translations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    schedule_template_id = Column(UUID(as_uuid=True), ForeignKey('schedule_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Translation information
    language_code = Column(String(10), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('schedule_template_id', 'language_code'),
    )
    
    # Relationships
    template = relationship("ScheduleTemplate", back_populates="translations")
    
    def __repr__(self):
        return f"<ScheduleTemplateTranslation(id={self.id}, template_id={self.schedule_template_id}, lang={self.language_code})>"


class ScheduleTemplateTask(Base):
    """
    Schedule template task model - matches DDL lines 815-840 exactly.
    
    Tasks within schedule templates with calculation metadata.
    """
    
    __tablename__ = "schedule_template_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    schedule_template_id = Column(UUID(as_uuid=True), ForeignKey('schedule_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Task timing
    day_offset = Column(Integer, nullable=False, index=True)
    
    # Task details template (JSONB with calculation formulas)
    task_details_template = Column(JSONB, nullable=False)
    
    # Ordering
    sort_order = Column(Integer, default=0)
    
    # Notes
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    template = relationship("ScheduleTemplate", back_populates="tasks")
    task = relationship("Task")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<ScheduleTemplateTask(id={self.id}, template_id={self.schedule_template_id}, day_offset={self.day_offset})>"
