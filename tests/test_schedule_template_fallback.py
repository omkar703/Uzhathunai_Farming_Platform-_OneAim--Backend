import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.orm import Session

from app.services.schedule_service import ScheduleService
from app.models.user import User
from app.models.organization import Organization
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.schedule import Schedule, ScheduleTask
from app.models.schedule_template import ScheduleTemplate, ScheduleTemplateTask
from app.models.input_item import InputItem, InputItemCategory
from app.models.reference_data import ReferenceData, ReferenceDataType, Task as TaskModel
from app.models.enums import TaskStatus, OrganizationType, TaskCategory, MeasurementUnitCategory
from app.models.measurement_unit import MeasurementUnit

def test_empty_task_details_fallback_to_template(db: Session, test_user: User):
    """
    Test that when task_details is empty ({}), the service falls back to template.
    This simulates the production bug where schedules created from templates
    have empty task_details.
    """
    # Setup organization
    org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        created_by=test_user.id
    )
    db.add(org)
    db.flush()
    
    test_user.current_organization_id = org.id
    db.add(test_user)
    
    # Setup farm/plot/crop
    farm = Farm(
        organization_id=org.id,
        name="Test Farm",
        is_active=True,
        created_by=test_user.id
    )
    db.add(farm)
    db.flush()
    
    plot = Plot(
        farm_id=farm.id,
        name="Test Plot",
        area=10.0,
        is_active=True,
        created_by=test_user.id
    )
    db.add(plot)
    db.flush()
    
    crop = Crop(
        plot_id=plot.id,
        name="Test Crop",
        created_by=test_user.id
    )
    db.add(crop)
    db.flush()
    
    # Create input item
    category = InputItemCategory(
        code="FERTILIZER",
        is_system_defined=True,
        created_by=test_user.id
    )
    db.add(category)
    db.flush()
    
    input_item = InputItem(
        category_id=category.id,
        code="UREA",
        is_system_defined=True,
        created_by=test_user.id
    )
    db.add(input_item)
    db.flush()
    
    # Create measurement unit
    unit = MeasurementUnit(
        category=MeasurementUnitCategory.VOLUME,
        code="L",
        symbol="Liter",
        is_base_unit=True,
        sort_order=1
    )
    db.add(unit)
    db.flush()
    
    # Create task definition
    task_def = TaskModel(
        code="FERT_APP",
        category=TaskCategory.FARMING,
        sort_order=1
    )
    db.add(task_def)
    db.flush()
    
    # Create template with task_details_template
    template = ScheduleTemplate(
        code="TEST_TEMPLATE",
        name="Test Template",
        is_active=True,
        created_by=test_user.id
    )
    db.add(template)
    db.flush()
    
    # Create template task with proper task_details_template
    template_task = ScheduleTemplateTask(
        schedule_template_id=template.id,
        task_id=task_def.id,
        day_offset=1,
        task_details_template={
            "input_items": [{
                "input_item_id": str(input_item.id),
                "quantity": 50.0,
                "dosage": {
                    "amount": 5.0,
                    "unit_id": str(unit.id)
                }
            }]
        },
        created_by=test_user.id
    )
    db.add(template_task)
    db.flush()
    
    # Create schedule from template
    schedule = Schedule(
        crop_id=crop.id,
        template_id=template.id,
        name="Test Schedule",
        template_parameters={
            "area": 10.0,
            "area_unit_id": str(unit.id),
            "calculation_basis": "per_acre",
            "start_date": "2026-02-11"
        },
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(schedule)
    db.flush()
    
    # CRITICAL: Create task with EMPTY task_details (simulating the bug)
    schedule_task = ScheduleTask(
        schedule_id=schedule.id,
        task_id=task_def.id,
        due_date=date.today(),
        status=TaskStatus.NOT_STARTED,
        task_details={},  # EMPTY - this is the bug!
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(schedule_task)
    db.commit()
    db.refresh(schedule)
    db.refresh(schedule_task)
    
    # Act - call the service
    service = ScheduleService(db)
    response = service.get_schedule_with_details(test_user, schedule.id)
    
    # Assert - verify fallback worked
    assert len(response.tasks) == 1
    task_resp = response.tasks[0]
    
    # These should NOT be null even though task_details was empty
    assert task_resp.input_item_name is not None
    assert task_resp.input_item_name.upper() == "UREA"
    
    assert task_resp.total_quantity_required is not None
    assert task_resp.total_quantity_required == 50.0
    
    assert task_resp.dosage is not None
    assert task_resp.dosage['amount'] == 5.0
    
    print(f"✓ Fallback worked! input_item_name: {task_resp.input_item_name}")
    print(f"✓ total_quantity_required: {task_resp.total_quantity_required}")
    print(f"✓ dosage: {task_resp.dosage}")
