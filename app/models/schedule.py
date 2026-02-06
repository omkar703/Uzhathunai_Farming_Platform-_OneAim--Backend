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
    
    @property
    def start_date(self):
        """Extract start_date from template_parameters or fallback to created_at."""
        if self.template_parameters and isinstance(self.template_parameters, dict):
            sd = self.template_parameters.get('start_date')
            if sd:
                try:
                    from datetime import date
                    return date.fromisoformat(sd)
                except:
                    pass
        return self.created_at.date() if self.created_at else None

    @property
    def total_tasks(self):
        """Total count of tasks in this schedule."""
        return len(self.tasks) if self.tasks else 0

    @property
    def completed_tasks(self):
        """Count of completed tasks."""
        if not self.tasks:
            return 0
        from app.models.enums import TaskStatus
        return len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])

    @property
    def items(self):
        """Alias for tasks to support frontend naming convention."""
        return self.tasks


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
    task_name = Column(String(200)) # Custom task name overriding the default
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

    @property
    def task_type_name(self):
        """Get the name of the underlying task Type."""
        return self.task.name if self.task else "Unknown Task"
    
    # Keeping task_name property as a bridge if needed? 
    # Actually, if I have a column named task_name, the property must be removed or renamed.
    # Let's rename the property to task_default_name if we want to keep it, 
    # but the frontend expects 'task_name' in the response.
    # The Pydantic model will pick up the 'task_name' column.
    # Let's just remove the property and handle fallback in the service or schema if needed.
    # However, 'task_name' as a property was useful for display.
    # I'll rename the column to 'custom_task_name' internally if I want to keep the property 'task_name'.
    # But the user specifically said "task_name column".
    
    # Decision: Rename the property to avoid conflict, 
    # and maybe add a fallback in the service logic.
    @property
    def display_task_name(self):
        """Get the custom name or fallback to task type name."""
        return self.task_name or (self.task.name if self.task else "Unknown Task")
    
    @property
    def input_item_name(self):
        """Get the input item name from task_details if present."""
        if self.task_details and isinstance(self.task_details, dict):
            # Try to get from calculated input_items
            items = self.task_details.get('input_items', [])
            if items and isinstance(items, list) and len(items) > 0:
                name = items[0].get('input_item_name')
                if name: return name
            
            # Try to get from concentration
            conc = self.task_details.get('concentration', {})
            if conc and isinstance(conc, dict):
                ings = conc.get('ingredients', [])
                if ings and len(ings) > 0:
                    name = ings[0].get('input_item_name')
                    if name: return name
        return None

    @property
    def application_method_name(self):
        """Get the application method name from task_details if present."""
        if self.task_details and isinstance(self.task_details, dict):
            return self.task_details.get('application_method_name')
        return None

    @property
    def scheduled_date(self):
        """Alias for due_date to match frontend naming."""
        return self.due_date


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
