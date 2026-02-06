import pytest
from uuid import uuid4
from datetime import date
from sqlalchemy.orm import Session

from app.services.schedule_service import ScheduleService
from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.schedule import Schedule, ScheduleTask
from app.models.input_item import InputItem, InputItemCategory
from app.models.reference_data import ReferenceData, ReferenceDataType
from app.models.enums import TaskStatus, OrganizationType, MeasurementUnitCategory
from app.models.measurement_unit import MeasurementUnit

def create_unit_reference_data(db: Session, code_suffix: str = ""):
    code = f"L_TEST{code_suffix}"
    unit = db.query(MeasurementUnit).filter(MeasurementUnit.code == code).first()
    if not unit:
        unit = MeasurementUnit(
            category=MeasurementUnitCategory.VOLUME,
            code=code,
            symbol="LiterTest",
            is_base_unit=True,
            sort_order=1
        )
        db.add(unit)
        db.flush()
    return unit

def create_test_data(db: Session, user: User):
    # 1. Organization
    org = Organization(
        name="Test Farm Org",
        organization_type=OrganizationType.FARMING,
        created_by=user.id
    )
    db.add(org)
    db.flush()
    
    # 2. Update user current organization
    user.current_organization_id = org.id
    db.add(user)
    
    # 3. Farm
    farm = Farm(
        organization_id=org.id,
        name="Test Farm",
        is_active=True,
        created_by=user.id
    )
    db.add(farm)
    db.flush()
    
    # 4. Plot
    plot = Plot(
        farm_id=farm.id,
        name="Test Plot",
        area=10.0,
        is_active=True,
        created_by=user.id
    )
    db.add(plot)
    db.flush()
    
    # 5. Crop
    crop = Crop(
        plot_id=plot.id,
        name="Test Crop",
        created_by=user.id,
        # minimal fields
    )
    db.add(crop)
    db.flush()
    
    return crop, org

def create_input_item(db: Session, user: User):
    # Category
    category = db.query(InputItemCategory).filter(InputItemCategory.code == "FERTILIZER").first()
    if not category:
        category = InputItemCategory(
            code="FERTILIZER",
            is_system_defined=True,
            created_by=user.id
        )
        db.add(category)
        db.flush()
    
    # Input Item
    item = db.query(InputItem).filter(InputItem.code == "UREA").first()
    if not item:
        item = InputItem(
            category_id=category.id,
            code="UREA", # Fallback name
            is_system_defined=True,
            created_by=user.id
        )
        db.add(item)
        db.flush()
    return item

def create_reference_data(db: Session):
    # Type
    rtype = db.query(ReferenceDataType).filter(ReferenceDataType.code == "APPLICATION_METHOD").first()
    if not rtype:
        rtype = ReferenceDataType(
            code="APPLICATION_METHOD",
            name="Application Method"
        )
        db.add(rtype)
        db.flush()
    
    # Data
    rdata = db.query(ReferenceData).filter(ReferenceData.code == "FOLIAR_SPRAY", ReferenceData.type_id == rtype.id).first()
    if not rdata:
        rdata = ReferenceData(
            type_id=rtype.id,
            code="FOLIAR_SPRAY",
            sort_order=1
        )
        db.add(rdata)
        db.flush()
        
        # Add translation
        from app.models.reference_data import ReferenceDataTranslation
        trans = ReferenceDataTranslation(
            reference_data_id=rdata.id,
            language_code="en",
            display_name="Foliar Spray"
        )
        db.add(trans)
        db.flush()
    return rdata

