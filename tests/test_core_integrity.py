
import pytest
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus, CropLifecycle
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.measurement_unit import MeasurementUnit
from app.models.enums import MeasurementUnitCategory
from decimal import Decimal

@pytest.fixture
def test_integrity_org(db: Session, test_user: User) -> Organization:
    """Create a clean organization for integrity tests."""
    org = Organization(
        name="Integrity Test Farm Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    member = OrgMember(
        user_id=test_user.id,
        organization_id=org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    return org

@pytest.fixture
def area_unit(db: Session) -> MeasurementUnit:
    """Ensure area unit exists."""
    unit = db.query(MeasurementUnit).filter_by(code="ACRE").first()
    if not unit:
        unit = MeasurementUnit(
            category=MeasurementUnitCategory.AREA,
            code="ACRE",
            symbol="ac",
            conversion_factor=Decimal("1.0"),
            is_base_unit=True
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
    return unit

class TestCoreDataIntegrity:
    """
    Verify the 'Orphan Protection' logic requested by the user.
    Ensures correct Cascade Deletion vs Restriction.
    """

    def test_farm_cascade_deletion(
        self,
        db: Session,
        test_integrity_org: Organization,
        area_unit: MeasurementUnit
    ):
        """
        Verify that deleting a Farm HARD deletes its Plots and Crops.
        This confirms the `ondelete='CASCADE'` configuration in models.
        """
        # 1. Create Farm
        farm = Farm(
            organization_id=test_integrity_org.id,
            name="Cascade Parent Farm",
            area_unit_id=area_unit.id,
            location="POINT(77.01 11.01)"
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)

        # 2. Create Plot on Farm
        plot = Plot(
            farm_id=farm.id,
            name="Child Plot",
            area=10,
            area_unit_id=area_unit.id
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)

        # 3. Create Crop on Plot
        crop = Crop(
            plot_id=plot.id,
            name="Child Crop",
            lifecycle=CropLifecycle.PLANNED,
            area_unit_id=area_unit.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

        # Confirm existence
        assert db.query(Farm).filter_by(id=farm.id).first() is not None
        assert db.query(Plot).filter_by(id=plot.id).first() is not None
        assert db.query(Crop).filter_by(id=crop.id).first() is not None

        # 4. ACTION: Delete Farm via API (to trigger soft or hard delete depending on implementation)
        # Note: The user requested verifying "Relationship Check". 
        # Typically API does SOFT delete (is_active=False).
        # But we need to check if HARD DB delete cascades correctly too, usually via Admin or cleanup.
        # Let's test the DB relationship specifically first using direct DB deletion, 
        # as API deletion usually just flags 'is_active=False'.
        
        db.delete(farm)
        db.commit()

        # 5. Assertion: Children should be gone
        # We use a new session or expire all to ensure we aren't reading from cache
        db.expire_all()
        
        found_plot = db.query(Plot).filter_by(id=plot.id).first()
        found_crop = db.query(Crop).filter_by(id=crop.id).first()

        assert found_plot is None, "Plot should have been cascaded deleted"
        assert found_crop is None, "Crop should have been cascaded deleted"

