"""
Verification test for Farm GIS Features.
Tests farm creation with specific GeoJSON payload provided by user.
"""
import pytest
import json
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.models.enums import OrganizationType, OrganizationStatus, MemberStatus
from app.models.measurement_unit import MeasurementUnit
from app.models.enums import MeasurementUnitCategory
from app.core.security import get_password_hash


@pytest.fixture
def local_test_user(db: Session) -> User:
    """Create a verified test user."""
    user = User(
        email="gistest@example.com",
        password_hash=get_password_hash("TestPass123!"),
        first_name="GIS",
        last_name="Tester",
        phone="+19998887777",
        preferred_language="en",
        is_active=True,
        is_verified=True  # Ensure verified
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def local_auth_headers(client: TestClient, local_test_user: User) -> dict:
    """Get authentication headers with correct response parsing."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": local_test_user.email,
            "password": "TestPass123!",
            "remember_me": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Handle BaseResponse wrapper if present
    if "data" in data and "tokens" in data["data"]:
        access_token = data["data"]["tokens"]["access_token"]
    elif "tokens" in data:
        access_token = data["tokens"]["access_token"]
    else:
        # Fallback for direct token response
        access_token = data.get("access_token")
        
    if not access_token:
        pytest.fail(f"Could not extract access token from login response: {data}")
        
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_organization(db: Session, local_test_user: User) -> Organization:
    """Create a test farming organization."""
    org = Organization(
        name="Test GIS Org",
        description="Organization for GIS testing",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=local_test_user.id,
        updated_by=local_test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Add user as member
    member = OrgMember(
        user_id=local_test_user.id,
        organization_id=org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
    return org


@pytest.fixture
def test_area_unit(db: Session) -> MeasurementUnit:
    """Get or create Acres unit."""
    unit = db.query(MeasurementUnit).filter(
        MeasurementUnit.code == "ACRE"
    ).first()
    
    if unit:
        return unit
    
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


class TestFarmGISPayload:
    """Test using the specific user-provided JSON payload."""
    
    def test_create_farm_with_user_payload(
        self,
        client: TestClient,
        local_auth_headers: dict,
        test_organization: Organization,
        test_area_unit: MeasurementUnit
    ):
        """
        Verify farm creation with the specific JSON including 
        Point location and Polygon boundary.
        """
        # User Provided Payload
        farm_data = {
            "name": "Green Valley Farm fifth",
            "description": "Demo farm created via API",
            "address": "Village Road, Near Main Canal",
            "district": "Coimbatore",
            "state": "Tamil Nadu",
            "pincode": "641001",
            "location": {
                "type": "Point",
                "coordinates": [76.9558, 11.0168]
            },
            "boundary": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [76.9548, 11.0162],
                        [76.9566, 11.0162],
                        [76.9566, 11.0176],
                        [76.9548, 11.0176],
                        [76.9548, 11.0162]
                    ]
                ]
            },
            "area_unit_id": str(test_area_unit.id)
        }
        
        response = client.post(
            "/api/v1/farms/",
            json=farm_data,
            headers=local_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify basic fields
        assert data["name"] == "Green Valley Farm fifth"
        assert data["district"] == "Coimbatore"
        
        # Verify Location (Point)
        assert data["location"]["type"] == "Point"
        assert data["location"]["coordinates"] == [76.9558, 11.0168]
        
        # Verify Boundary (Polygon)
        assert data["boundary"]["type"] == "Polygon"
        ring = data["boundary"]["coordinates"][0]
        assert len(ring) == 5
        
        # Verify Area Calculation
        assert data["area"] is not None
        area_val = float(data["area"])
        assert 20000 < area_val < 40000
        
        print("\nCreated Farm ID:", data["id"])
        print("Calculated Area (sq m):", area_val)