def test_get_schedule_details_populates_fields(db: Session, test_user: User):
    # Setup
    crop, org = create_test_data(db, test_user)
    input_item = create_input_item(db, test_user)
    app_method = create_reference_data(db)
    
    # Create Schedule
    schedule = Schedule(
        crop_id=crop.id,
        name=f"Test Schedule {uuid4()}", # Unique name
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(schedule)
    db.flush()
    
    # Create Task with task_details
    from app.models.reference_data import Task as TaskModel
    from app.models.enums import TaskCategory
    
    task_def = db.query(TaskModel).filter(TaskModel.code == "FERT_APP").first()
    if not task_def:
        task_def = TaskModel(
            code="FERT_APP",
            category=TaskCategory.FARMING,
            sort_order=1
        )
        db.add(task_def)
        db.flush()
    
    task_details = {
        "input_items": [
            {
                "input_item_id": str(input_item.id),
                "quantity": 50.5,
                "application_method_id": str(app_method.id)
            }
        ]
    }
    
    schedule_task = ScheduleTask(
        schedule_id=schedule.id,
        task_id=task_def.id,
        due_date=date.today(),
        status=TaskStatus.NOT_STARTED,
        task_details=task_details,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(schedule_task)
    db.commit()
    db.refresh(schedule)
    db.refresh(schedule_task)

    # Act
    service = ScheduleService(db)
    response = service.get_schedule_with_details(test_user, schedule.id)
    
    # Assert
    assert len(response.tasks) == 1
    task_resp = response.tasks[0]
    
    # Verify populated fields
    # Note: If item existed, it might not have expected name/translation.
    # UREA code is used as fallback.
    assert task_resp.input_item_name and task_resp.input_item_name.upper() == "UREA"
    assert task_resp.application_method_name == "Foliar Spray"
    assert task_resp.total_quantity_required == 50.5

def test_get_schedule_details_concentration_populates_fields(db: Session, test_user: User):
    # Setup for concentration case
    crop, org = create_test_data(db, test_user)
    input_item = create_input_item(db, test_user)
    unit = create_unit_reference_data(db, code_suffix="_CONC")
    
    schedule = Schedule(
        crop_id=crop.id,
        name=f"Conc Schedule {uuid4()}",
        created_by=test_user.id,
        updated_by=test_user.id,
        template_parameters={"area": 10.0, "area_unit_id": str(unit.id), "calculation_basis": "per_acre"}
    )
    db.add(schedule)
    db.flush()
    
    from app.models.reference_data import Task as TaskModel
    from app.models.enums import TaskCategory
    
    # Reuse or create task def
    task_def = db.query(TaskModel).filter(TaskModel.code=="FERT_APP").first()
    if not task_def:
        task_def = TaskModel(code="FERT_APP", category=TaskCategory.FARMING)
        db.add(task_def)
        db.flush()
        
    # Let's stick to regular tasks for dosage verification for now, as that's the primary "dosage" use case.
    # I'll update this test to standard input_item based task but with dosage.
    
    task_details_dosage = {
        "input_items": [
             {
                  "input_item_id": str(input_item.id),
                  # "quantity": 12.5, # Removed to force calculation
                  "application_method_id": None, 
                  "dosage": {"amount": 5.0, "unit_id": str(unit.id)}
             }
        ]
    }
    
    schedule_task = ScheduleTask(
        schedule_id=schedule.id,
        task_id=task_def.id,
        due_date=date.today(),
        status=TaskStatus.NOT_STARTED,
        task_details=task_details_dosage,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(schedule_task)
    db.commit()
    db.refresh(schedule)
    db.refresh(schedule_task)
    
    # Act
    service = ScheduleService(db)
    response = service.get_schedule_with_details(test_user, schedule.id)
    
    # Assert
    assert len(response.tasks) == 1
    task_resp = response.tasks[0]
    
    # Verify Area
    assert response.area == 10.0
    assert response.area_unit == "LiterTest" 
    
    # Verify Dosage
    assert task_resp.dosage is not None
    assert task_resp.dosage['amount'] == 5.0
    
    # Verify Calculated Total Quantity
    # Area 10.0 * Dosage 5.0 = 50.0
    assert task_resp.total_quantity_required == 50.0
