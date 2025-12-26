"""
Tasks API endpoints for Uzhathunai v2.0.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.reference_data import TaskResponse
from app.services.task_service import TaskService

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    language: str = Query("en", description="Language code (en, ta, ml)"),
    is_active: bool = Query(True, description="Filter by active status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all farming tasks.
    
    - **language**: Language code for translations (default: en)
    - **is_active**: Filter by active status (default: true)
    
    Returns list of tasks with translations.
    Tasks include attributes like requires_input_items, requires_concentration, etc.
    """
    service = TaskService(db)
    return service.get_tasks(language, is_active)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    language: str = Query("en", description="Language code (en, ta, ml)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.
    
    - **task_id**: UUID of the task
    - **language**: Language code for translations (default: en)
    
    Returns task details with translation.
    """
    service = TaskService(db)
    return service.get_task_by_id(task_id, language)
