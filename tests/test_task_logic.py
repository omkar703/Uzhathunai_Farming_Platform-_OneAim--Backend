
import pytest
from uuid import UUID, uuid4
from datetime import date
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.schedule import Schedule, ScheduleTask
from app.models.enums import TaskStatus
from app.services.schedule_task_service import ScheduleTaskService
from app.core.exceptions import ValidationError

class TestTaskLogic:
    """
    Verify Task Status Transition Logic.
    Requirements: 
    - Ensure COMPLETED is a terminal state (cannot re-open).
    - Ensure invalid transitions raise ValidationError.
    """

    def test_invalid_transition_from_completed(self):
        """
        Test that a task cannot be moved from COMPLETED to IN_PROGRESS.
        """
        # Mock DB Session
        mock_db = MagicMock(spec=Session)
        service = ScheduleTaskService(mock_db)

        # Mock Data
        task_id = uuid4()
        user = Mock(spec=User)
        # Explicitly mock the method
        user.is_system_user = Mock(return_value=True)

        # Mock existing task in DB
        schedule_task = Mock(spec=ScheduleTask)
        schedule_task.id = task_id
        schedule_task.status = TaskStatus.COMPLETED
        schedule_task.schedule_id = uuid4()
        
        # Mock Schedule (needed for access check)
        schedule = Mock(spec=Schedule)
        schedule.id = schedule_task.schedule_id

        # Setup Queries
        # 1. query(ScheduleTask) -> first()
        # 2. query(Schedule) -> first()
        mock_db.query.return_value.filter.return_value.first.side_effect = [schedule_task, schedule]

        # Action: Try to update status
        with pytest.raises(ValidationError) as excinfo:
            service.update_task_status(
                task_id=task_id,
                new_status=TaskStatus.IN_PROGRESS,
                completed_date=None,
                user=user
            )
        
        assert "Invalid status transition" in str(excinfo.value)

    def test_valid_transition_start_task(self):
        """
        Test valid transition NOT_STARTED -> IN_PROGRESS.
        """
        mock_db = MagicMock(spec=Session)
        service = ScheduleTaskService(mock_db)

        task_id = uuid4()
        user = Mock(spec=User)
        user.id = uuid4()
        user.is_system_user = Mock(return_value=True)

        schedule_task = Mock(spec=ScheduleTask)
        schedule_task.id = task_id
        schedule_task.status = TaskStatus.NOT_STARTED
        schedule_task.schedule_id = uuid4()
        
        schedule = Mock(spec=Schedule)
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [schedule_task, schedule]

        # Action
        updated_task = service.update_task_status(
            task_id=task_id,
            new_status=TaskStatus.IN_PROGRESS,
            completed_date=None,
            user=user
        )

        # Verify
        assert schedule_task.status == TaskStatus.IN_PROGRESS
        mock_db.commit.assert_called_once()
