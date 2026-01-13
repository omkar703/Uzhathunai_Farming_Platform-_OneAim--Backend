"""
Task service for managing predefined farming tasks.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.exceptions import NotFoundError
from app.core.cache import cache_service
from app.models.reference_data import Task, TaskTranslation
from app.models.enums import TaskCategory
from app.schemas.reference_data import TaskResponse, TaskTranslationResponse

logger = get_logger(__name__)

# Cache TTL: 24 hours for tasks (system-defined, rarely change)
CACHE_TTL = 86400


class TaskService:
    """Service for task operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache = cache_service
    
    def get_tasks(
        self, 
        language: str = "en",
        is_active: bool = True
    ) -> List[TaskResponse]:
        """
        Get all tasks with translations.
        
        Args:
            language: Language code for translations (default: en)
            is_active: Filter by active status (default: True)
            
        Returns:
            List of tasks with translations
        """
        # Check cache first
        cache_key = self.cache._get_key(
            "tasks",
            language,
            "active" if is_active else "all"
        )
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(
                "Cache hit for tasks",
                extra={
                    "language": language,
                    "is_active": is_active,
                    "cache_key": cache_key
                }
            )
            return [TaskResponse(**item) for item in cached_data]
        
        # Cache miss - query database
        query = self.db.query(Task)
        
        if is_active:
            query = query.filter(Task.is_active == True)
        
        tasks = query.order_by(Task.sort_order, Task.code).all()
        
        result = []
        for task in tasks:
            # Build translation responses
            translation_responses = [
                TaskTranslationResponse(
                    language_code=t.language_code,
                    name=t.name,
                    description=t.description
                )
                for t in task.translations
            ]
            
            result.append(TaskResponse(
                id=str(task.id),
                code=task.code,
                category=task.category,
                requires_input_items=task.requires_input_items,
                requires_concentration=task.requires_concentration,
                requires_machinery=task.requires_machinery,
                requires_labor=task.requires_labor,
                sort_order=task.sort_order,
                is_active=task.is_active,
                translations=translation_responses
            ))
        
        # Cache the result
        cache_data = [item.dict() for item in result]
        self.cache.set(cache_key, cache_data, CACHE_TTL)
        
        logger.info(
            "Retrieved tasks from database and cached",
            extra={
                "language": language,
                "is_active": is_active,
                "count": len(result),
                "cache_key": cache_key,
                "ttl": CACHE_TTL
            }
        )
        
        return result
    
    def get_task_by_id(
        self, 
        task_id: UUID, 
        language: str = "en"
    ) -> TaskResponse:
        """
        Get a task by ID with translations.
        
        Args:
            task_id: Task ID
            language: Language code for translations (default: en)
            
        Returns:
            Task with translations
            
        Raises:
            NotFoundError: If task not found
        """
        # Check cache first
        cache_key = self.cache._get_key("task", str(task_id), language)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(
                "Cache hit for task by ID",
                extra={
                    "task_id": str(task_id),
                    "language": language,
                    "cache_key": cache_key
                }
            )
            return TaskResponse(**cached_data)
        
        # Cache miss - query database
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )
        
        if not task:
            raise NotFoundError(
                message=f"Task {task_id} not found",
                error_code="TASK_NOT_FOUND",
                details={"task_id": str(task_id)}
            )
        
        # Build translation responses
        translation_responses = [
            TaskTranslationResponse(
                language_code=t.language_code,
                name=t.name,
                description=t.description
            )
            for t in task.translations
        ]
        
        result = TaskResponse(
            id=str(task.id),
            code=task.code,
            category=task.category,
            requires_input_items=task.requires_input_items,
            requires_concentration=task.requires_concentration,
            requires_machinery=task.requires_machinery,
            requires_labor=task.requires_labor,
            sort_order=task.sort_order,
            is_active=task.is_active,
            translations=translation_responses
        )
        
        # Cache the result
        self.cache.set(cache_key, result.dict(), CACHE_TTL)
        
        logger.info(
            "Retrieved task by ID from database and cached",
            extra={
                "task_id": str(task_id),
                "code": task.code,
                "language": language,
                "cache_key": cache_key,
                "ttl": CACHE_TTL
            }
        )
        
        return result
    
    def get_tasks_by_category(
        self, 
        category: TaskCategory, 
        language: str = "en"
    ) -> List[TaskResponse]:
        """
        Get tasks filtered by category.
        
        Args:
            category: Task category (FARMING, FSP_CONSULTANCY)
            language: Language code for translations (default: en)
            
        Returns:
            List of tasks in the specified category
        """
        # Check cache first
        cache_key = self.cache._get_key("tasks", "category", category.value, language)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            logger.info(
                "Cache hit for tasks by category",
                extra={
                    "category": category.value,
                    "language": language,
                    "cache_key": cache_key
                }
            )
            return [TaskResponse(**item) for item in cached_data]
        
        # Cache miss - query database
        tasks = (
            self.db.query(Task)
            .filter(Task.category == category)
            .filter(Task.is_active == True)
            .order_by(Task.sort_order, Task.code)
            .all()
        )
        
        result = []
        for task in tasks:
            # Build translation responses
            translation_responses = [
                TaskTranslationResponse(
                    language_code=t.language_code,
                    name=t.name,
                    description=t.description
                )
                for t in task.translations
            ]
            
            result.append(TaskResponse(
                id=str(task.id),
                code=task.code,
                category=task.category,
                requires_input_items=task.requires_input_items,
                requires_concentration=task.requires_concentration,
                requires_machinery=task.requires_machinery,
                requires_labor=task.requires_labor,
                sort_order=task.sort_order,
                is_active=task.is_active,
                translations=translation_responses
            ))
        
        # Cache the result
        cache_data = [item.dict() for item in result]
        self.cache.set(cache_key, cache_data, CACHE_TTL)
        
        logger.info(
            "Retrieved tasks by category from database and cached",
            extra={
                "category": category.value,
                "language": language,
                "count": len(result),
                "cache_key": cache_key,
                "ttl": CACHE_TTL
            }
        )
        
        return result
