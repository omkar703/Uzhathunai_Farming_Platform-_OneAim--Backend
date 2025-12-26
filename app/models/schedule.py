"""
Schedule models for Uzhathunai v2.0.

Models match database schema exactly from 001_uzhathunai_ddl.sql:
- Schedule (lines 841-860)
- ScheduleTask (lines 862-888)
- TaskActual (lines 890-925)
- TaskPhoto (lines 927-940)
- ScheduleChangeLog (lines 942-960)
"""
from datetime import datetime, date
from sqlalchemy import Column, String, Text, Date, DateTime, Integer, Boolean, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base
from app.models.enums import TaskStatus, ScheduleChangeTrigger


class Schedule(Base):
    """
    Schedule model - matches DDL lines 841-860 exactly.
    
    Crop schedules created from templates or from scratch.
    """
    
    __tablename__ = "schedules"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey('schedule_templates.id'), index=True)
    
    # Schedule information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_parameters = Column(JSONB)
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    crop = relationship("Crop")
    template = relationship("ScheduleTemplate", back_populates="schedules")
    tasks = relationship("ScheduleTask", back_populates="schedule", cascade="all, delete-orphan")
    task_actuals = relationship("TaskActual", back_populates="schedule")
    change_logs = relationship("ScheduleChangeLog", back_populates="schedule", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, name={self.name}, crop_id={self.crop_id})>"


class ScheduleTask(Base):
    """
    Schedule task model - matches DDL lines 862-888 exactly.
    
    Individual tasks within a schedule with status tracking.
    """
    
    __tablename__ = "schedule_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Task information
    due_date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(TaskStatus, name='task_status'), default=TaskStatus.NOT_STARTED, index=True)
    completed_date = Column(Date)
    task_details = Column(JSONB)
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    schedule = relationship("Schedule", back_populates="tasks")
    task = relationship("Task")
    actuals = relationship("TaskActual", back_populates="schedule_task")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<ScheduleTask(id={self.id}, schedule_id={self.schedule_id}, due_date={self.due_date})>"


class TaskActual(Base):
    """
    Task actual model - matches DDL lines 890-925 exactly.
    
    Consolidated table for both planned and adhoc task actuals.
    """
    
    __tablename__ = "task_actuals"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.id'), index=True)
    schedule_task_id = Column(UUID(as_uuid=True), ForeignKey('schedule_tasks.id', ondelete='CASCADE'), index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Task type
    is_planned = Column(Boolean, nullable=False, index=True)
    
    # Resource associations
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), index=True)
    plot_id = Column(UUID(as_uuid=True), ForeignKey('plots.id'), index=True)
    
    # Actual information
    actual_date = Column(Date, nullable=False, index=True)
    task_details = Column(JSONB)
    notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Constraint
    __table_args__ = (
        CheckConstraint(
            '(is_planned = true AND schedule_task_id IS NOT NULL) OR (is_planned = false AND schedule_task_id IS NULL)',
            name='chk_task_actuals_planned'
        ),
    )
    
    # Relationships
    schedule = relationship("Schedule", back_populates="task_actuals")
    schedule_task = relationship("ScheduleTask", back_populates="actuals")
    task = relationship("Task")
    crop = relationship("Crop")
    plot = relationship("Plot")
    photos = relationship("TaskPhoto", back_populates="task_actual", cascade="all, delete-orphan")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<TaskActual(id={self.id}, task_id={self.task_id}, is_planned={self.is_planned})>"


class TaskPhoto(Base):
    """
    Task photo model - matches DDL lines 927-940 exactly.
    
    Photos for task actuals (both planned and adhoc).
    """
    
    __tablename__ = "task_photos"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key
    task_actual_id = Column(UUID(as_uuid=True), ForeignKey('task_actuals.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Photo information
    file_url = Column(String(500), nullable=False)
    file_key = Column(String(500))
    caption = Column(Text)
    
    # Audit fields
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    task_actual = relationship("TaskActual", back_populates="photos")
    uploader = relationship("User")
    
    def __repr__(self):
        return f"<TaskPhoto(id={self.id}, task_actual_id={self.task_actual_id})>"


class ScheduleChangeLog(Base):
    """
    Schedule change log model - matches DDL lines 942-960 exactly.
    
    Audit trail for schedule modifications with trigger attribution.
    """
    
    __tablename__ = "schedule_change_log"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('schedules.id', ondelete='CASCADE'), nullable=False, index=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey('schedule_tasks.id'))
    
    # Trigger information
    trigger_type = Column(SQLEnum(ScheduleChangeTrigger, name='schedule_change_trigger'), nullable=False, index=True)
    trigger_reference_id = Column(UUID(as_uuid=True), index=True)
    
    # Change information
    change_type = Column(String(20), nullable=False)
    task_details_before = Column(JSONB)
    task_details_after = Column(JSONB)
    change_description = Column(Text)
    
    # Application tracking
    is_applied = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True))
    applied_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    schedule = relationship("Schedule", back_populates="change_logs")
    applier = relationship("User", foreign_keys=[applied_by])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<ScheduleChangeLog(id={self.id}, schedule_id={self.schedule_id}, change_type={self.change_type})>"
