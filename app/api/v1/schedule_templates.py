"""
Schedule Template API endpoints for Uzhathunai v2.0.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.services.schedule_template_service import ScheduleTemplateService
from app.services.schedule_template_task_service import ScheduleTemplateTaskService
from app.schemas.schedule_template import (
    ScheduleTemplateCreate,
    ScheduleTemplateUpdate,
    ScheduleTemplateCopy,
    ScheduleTemplateResponse,
    ScheduleTemplateListResponse,
    ScheduleTemplateTaskCreate,
    ScheduleTemplateTaskUpdate,
    ScheduleTemplateTaskResponse
)

router = APIRouter(prefix="/schedule-templates", tags=["Schedule Templates"])


@router.get("", response_model=ScheduleTemplateListResponse)
def get_schedule_templates(
    crop_type_id: Optional[UUID] = Query(None, description="Filter by crop type"),
    crop_variety_id: Optional[UUID] = Query(None, description="Filter by crop variety"),
    is_system_defined: Optional[bool] = Query(None, description="Filter by system/org templates"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get schedule templates with ownership filtering.
    
    Requirements 4.13:
    - Returns system-defined templates (read-only for all)
    - Returns org-specific templates owned by user's organizations
    - Supports filtering by crop type, variety, and system/org flag
    """
    service = ScheduleTemplateService(db)
    templates, total = service.get_templates(
        user_id=current_user.id,
        crop_type_id=crop_type_id,
        crop_variety_id=crop_variety_id,
        is_system_defined=is_system_defined,
        page=page,
        limit=limit
    )
    
    return {
        "items": templates,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/{template_id}", response_model=ScheduleTemplateResponse)
def get_schedule_template(
    template_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get schedule template by ID.
    
    Returns template with all tasks and translations.
    """
    service = ScheduleTemplateService(db)
    template = service.get_template(template_id)
    return template


@router.post("", response_model=ScheduleTemplateResponse, status_code=201)
def create_schedule_template(
    data: ScheduleTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create schedule template with access control.
    
    Requirements 4.1, 4.2:
    - System users can create templates
    - FSP users with consultancy service can create templates
    - Farming organization users cannot create templates
    """
    service = ScheduleTemplateService(db)
    template = service.create_template(
        user_id=current_user.id,
        data=data
    )
    return template


@router.put("/{template_id}", response_model=ScheduleTemplateResponse)
def update_schedule_template(
    template_id: UUID,
    data: ScheduleTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update schedule template with ownership validation.
    
    Requirements 15.2, 15.5:
    - System-defined templates cannot be modified
    - Org-specific templates can only be modified by owner organization
    """
    service = ScheduleTemplateService(db)
    template = service.update_template(
        template_id=template_id,
        user_id=current_user.id,
        data=data
    )
    return template


@router.post("/{template_id}/copy", response_model=ScheduleTemplateResponse, status_code=201)
def copy_schedule_template(
    template_id: UUID,
    data: ScheduleTemplateCopy,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Copy schedule template with ownership rules.
    
    Requirements 5.1, 5.2, 5.3, 5.4:
    - System users can copy from any template
    - FSP users can only copy from their org templates
    - Copies all template tasks and translations
    """
    service = ScheduleTemplateService(db)
    template = service.copy_template(
        source_template_id=template_id,
        user_id=current_user.id,
        new_code=data.new_code,
        is_system_defined=data.is_system_defined
    )
    return template


@router.get("/{template_id}/tasks", response_model=list[ScheduleTemplateTaskResponse])
def get_template_tasks(
    template_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all tasks for a template.
    
    Returns tasks ordered by sort_order and day_offset.
    """
    service = ScheduleTemplateTaskService(db)
    tasks = service.get_template_tasks(template_id)
    return tasks


@router.post("/{template_id}/tasks", response_model=ScheduleTemplateTaskResponse, status_code=201)
def create_template_task(
    template_id: UUID,
    data: ScheduleTemplateTaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add task to schedule template.
    
    Requirements 4.7, 4.8:
    - Validates day_offset is non-negative
    - Validates task_details_template structure
    - Supports calculation_basis for all components
    """
    service = ScheduleTemplateTaskService(db)
    task = service.create_template_task(
        template_id=template_id,
        user_id=current_user.id,
        data=data
    )
    return task


@router.put("/tasks/{task_id}", response_model=ScheduleTemplateTaskResponse)
def update_template_task(
    task_id: UUID,
    data: ScheduleTemplateTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update template task.
    
    Validates ownership and task_details_template structure.
    """
    service = ScheduleTemplateTaskService(db)
    task = service.update_template_task(
        task_id=task_id,
        user_id=current_user.id,
        data=data
    )
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_template_task(
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete template task.
    
    Validates ownership before deletion.
    """
    service = ScheduleTemplateTaskService(db)
    service.delete_template_task(
        task_id=task_id,
        user_id=current_user.id
    )
    return None
