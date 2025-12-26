"""
Schedule API endpoints for Uzhathunai v2.0.

Handles schedule creation, copying, and task management.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import TaskStatus
from app.services.schedule_service import ScheduleService
from app.services.schedule_task_service import ScheduleTaskService
from app.schemas.schedule import (
    ScheduleFromTemplateCreate,
    ScheduleFromScratchCreate,
    ScheduleCopyRequest,
    ScheduleTaskCreate,
    ScheduleTaskUpdate,
    ScheduleTaskStatusUpdate,
    ScheduleResponse,
    ScheduleWithTasksResponse,
    ScheduleTaskResponse
)

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("/from-template", response_model=ScheduleResponse)
def create_schedule_from_template(
    data: ScheduleFromTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create schedule from template with automatic calculations.
    
    Validates: Requirement 6.1
    """
    service = ScheduleService(db)
    schedule = service.create_schedule_from_template(
        crop_id=data.crop_id,
        template_id=data.template_id,
        name=data.name,
        template_parameters=data.template_parameters,
        user=current_user
    )
    return schedule


@router.post("/from-scratch", response_model=ScheduleResponse)
def create_schedule_from_scratch(
    data: ScheduleFromScratchCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create schedule from scratch without template.
    
    Validates: Requirement 7.1
    """
    service = ScheduleService(db)
    schedule = service.create_schedule_from_scratch(
        crop_id=data.crop_id,
        name=data.name,
        description=data.description,
        user=current_user
    )
    return schedule


@router.post("/{schedule_id}/copy", response_model=ScheduleResponse)
def copy_schedule(
    schedule_id: UUID,
    data: ScheduleCopyRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Copy schedule to new crop with date adjustment.
    
    Validates: Requirement 8.1
    """
    service = ScheduleService(db)
    schedule = service.copy_schedule(
        source_schedule_id=schedule_id,
        target_crop_id=data.target_crop_id,
        new_start_date=data.new_start_date,
        user=current_user
    )
    return schedule


@router.get("", response_model=dict)
def get_schedules(
    crop_id: Optional[UUID] = Query(None, description="Filter by crop ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get schedules with pagination and access control.
    
    Returns paginated list of schedules.
    """
    service = ScheduleService(db)
    schedules, total = service.get_schedules(
        user=current_user,
        crop_id=crop_id,
        page=page,
        limit=limit
    )
    
    return {
        "items": schedules,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{schedule_id}", response_model=ScheduleWithTasksResponse)
def get_schedule(
    schedule_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get schedule details with tasks."""
    from app.models.schedule import Schedule
    from app.core.exceptions import NotFoundError
    
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.is_active == True
    ).first()
    
    if not schedule:
        raise NotFoundError(
            message=f"Schedule {schedule_id} not found",
            error_code="SCHEDULE_NOT_FOUND",
            details={"schedule_id": str(schedule_id)}
        )
    
    return schedule


@router.post("/{schedule_id}/tasks", response_model=ScheduleTaskResponse)
def create_schedule_task(
    schedule_id: UUID,
    data: ScheduleTaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task in schedule.
    
    Validates: Requirement 9.10
    """
    service = ScheduleTaskService(db)
    task = service.create_schedule_task(
        schedule_id=schedule_id,
        task_id=data.task_id,
        due_date=data.due_date,
        task_details=data.task_details,
        notes=data.notes,
        user=current_user
    )
    return task


@router.get("/{schedule_id}/tasks", response_model=list)
def get_schedule_tasks(
    schedule_id: UUID,
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks for schedule ordered by due date.
    
    Validates: Requirement 9.3
    """
    service = ScheduleTaskService(db)
    tasks = service.get_schedule_tasks(
        schedule_id=schedule_id,
        status=status
    )
    return tasks


@router.put("/tasks/{task_id}", response_model=ScheduleTaskResponse)
def update_schedule_task(
    task_id: UUID,
    data: ScheduleTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update schedule task.
    
    Validates: Requirement 9.7, 9.8
    """
    service = ScheduleTaskService(db)
    task = service.update_schedule_task(
        task_id=task_id,
        due_date=data.due_date,
        task_details=data.task_details,
        notes=data.notes,
        user=current_user
    )
    return task


@router.put("/tasks/{task_id}/status", response_model=ScheduleTaskResponse)
def update_task_status(
    task_id: UUID,
    data: ScheduleTaskStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update task status with transition validation.
    
    Validates: Requirement 9.4
    """
    service = ScheduleTaskService(db)
    task = service.update_task_status(
        task_id=task_id,
        new_status=data.status,
        completed_date=data.completed_date,
        user=current_user
    )
    return task
