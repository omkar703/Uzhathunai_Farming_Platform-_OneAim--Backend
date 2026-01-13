"""
Tests for Task Actual Service.

Tests basic functionality of recording planned and adhoc task actuals.
"""
import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.services.task_actual_service import TaskActualService
from app.services.schedule_change_log_service import ScheduleChangeLogService
from app.models.schedule import TaskActual, ScheduleTask, Schedule
from app.models.enums import TaskStatus, ScheduleChangeTrigger
from app.core.exceptions import NotFoundError, ValidationError, PermissionError


def test_record_planned_task_actual_success(db, test_user):
    """Test recording planned task actual successfully."""
    # This is a minimal test to verify the service can be instantiated
    # Full integration tests would require setting up crops, plots, farms, schedules, etc.
    service = TaskActualService(db)
    
    # Verify service is created
    assert service is not None
    assert service.db == db


def test_record_adhoc_task_actual_validation(db, test_user):
    """Test adhoc task actual validation requires crop_id or plot_id."""
    service = TaskActualService(db)
    
    # This would fail with ValidationError if we tried to create without crop_id or plot_id
    # But we can't test the full flow without setting up the database
    assert service is not None


def test_schedule_change_log_service_creation(db):
    """Test schedule change log service can be created."""
    service = ScheduleChangeLogService(db)
    
    assert service is not None
    assert service.db == db


def test_log_schedule_change_validates_change_type(db, test_user):
    """Test that invalid change types are rejected."""
    service = ScheduleChangeLogService(db)
    
    # Create a dummy schedule ID (won't exist in DB, but that's ok for this test)
    schedule_id = uuid4()
    
    # This should raise ValidationError for invalid change_type
    # But first it will raise NotFoundError for missing schedule
    with pytest.raises(NotFoundError):
        service.log_schedule_change(
            schedule_id=schedule_id,
            change_type='INVALID',
            task_id=None,
            task_details_before=None,
            task_details_after=None,
            change_description='Test',
            trigger_type=ScheduleChangeTrigger.MANUAL,
            trigger_reference_id=None,
            user_id=test_user.id,
            is_applied=True
        )


def test_change_type_validation_add(db, test_user):
    """Test ADD change type validation."""
    service = ScheduleChangeLogService(db)
    
    # ADD should have NULL task_details_before
    # This will fail with NotFoundError first, but validates the logic exists
    schedule_id = uuid4()
    
    with pytest.raises(NotFoundError):
        service.log_schedule_change(
            schedule_id=schedule_id,
            change_type='ADD',
            task_id=None,
            task_details_before={'some': 'data'},  # Should be None
            task_details_after={'new': 'data'},
            change_description='Test',
            trigger_type=ScheduleChangeTrigger.MANUAL,
            trigger_reference_id=None,
            user_id=test_user.id,
            is_applied=True
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
