"""
Unit tests for CropService lifecycle management.

Tests:
- Lifecycle transitions (valid and invalid)
- Date field updates
- State machine validation

Requirements: 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9
"""
import pytest
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session

from app.services.crop_service import CropService, LIFECYCLE_TRANSITIONS
from app.models.organization import Organization
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.user import User
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    CropLifecycle
)
from app.core.exceptions import NotFoundError, ValidationError
from app.schemas.crop import CropCreate


@pytest.fixture
def test_organization(db: Session, test_user: User) -> Organization:
    """Create a test organization."""
    org = Organization(
        name="Test Farm Organization",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def test_farm(db: Session, test_organization: Organization, test_user: User) -> Farm:
    """Create a test farm."""
    farm = Farm(
        organization_id=test_organization.id,
        name="Test Farm",
        location="POINT(80.2707 13.0827)",  # Chennai coordinates
        is_active=True,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@pytest.fixture
def test_plot(db: Session, test_farm: Farm, test_user: User) -> Plot:
    """Create a test plot."""
    plot = Plot(
        farm_id=test_farm.id,
        name="Test Plot",
        is_active=True,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(plot)
    db.commit()
    db.refresh(plot)
    return plot


@pytest.fixture
def test_crop(db: Session, test_plot: Plot, test_user: User) -> Crop:
    """Create a test crop in PLANNED state."""
    crop = Crop(
        plot_id=test_plot.id,
        name="Test Crop",
        lifecycle=CropLifecycle.PLANNED,
        planned_date=date.today(),
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


class TestCropServiceLifecycle:
    """Test suite for CropService lifecycle management."""
    
    # Valid Lifecycle Transitions Tests
    
    def test_transition_planned_to_planted(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PLANNED to PLANTED."""
        service = CropService(db)
        
        # Verify initial state
        assert test_crop.lifecycle == CropLifecycle.PLANNED
        assert test_crop.planted_date is None
        
        # Transition to PLANTED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.PLANTED
        assert result.planted_date == date.today()
    
    def test_transition_planned_to_terminated(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PLANNED to TERMINATED."""
        service = CropService(db)
        
        # Transition to TERMINATED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.TERMINATED
        assert result.terminated_date == date.today()
    
    def test_transition_planted_to_transplanted(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PLANTED to TRANSPLANTED."""
        service = CropService(db)
        
        # First transition to PLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to TRANSPLANTED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TRANSPLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.TRANSPLANTED
        assert result.transplanted_date == date.today()
    
    def test_transition_planted_to_production(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PLANTED to PRODUCTION."""
        service = CropService(db)
        
        # First transition to PLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to PRODUCTION
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.PRODUCTION
        assert result.production_start_date == date.today()
    
    def test_transition_planted_to_terminated(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PLANTED to TERMINATED."""
        service = CropService(db)
        
        # First transition to PLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to TERMINATED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.TERMINATED
        assert result.terminated_date == date.today()
    
    def test_transition_transplanted_to_production(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from TRANSPLANTED to PRODUCTION."""
        service = CropService(db)
        
        # Transition to PLANTED then TRANSPLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TRANSPLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to PRODUCTION
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.PRODUCTION
        assert result.production_start_date == date.today()
    
    def test_transition_transplanted_to_terminated(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from TRANSPLANTED to TERMINATED."""
        service = CropService(db)
        
        # Transition to PLANTED then TRANSPLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TRANSPLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to TERMINATED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.TERMINATED
        assert result.terminated_date == date.today()
    
    def test_transition_production_to_completed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PRODUCTION to COMPLETED."""
        service = CropService(db)
        
        # Transition to PLANTED then PRODUCTION
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to COMPLETED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.COMPLETED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.COMPLETED
        assert result.completed_date == date.today()
    
    def test_transition_production_to_terminated(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from PRODUCTION to TERMINATED."""
        service = CropService(db)
        
        # Transition to PLANTED then PRODUCTION
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to TERMINATED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.TERMINATED
        assert result.terminated_date == date.today()
    
    def test_transition_completed_to_closed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from COMPLETED to CLOSED."""
        service = CropService(db)
        
        # Transition through lifecycle to COMPLETED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.COMPLETED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to CLOSED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.CLOSED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.CLOSED
        assert result.closed_date == date.today()
    
    def test_transition_terminated_to_closed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test valid transition from TERMINATED to CLOSED."""
        service = CropService(db)
        
        # Transition to TERMINATED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Then transition to CLOSED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.CLOSED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify transition
        assert result.lifecycle == CropLifecycle.CLOSED
        assert result.closed_date == date.today()
    
    # Invalid Lifecycle Transitions Tests
    
    def test_invalid_transition_planned_to_production(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test invalid transition from PLANNED to PRODUCTION."""
        service = CropService(db)
        
        # Try invalid transition
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.PRODUCTION,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
        assert "PLANNED" in exc_info.value.message
        assert "PRODUCTION" in exc_info.value.message
    
    def test_invalid_transition_planned_to_completed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test invalid transition from PLANNED to COMPLETED."""
        service = CropService(db)
        
        # Try invalid transition
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.COMPLETED,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
    
    def test_invalid_transition_planned_to_closed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test invalid transition from PLANNED to CLOSED."""
        service = CropService(db)
        
        # Try invalid transition
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.CLOSED,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
    
    def test_invalid_transition_planted_to_completed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test invalid transition from PLANTED to COMPLETED."""
        service = CropService(db)
        
        # First transition to PLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Try invalid transition
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.COMPLETED,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
    
    def test_invalid_transition_transplanted_to_completed(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test invalid transition from TRANSPLANTED to COMPLETED."""
        service = CropService(db)
        
        # Transition to PLANTED then TRANSPLANTED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TRANSPLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Try invalid transition
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.COMPLETED,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
    
    def test_invalid_transition_completed_to_production(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test invalid transition from COMPLETED to PRODUCTION."""
        service = CropService(db)
        
        # Transition through lifecycle to COMPLETED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.COMPLETED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Try invalid transition back to PRODUCTION
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.PRODUCTION,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
    
    def test_invalid_transition_closed_to_any(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test that CLOSED is a terminal state (no transitions allowed)."""
        service = CropService(db)
        
        # Transition to CLOSED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.CLOSED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Try to transition from CLOSED (should fail)
        with pytest.raises(ValidationError) as exc_info:
            service.update_lifecycle(
                crop_id=test_crop.id,
                new_lifecycle=CropLifecycle.PLANNED,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "INVALID_LIFECYCLE_TRANSITION"
        assert "none" in exc_info.value.message.lower()  # No valid transitions
    
    # Date Field Update Tests
    
    def test_date_field_updates_for_all_stages(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test that date fields are updated correctly for each lifecycle stage."""
        service = CropService(db)
        
        # Initial state - only planned_date should be set
        assert test_crop.planned_date is not None
        assert test_crop.planted_date is None
        assert test_crop.transplanted_date is None
        assert test_crop.production_start_date is None
        assert test_crop.completed_date is None
        assert test_crop.terminated_date is None
        assert test_crop.closed_date is None
        
        # Transition to PLANTED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        assert result.planted_date == date.today()
        
        # Transition to TRANSPLANTED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TRANSPLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        assert result.transplanted_date == date.today()
        
        # Transition to PRODUCTION
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PRODUCTION,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        assert result.production_start_date == date.today()
        
        # Transition to COMPLETED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.COMPLETED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        assert result.completed_date == date.today()
        
        # Transition to CLOSED
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.CLOSED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        assert result.closed_date == date.today()
        
        # Verify all dates are set
        assert result.planned_date is not None
        assert result.planted_date is not None
        assert result.transplanted_date is not None
        assert result.production_start_date is not None
        assert result.completed_date is not None
        assert result.closed_date is not None
    
    def test_terminated_date_field_update(
        self,
        db: Session,
        test_crop: Crop,
        test_organization: Organization,
        test_user: User
    ):
        """Test that terminated_date is set when transitioning to TERMINATED."""
        service = CropService(db)
        
        # Transition to PLANTED then TERMINATED
        service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.PLANTED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        result = service.update_lifecycle(
            crop_id=test_crop.id,
            new_lifecycle=CropLifecycle.TERMINATED,
            org_id=test_organization.id,
            user_id=test_user.id
        )
        
        # Verify terminated_date is set
        assert result.terminated_date == date.today()
        
        # Verify other completion dates are not set
        assert result.completed_date is None
    
    def test_validate_lifecycle_transition_method(self, db: Session):
        """Test the validate_lifecycle_transition method directly."""
        service = CropService(db)
        
        # Test valid transitions
        assert service.validate_lifecycle_transition(
            CropLifecycle.PLANNED,
            CropLifecycle.PLANTED
        ) is True
        
        assert service.validate_lifecycle_transition(
            CropLifecycle.PLANTED,
            CropLifecycle.PRODUCTION
        ) is True
        
        # Test invalid transitions
        with pytest.raises(ValidationError):
            service.validate_lifecycle_transition(
                CropLifecycle.PLANNED,
                CropLifecycle.PRODUCTION
            )
        
        with pytest.raises(ValidationError):
            service.validate_lifecycle_transition(
                CropLifecycle.CLOSED,
                CropLifecycle.PLANNED
            )
    
    def test_lifecycle_state_machine_completeness(self):
        """Test that the lifecycle state machine covers all states."""
        # Verify all lifecycle states are in the state machine
        for lifecycle in CropLifecycle:
            assert lifecycle in LIFECYCLE_TRANSITIONS
        
        # Verify CLOSED has no transitions (terminal state)
        assert LIFECYCLE_TRANSITIONS[CropLifecycle.CLOSED] == []
    
    def test_crop_not_found_error(
        self,
        db: Session,
        test_organization: Organization,
        test_user: User
    ):
        """Test that updating lifecycle for non-existent crop raises error."""
        service = CropService(db)
        
        # Try to update lifecycle for non-existent crop
        fake_crop_id = UUID("00000000-0000-0000-0000-000000000000")
        
        with pytest.raises(NotFoundError) as exc_info:
            service.update_lifecycle(
                crop_id=fake_crop_id,
                new_lifecycle=CropLifecycle.PLANTED,
                org_id=test_organization.id,
                user_id=test_user.id
            )
        
        # Verify error
        assert exc_info.value.error_code == "CROP_NOT_FOUND"
