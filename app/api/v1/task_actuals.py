"""
Task Actual API endpoints for Uzhathunai v2.0.

Endpoints for recording planned and adhoc task actuals with photo uploads.
"""
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.task_actual_service import TaskActualService
from app.services.schedule_change_log_service import ScheduleChangeLogService
from app.schemas.task_actual import (
    PlannedTaskActualCreate,
    AdhocTaskActualCreate,
    TaskPhotoCreate,
    TaskActualResponse,
    TaskPhotoResponse,
    ScheduleChangeLogResponse,
    ApplyProposedChangesRequest
)

router = APIRouter(prefix="/task-actuals", tags=["Task Actuals"])


@router.post("/planned", response_model=TaskActualResponse)
def record_planned_task_actual(
    data: PlannedTaskActualCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Record actual execution of a planned schedule task.
    
    Requirements: 10.1, 10.12
    """
    service = TaskActualService(db)
    
    task_actual = service.record_planned_task_actual(
        schedule_task_id=data.schedule_task_id,
        actual_date=data.actual_date,
        task_details=data.task_details,
        notes=data.notes,
        user_id=current_user.id,
        user_org_id=current_user.current_organization_id
    )
    
    return task_actual


@router.post("/adhoc", response_model=TaskActualResponse)
def record_adhoc_task_actual(
    data: AdhocTaskActualCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Record adhoc (unplanned) task execution.
    
    Requirements: 10.2
    """
    service = TaskActualService(db)
    
    task_actual = service.record_adhoc_task_actual(
        task_id=data.task_id,
        crop_id=data.crop_id,
        plot_id=data.plot_id,
        actual_date=data.actual_date,
        task_details=data.task_details,
        notes=data.notes,
        user_id=current_user.id,
        user_org_id=current_user.current_organization_id
    )
    
    return task_actual


@router.post("/{task_actual_id}/photos", response_model=TaskPhotoResponse)
def upload_task_photo(
    task_actual_id: UUID,
    data: TaskPhotoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload photo for task actual.
    
    Requirements: 10.8
    """
    service = TaskActualService(db)
    
    task_photo = service.upload_task_photo(
        task_actual_id=task_actual_id,
        file_url=data.file_url,
        file_key=data.file_key,
        caption=data.caption,
        user_id=current_user.id
    )
    
    return task_photo


@router.get("", response_model=dict)
def get_task_actuals(
    schedule_id: Optional[UUID] = Query(None),
    crop_id: Optional[UUID] = Query(None),
    plot_id: Optional[UUID] = Query(None),
    is_planned: Optional[bool] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get task actuals with filters and pagination.
    
    Requirements: 10.11
    """
    service = TaskActualService(db)
    
    task_actuals, total = service.get_task_actuals(
        schedule_id=schedule_id,
        crop_id=crop_id,
        plot_id=plot_id,
        is_planned=is_planned,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )
    
    return {
        "items": task_actuals,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


# Schedule Change Log Endpoints

change_log_router = APIRouter(prefix="/schedules", tags=["Schedule Change Log"])


@change_log_router.get("/{schedule_id}/change-log", response_model=dict)
def get_schedule_change_log(
    schedule_id: UUID,
    trigger_type: Optional[str] = Query(None),
    change_type: Optional[str] = Query(None),
    is_applied: Optional[bool] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get change history for a schedule with filters.
    
    Requirements: 11.7
    """
    service = ScheduleChangeLogService(db)
    
    # Convert trigger_type string to enum if provided
    from app.models.enums import ScheduleChangeTrigger
    trigger_enum = None
    if trigger_type:
        try:
            trigger_enum = ScheduleChangeTrigger[trigger_type.upper()]
        except KeyError:
            pass
    
    change_logs, total = service.get_change_history(
        schedule_id=schedule_id,
        trigger_type=trigger_enum,
        change_type=change_type,
        is_applied=is_applied,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )
    
    return {
        "items": change_logs,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@change_log_router.post("/change-log/apply", response_model=List[ScheduleChangeLogResponse])
def apply_proposed_changes(
    data: ApplyProposedChangesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Apply proposed schedule changes.
    
    Requirements: 11.10
    """
    service = ScheduleChangeLogService(db)
    
    applied_changes = service.apply_proposed_changes(
        change_log_ids=data.change_log_ids,
        user_id=current_user.id,
        user_org_id=current_user.current_organization_id
    )
    
    return applied_changes
