"""
Integration tests for Farm API endpoints.

Tests POST /farms, GET /farms, boundary validation, and area calculation.
Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9
"""
import pytest
from uuid import UUID
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus
from app.models.measurement_unit import MeasurementUnit
from app.models.enums import MeasurementUnitCategory


@pytest.fixture
def test_organization(db: Session, test_user: User) -> Organization:
    """Create a test farming organization."""
    org = Organization(
        name="Test Farm Organization",
        description="Test organization for farming",
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
def test_area_unit(db: Session) -> MeasurementUnit:
    """Get or create a test area measurement unit (acres)."""
    # Try to get existing unit first
    unit = db.query(MeasurementUnit).filter(
        MeasurementUnit.code == "ACRE"
    ).first()
    
    if unit:
        return unit
    
    # Create new unit if it doesn't exist
    unit = MeasurementUnit(
        category=MeasurementUnitCategory.AREA,
        code="ACRE",
        symbol="ac",
        is_base_unit=True,
        conversion_factor=Decimal("1.0"),
        sort_order=1
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


class TestFarmCreation:
    """Test farm creation endpoint."""
    
    def test_create_farm_with_location_only(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test creating farm with location only (no boundary)."""
        # Requirement 7.1: Create farm with organization ID, farm name, and location coordinates
        farm_data = {
            "name": "Green Valley Farm",
            "description": "A beautiful farm in the valley",
            "address": "123 Farm Road",
            "district": "Test District",
            "state": "Test State",
            "pincode": "123456",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]  # Bangalore coordinates
            },
            "area": 10.5,
            "area_unit_id": str(test_area_unit.id)
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["name"] == "Green Valley Farm"
        assert data["description"] == "A beautiful farm in the valley"
        assert data["district"] == "Test District"
        assert data["location"]["type"] == "Point"
        assert data["location"]["coordinates"] == [77.5946, 12.9716]
        assert data["boundary"] is None
        assert float(data["area"]) == 10.5
        assert data["is_active"] is True
    
    def test_create_farm_with_boundary(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test creating farm with boundary polygon."""
        # Requirement 7.2: Define farm boundaries using GEOGRAPHY(POLYGON, 4326)
        # Requirement 7.7: Display farm boundaries on maps using GIS capabilities
        farm_data = {
            "name": "Boundary Farm",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [77.5946, 12.9716],
                    [77.5956, 12.9716],
                    [77.5956, 12.9726],
                    [77.5946, 12.9726],
                    [77.5946, 12.9716]  # Closed polygon
                ]]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify boundary is stored
        assert data["boundary"] is not None
        assert data["boundary"]["type"] == "Polygon"
        assert len(data["boundary"]["coordinates"][0]) == 5  # 4 corners + closing point
        
        # Verify area is calculated when boundary provided
        # Requirement 7.3: Calculate farm area
        assert data["area"] is not None
        assert float(data["area"]) > 0
    
    def test_create_farm_with_attributes(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test creating farm with farm attributes."""
        # Requirement 7.4: Store farm attributes in JSONB
        farm_data = {
            "name": "Attribute Farm",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "farm_attributes": {
                "soil_ec": 2.5,
                "soil_ph": 6.8,
                "water_ec": 1.2,
                "water_ph": 7.0
            },
            "area_unit_id": str(test_area_unit.id)
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify attributes are stored
        assert data["farm_attributes"] is not None
        assert data["farm_attributes"]["soil_ec"] == 2.5
        assert data["farm_attributes"]["soil_ph"] == 6.8
        assert data["farm_attributes"]["water_ec"] == 1.2
        assert data["farm_attributes"]["water_ph"] == 7.0
    
    def test_create_farm_invalid_location_coordinates(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization
    ):
        """Test creating farm with invalid location coordinates."""
        # Requirement 7.2: Validate location coordinates
        farm_data = {
            "name": "Invalid Location Farm",
            "location": {
                "type": "Point",
                "coordinates": [200.0, 100.0]  # Invalid: lon > 180, lat > 90
            }
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422
        error_data = response.json()
        assert error_data["success"] is False
        assert "coordinates" in str(error_data).lower() or "longitude" in str(error_data).lower()
    
    def test_create_farm_invalid_boundary_not_closed(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization
    ):
        """Test creating farm with non-closed boundary polygon."""
        # Requirement 7.2: Validate boundary polygon is closed
        farm_data = {
            "name": "Invalid Boundary Farm",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [77.5946, 12.9716],
                    [77.5956, 12.9716],
                    [77.5956, 12.9726],
                    [77.5946, 12.9726]
                    # Missing closing point - not closed!
                ]]
            }
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422
        error_data = response.json()
        assert error_data["success"] is False
        assert "closed" in str(error_data).lower()
    
    def test_create_farm_invalid_boundary_too_few_points(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization
    ):
        """Test creating farm with boundary having too few points."""
        # Requirement 7.2: Validate boundary has at least 4 points
        farm_data = {
            "name": "Invalid Boundary Farm",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [77.5946, 12.9716],
                    [77.5956, 12.9716],
                    [77.5946, 12.9716]  # Only 3 points (including closing)
                ]]
            }
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        # Should fail validation
        assert response.status_code == 422
        error_data = response.json()
        assert error_data["success"] is False
        assert "4 points" in str(error_data).lower() or "at least" in str(error_data).lower()


class TestFarmRetrieval:
    """Test farm retrieval endpoints."""
    
    def test_get_farms_list(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test getting list of farms with pagination."""
        # Requirement 7.1: Get farms for organization
        # Create multiple farms
        for i in range(3):
            farm_data = {
                "name": f"Farm {i+1}",
                "location": {
                    "type": "Point",
                    "coordinates": [77.5946 + i*0.01, 12.9716 + i*0.01]
                },
                "area_unit_id": str(test_area_unit.id)
            }
            client.post("/api/v1/farms/", json=farm_data, headers=auth_headers)
        
        # Get farms list
        response = client.get(
            "/api/v1/farms/?page=1&limit=10",
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
        
        # Verify farms are returned
        assert len(data["items"]) == 3
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["limit"] == 10
    
    def test_get_farm_by_id(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test getting specific farm by ID."""
        # Requirement 7.1: Get farm by ID
        # Create farm
        farm_data = {
            "name": "Specific Farm",
            "description": "Farm to retrieve",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        create_response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        farm_id = create_response.json()["id"]
        
        # Get farm by ID
        response = client.get(
            f"/api/v1/farms/{farm_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify farm details
        assert data["id"] == farm_id
        assert data["name"] == "Specific Farm"
        assert data["description"] == "Farm to retrieve"
    
    def test_get_farm_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization
    ):
        """Test getting non-existent farm."""
        # Requirement 7.1: Handle farm not found
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = client.get(
            f"/api/v1/farms/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["success"] is False
        assert error_data["error_code"] == "FARM_NOT_FOUND"


class TestFarmUpdate:
    """Test farm update endpoint."""
    
    def test_update_farm_basic_fields(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test updating farm basic fields."""
        # Requirement 7.8: Update farm details
        # Create farm
        farm_data = {
            "name": "Original Farm",
            "description": "Original description",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        create_response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        farm_id = create_response.json()["id"]
        
        # Update farm
        update_data = {
            "name": "Updated Farm",
            "description": "Updated description",
            "district": "New District"
        }
        response = client.put(
            f"/api/v1/farms/{farm_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify updates
        assert data["name"] == "Updated Farm"
        assert data["description"] == "Updated description"
        assert data["district"] == "New District"
    
    def test_update_farm_boundary(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test updating farm boundary."""
        # Requirement 7.8: Update farm boundary with validation
        # Create farm without boundary
        farm_data = {
            "name": "Farm to Update",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        create_response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        farm_id = create_response.json()["id"]
        
        # Update with boundary
        update_data = {
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [77.5946, 12.9716],
                    [77.5956, 12.9716],
                    [77.5956, 12.9726],
                    [77.5946, 12.9726],
                    [77.5946, 12.9716]
                ]]
            }
        }
        response = client.put(
            f"/api/v1/farms/{farm_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify boundary is updated
        assert data["boundary"] is not None
        assert data["boundary"]["type"] == "Polygon"
        
        # Verify area is recalculated
        assert data["area"] is not None
        assert float(data["area"]) > 0


class TestFarmDeletion:
    """Test farm deletion endpoint."""
    
    def test_delete_farm(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test soft deleting farm."""
        # Requirement 7.9: Soft delete farm using is_active flag
        # Create farm
        farm_data = {
            "name": "Farm to Delete",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        create_response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        farm_id = create_response.json()["id"]
        
        # Delete farm
        response = client.delete(
            f"/api/v1/farms/{farm_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify farm is not accessible (soft deleted)
        get_response = client.get(
            f"/api/v1/farms/{farm_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404


class TestFarmSupervisors:
    """Test farm supervisor management."""
    
    def test_assign_supervisor(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit,
        db: Session
    ):
        """Test assigning supervisor to farm."""
        # Requirement 7.5: Assign supervisors to farm
        # Create farm
        farm_data = {
            "name": "Supervised Farm",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        create_response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        farm_id = create_response.json()["id"]
        
        # Create another user to be supervisor
        from app.models.user import User
        from app.core.security import get_password_hash
        supervisor = User(
            email="supervisor@example.com",
            password_hash=get_password_hash("SuperPass123!"),
            first_name="Super",
            last_name="Visor",
            phone="+1234567892",
            preferred_language="en",
            is_active=True
        )
        db.add(supervisor)
        db.commit()
        db.refresh(supervisor)
        
        # Add supervisor to organization
        member = OrgMember(
            user_id=supervisor.id,
            organization_id=test_organization.id,
            status=MemberStatus.ACTIVE
        )
        db.add(member)
        db.commit()
        
        # Assign supervisor
        response = client.post(
            f"/api/v1/farms/{farm_id}/supervisors?supervisor_id={supervisor.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Supervisor assigned successfully"


class TestAreaCalculation:
    """Test area calculation from boundary."""
    
    def test_area_calculated_from_boundary(
        self,
        client: TestClient,
        auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """Test that area is automatically calculated from boundary."""
        # Requirement 7.3: Calculate farm area using PostGIS
        farm_data = {
            "name": "Auto Area Farm",
            "location": {
                "type": "Point",
                "coordinates": [77.5946, 12.9716]
            },
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [77.5946, 12.9716],
                    [77.5956, 12.9716],
                    [77.5956, 12.9726],
                    [77.5946, 12.9726],
                    [77.5946, 12.9716]
                ]]
            },
            "area_unit_id": str(test_area_unit.id)
            # Note: No area provided - should be calculated
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify area was calculated
        assert data["area"] is not None
        assert float(data["area"]) > 0
        
        # Area should be reasonable for the given boundary
        # (approximately 0.01 degrees x 0.01 degrees near Bangalore)
        # At this latitude, 0.01 degrees ≈ 1.1 km, so area ≈ 1.21 km² = 1,210,000 m²
        # But PostGIS calculates on the spheroid, so it's ~12,000 m²
        assert float(data["area"]) > 10000  # Should be more than 10,000 square meters
        assert float(data["area"]) < 15000  # Should be less than 15,000 square meters
