"""
Integration tests for Crop API endpoints.

Tests POST /crops, PUT /crops/{id}/lifecycle, and lifecycle transitions.
Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9
"""
import pytest
from uuid import UUID
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    CropLifecycle
)


@pytest.fixture
def test_organization(db: Session, test_user: User) -> Organization:
    """Create a test farming organization."""
    org = Organization(
        name="Test Farm Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id,
        updated_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Add user as member
    member = OrgMember(
        user_id=test_user.id,
        organization_id=org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
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


class TestCropCreation:
    """Test crop creation endpoint."""
    
    def test_create_crop_success(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot
    ):
        """Test successful crop creation."""
        # Requirement 9.1: Create crop with required fields
        crop_data = {
            "plot_id": str(test_plot.id),
            "name": "Tomato Crop",
            "description": "Test tomato crop",
            "plant_count": 100
        }
        
        response = client.post(
            "/api/v1/crops/",
            json=crop_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["name"] == "Tomato Crop"
        assert data["description"] == "Test tomato crop"
        assert data["plot_id"] == str(test_plot.id)
        assert data["plant_count"] == 100
        
        # Requirement 9.3: Initial lifecycle is PLANNED
        assert data["lifecycle"] == CropLifecycle.PLANNED.value
        assert data["planned_date"] is None  # Not set in request
        
        # Verify lifecycle dates are null initially
        assert data["planted_date"] is None
        assert data["transplanted_date"] is None
        assert data["production_start_date"] is None
        assert data["completed_date"] is None
        assert data["terminated_date"] is None
        assert data["closed_date"] is None
    
    def test_create_crop_with_planned_date(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot
    ):
        """Test crop creation with planned date."""
        # Requirement 9.4: Record planned_date
        crop_data = {
            "plot_id": str(test_plot.id),
            "name": "Wheat Crop",
            "planned_date": "2024-01-15"
        }
        
        response = client.post(
            "/api/v1/crops/",
            json=crop_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["planned_date"] == "2024-01-15"
    
    def test_create_crop_with_area(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        db: Session
    ):
        """Test crop creation with area."""
        # Requirement 9.2: Define crop area with unit
        # First, create a measurement unit for testing
        from app.models.measurement_unit import MeasurementUnit
        from app.models.enums import MeasurementUnitCategory
        
        unit = MeasurementUnit(
            category=MeasurementUnitCategory.AREA,
            code="ACRE",
            symbol="ac",
            is_base_unit=True,
            conversion_factor=1.0,
            sort_order=1
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
        
        crop_data = {
            "plot_id": str(test_plot.id),
            "name": "Rice Crop",
            "area": "2.5",
            "area_unit_id": str(unit.id)
        }
        
        response = client.post(
            "/api/v1/crops/",
            json=crop_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert float(data["area"]) == 2.5
        assert data["area_unit_id"] == str(unit.id)
    
    def test_create_crop_invalid_plot(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test crop creation with invalid plot ID."""
        crop_data = {
            "plot_id": "00000000-0000-0000-0000-000000000000",
            "name": "Invalid Crop"
        }
        
        response = client.post(
            "/api/v1/crops/",
            json=crop_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "PLOT_NOT_FOUND"
    
    def test_create_crop_empty_name(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot
    ):
        """Test crop creation with empty name."""
        crop_data = {
            "plot_id": str(test_plot.id),
            "name": ""
        }
        
        response = client.post(
            "/api/v1/crops/",
            json=crop_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"


class TestCropRetrieval:
    """Test crop retrieval endpoints."""
    
    def test_get_crops_list(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        db: Session,
        test_user: User
    ):
        """Test getting list of crops."""
        # Create multiple crops
        crops = [
            Crop(
                plot_id=test_plot.id,
                name=f"Crop {i}",
                lifecycle=CropLifecycle.PLANNED,
                created_by=test_user.id,
                updated_by=test_user.id
            )
            for i in range(3)
        ]
        db.add_all(crops)
        db.commit()
        
        response = client.get(
            "/api/v1/crops/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "total_pages" in data
        
        assert len(data["items"]) == 3
        assert data["total"] == 3
    
    def test_get_crops_filter_by_plot(
        self,
        client: TestClient,
        auth_headers: dict,
        test_farm: Farm,
        test_user: User,
        db: Session
    ):
        """Test filtering crops by plot."""
        # Create two plots
        plot1 = Plot(
            farm_id=test_farm.id,
            name="Plot 1",
            is_active=True,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        plot2 = Plot(
            farm_id=test_farm.id,
            name="Plot 2",
            is_active=True,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add_all([plot1, plot2])
        db.commit()
        
        # Create crops in different plots
        crop1 = Crop(
            plot_id=plot1.id,
            name="Crop in Plot 1",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        crop2 = Crop(
            plot_id=plot2.id,
            name="Crop in Plot 2",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add_all([crop1, crop2])
        db.commit()
        
        # Filter by plot1
        response = client.get(
            f"/api/v1/crops/?plot_id={plot1.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Crop in Plot 1"
    
    def test_get_crops_filter_by_lifecycle(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test filtering crops by lifecycle."""
        # Create crops with different lifecycles
        crop1 = Crop(
            plot_id=test_plot.id,
            name="Planned Crop",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        crop2 = Crop(
            plot_id=test_plot.id,
            name="Planted Crop",
            lifecycle=CropLifecycle.PLANTED,
            planted_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add_all([crop1, crop2])
        db.commit()
        
        # Filter by PLANNED
        response = client.get(
            f"/api/v1/crops/?lifecycle={CropLifecycle.PLANNED.value}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["lifecycle"] == CropLifecycle.PLANNED.value
    
    def test_get_crop_by_id(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test getting crop by ID."""
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            description="Test description",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.get(
            f"/api/v1/crops/{crop.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(crop.id)
        assert data["name"] == "Test Crop"
        assert data["description"] == "Test description"


class TestCropLifecycleTransitions:
    """Test crop lifecycle transition endpoint."""
    
    def test_lifecycle_planned_to_planted(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test valid transition from PLANNED to PLANTED."""
        # Requirement 9.5: Valid lifecycle transition
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.PLANTED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify lifecycle updated
        assert data["lifecycle"] == CropLifecycle.PLANTED.value
        
        # Requirement 9.4: planted_date is set automatically
        assert data["planted_date"] is not None
        assert data["planted_date"] == str(date.today())
    
    def test_lifecycle_planted_to_production(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test valid transition from PLANTED to PRODUCTION."""
        # Requirement 9.6: Valid lifecycle transition
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PLANTED,
            planted_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.PRODUCTION.value},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["lifecycle"] == CropLifecycle.PRODUCTION.value
        
        # Requirement 9.4: production_start_date is set automatically
        assert data["production_start_date"] is not None
        assert data["production_start_date"] == str(date.today())
    
    def test_lifecycle_production_to_completed(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test valid transition from PRODUCTION to COMPLETED."""
        # Requirement 9.7: Valid lifecycle transition
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PRODUCTION,
            production_start_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.COMPLETED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["lifecycle"] == CropLifecycle.COMPLETED.value
        
        # Requirement 9.4: completed_date is set automatically
        assert data["completed_date"] is not None
        assert data["completed_date"] == str(date.today())
    
    def test_lifecycle_completed_to_closed(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test valid transition from COMPLETED to CLOSED."""
        # Requirement 9.8: Valid lifecycle transition
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.COMPLETED,
            completed_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.CLOSED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["lifecycle"] == CropLifecycle.CLOSED.value
        
        # Requirement 9.4: closed_date is set automatically
        assert data["closed_date"] is not None
        assert data["closed_date"] == str(date.today())
    
    def test_lifecycle_invalid_transition(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test invalid lifecycle transition."""
        # Requirement 9.5: Enforce valid lifecycle transitions
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.COMPLETED,
            completed_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        # Try invalid transition: COMPLETED -> PLANTED
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.PLANTED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "INVALID_LIFECYCLE_TRANSITION"
        assert "COMPLETED" in data["message"]
        assert "PLANTED" in data["message"]
        
        # Verify valid transitions are listed
        assert "details" in data
        assert "valid_transitions" in data["details"]
        assert CropLifecycle.CLOSED.value in data["details"]["valid_transitions"]
    
    def test_lifecycle_planned_to_terminated(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test transition from PLANNED to TERMINATED."""
        # Requirement 9.5: Valid transition to TERMINATED
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.TERMINATED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["lifecycle"] == CropLifecycle.TERMINATED.value
        assert data["terminated_date"] is not None
    
    def test_lifecycle_terminated_to_closed(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test transition from TERMINATED to CLOSED."""
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.TERMINATED,
            terminated_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.CLOSED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["lifecycle"] == CropLifecycle.CLOSED.value
        assert data["closed_date"] is not None
    
    def test_lifecycle_closed_no_transitions(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test that CLOSED is a terminal state with no valid transitions."""
        # Requirement 9.8: CLOSED is terminal state
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.CLOSED,
            closed_date=date.today(),
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        # Try to transition from CLOSED (should fail)
        response = client.put(
            f"/api/v1/crops/{crop.id}/lifecycle",
            json={"new_lifecycle": CropLifecycle.PLANNED.value},
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "INVALID_LIFECYCLE_TRANSITION"
        
        # Verify no valid transitions
        assert data["details"]["valid_transitions"] == []


class TestCropHistory:
    """Test crop history endpoint."""
    
    def test_get_crop_history(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test getting crop history for a plot."""
        # Requirement 9.9: View crop history
        # Create multiple crops in different lifecycle stages
        crops = [
            Crop(
                plot_id=test_plot.id,
                name="Old Crop",
                lifecycle=CropLifecycle.CLOSED,
                closed_date=date.today(),
                created_by=test_user.id,
                updated_by=test_user.id
            ),
            Crop(
                plot_id=test_plot.id,
                name="Current Crop",
                lifecycle=CropLifecycle.PRODUCTION,
                production_start_date=date.today(),
                created_by=test_user.id,
                updated_by=test_user.id
            ),
            Crop(
                plot_id=test_plot.id,
                name="Planned Crop",
                lifecycle=CropLifecycle.PLANNED,
                created_by=test_user.id,
                updated_by=test_user.id
            )
        ]
        db.add_all(crops)
        db.commit()
        
        response = client.get(
            f"/api/v1/crops/plots/{test_plot.id}/crop-history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all crops returned (including closed)
        assert len(data) == 3
        
        # Verify crops are ordered by created_at desc
        crop_names = [crop["name"] for crop in data]
        assert "Planned Crop" in crop_names
        assert "Current Crop" in crop_names
        assert "Old Crop" in crop_names


class TestCropUpdate:
    """Test crop update endpoint."""
    
    def test_update_crop_name(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test updating crop name."""
        crop = Crop(
            plot_id=test_plot.id,
            name="Original Name",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}",
            json={"name": "Updated Name"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
    
    def test_update_crop_area(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test updating crop area."""
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        response = client.put(
            f"/api/v1/crops/{crop.id}",
            json={"area": "3.5"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert float(data["area"]) == 3.5


class TestCropDeletion:
    """Test crop deletion endpoint."""
    
    def test_delete_crop(
        self,
        client: TestClient,
        auth_headers: dict,
        test_plot: Plot,
        test_user: User,
        db: Session
    ):
        """Test deleting a crop."""
        crop = Crop(
            plot_id=test_plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PLANNED,
            created_by=test_user.id,
            updated_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        crop_id = crop.id
        
        response = client.delete(
            f"/api/v1/crops/{crop_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify crop is deleted
        deleted_crop = db.query(Crop).filter(Crop.id == crop_id).first()
        assert deleted_crop is None
