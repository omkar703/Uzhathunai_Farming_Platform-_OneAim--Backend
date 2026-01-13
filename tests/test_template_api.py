"""
API tests for Template endpoints.

Tests cover:
- GET /api/v1/farm-audit/templates (list templates)
- GET /api/v1/farm-audit/templates/{id} (get template)
- POST /api/v1/farm-audit/templates (create template)
- PUT /api/v1/farm-audit/templates/{id} (update template)
- DELETE /api/v1/farm-audit/templates/{id} (delete template)
- POST /api/v1/farm-audit/templates/{id}/sections (add section)
- POST /api/v1/farm-audit/templates/{id}/sections/{section_id}/parameters (add parameter)
- POST /api/v1/farm-audit/templates/{id}/copy (copy template)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.models.user import User
from app.models.organization import Organization, OrgMember
from app.models.section import Section, SectionTranslation
from app.models.parameter import Parameter, ParameterTranslation, ParameterType
from app.models.enums import OrganizationType, MemberStatus
from app.core.security import create_access_token


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        email=f"test_{uuid4()}@example.com",
        phone="+911234567890",
        first_name="Test",
        last_name="User",
        password_hash="hashed_password",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_organization(db: Session, test_user: User) -> Organization:
    """Create a test organization."""
    org = Organization(
        name=f"Test Org {uuid4()}",
        organization_type=OrganizationType.FARMING,
        created_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Add user as member
    member = OrgMember(
        organization_id=org.id,
        user_id=test_user.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
    return org


@pytest.fixture
def test_section(db: Session, test_user: User) -> Section:
    """Create a test section."""
    section = Section(
        code=f"TEST_SECTION_{uuid4().hex[:8]}",
        is_system_defined=True,
        owner_org_id=None,
        is_active=True,
        created_by=test_user.id
    )
    db.add(section)
    db.flush()
    
    translation = SectionTranslation(
        section_id=section.id,
        language_code="en",
        name="Test Section",
        description="Test section description"
    )
    db.add(translation)
    db.commit()
    db.refresh(section)
    return section


@pytest.fixture
def test_parameter(db: Session, test_user: User) -> Parameter:
    """Create a test parameter."""
    parameter = Parameter(
        code=f"TEST_PARAM_{uuid4().hex[:8]}",
        parameter_type=ParameterType.TEXT,
        is_system_defined=True,
        owner_org_id=None,
        is_active=True,
        parameter_metadata={},
        created_by=test_user.id
    )
    db.add(parameter)
    db.flush()
    
    translation = ParameterTranslation(
        parameter_id=parameter.id,
        language_code="en",
        name="Test Parameter",
        description="Test parameter description",
        help_text="Test help text"
    )
    db.add(translation)
    db.commit()
    db.refresh(parameter)
    return parameter


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_create_template(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization
):
    """Test creating a template."""
    data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test template description"
            }
        ]
    }
    
    response = client.post(
        "/api/v1/farm-audit/templates",
        json=data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = response.json()
    assert result["code"] == data["code"]
    assert result["is_active"] is True
    assert len(result["translations"]) == 1


def test_get_templates(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization
):
    """Test getting templates list."""
    # Create a template first
    create_data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test"
            }
        ]
    }
    client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    
    # Get templates
    response = client.get(
        "/api/v1/farm-audit/templates",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "limit" in result
    assert "total_pages" in result
    assert len(result["items"]) > 0


def test_get_template_by_id(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization
):
    """Test getting a template by ID."""
    # Create a template
    create_data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test"
            }
        ]
    }
    create_response = client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    template_id = create_response.json()["id"]
    
    # Get template by ID
    response = client.get(
        f"/api/v1/farm-audit/templates/{template_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == template_id
    assert result["code"] == create_data["code"]


def test_update_template(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization
):
    """Test updating a template."""
    # Create a template
    create_data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test"
            }
        ]
    }
    create_response = client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    template_id = create_response.json()["id"]
    
    # Update template
    update_data = {
        "is_active": False
    }
    response = client.put(
        f"/api/v1/farm-audit/templates/{template_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["is_active"] is False


def test_delete_template(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization
):
    """Test deleting a template."""
    # Create a template
    create_data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test"
            }
        ]
    }
    create_response = client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    template_id = create_response.json()["id"]
    
    # Delete template
    response = client.delete(
        f"/api/v1/farm-audit/templates/{template_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 204
    
    # Verify template is deleted
    get_response = client.get(
        f"/api/v1/farm-audit/templates/{template_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_add_section_to_template(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization,
    test_section: Section
):
    """Test adding a section to a template."""
    # Create a template
    create_data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test"
            }
        ]
    }
    create_response = client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    template_id = create_response.json()["id"]
    
    # Add section
    section_data = {
        "section_id": str(test_section.id),
        "sort_order": 1
    }
    response = client.post(
        f"/api/v1/farm-audit/templates/{template_id}/sections",
        json=section_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = response.json()
    assert result["template_id"] == template_id
    assert result["section_id"] == str(test_section.id)


def test_add_parameter_to_template_section(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization,
    test_section: Section,
    test_parameter: Parameter
):
    """Test adding a parameter to a template section."""
    # Create a template
    create_data = {
        "code": f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Test Template",
                "description": "Test"
            }
        ]
    }
    create_response = client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    template_id = create_response.json()["id"]
    
    # Add section
    section_data = {
        "section_id": str(test_section.id),
        "sort_order": 1
    }
    client.post(
        f"/api/v1/farm-audit/templates/{template_id}/sections",
        json=section_data,
        headers=auth_headers
    )
    
    # Add parameter
    param_data = {
        "parameter_id": str(test_parameter.id),
        "is_required": True,
        "sort_order": 1
    }
    response = client.post(
        f"/api/v1/farm-audit/templates/{template_id}/sections/{test_section.id}/parameters",
        json=param_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = response.json()
    assert result["parameter_id"] == str(test_parameter.id)
    assert result["is_required"] is True


def test_copy_template(
    client: TestClient,
    auth_headers: dict,
    test_organization: Organization,
    test_section: Section,
    test_parameter: Parameter
):
    """Test copying a template."""
    # Create a template with section and parameter
    create_data = {
        "code": f"SOURCE_{uuid4().hex[:8]}",
        "crop_type_id": None,
        "is_active": True,
        "translations": [
            {
                "language_code": "en",
                "name": "Source Template",
                "description": "Source"
            }
        ]
    }
    create_response = client.post(
        "/api/v1/farm-audit/templates",
        json=create_data,
        headers=auth_headers
    )
    template_id = create_response.json()["id"]
    
    # Add section
    section_data = {
        "section_id": str(test_section.id),
        "sort_order": 1
    }
    client.post(
        f"/api/v1/farm-audit/templates/{template_id}/sections",
        json=section_data,
        headers=auth_headers
    )
    
    # Add parameter
    param_data = {
        "parameter_id": str(test_parameter.id),
        "is_required": True,
        "sort_order": 1
    }
    client.post(
        f"/api/v1/farm-audit/templates/{template_id}/sections/{test_section.id}/parameters",
        json=param_data,
        headers=auth_headers
    )
    
    # Copy template
    copy_data = {
        "new_code": f"COPY_{uuid4().hex[:8]}",
        "new_name_translations": {
            "en": "Copied Template"
        },
        "crop_type_id": None
    }
    response = client.post(
        f"/api/v1/farm-audit/templates/{template_id}/copy",
        json=copy_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = response.json()
    assert result["code"] == copy_data["new_code"]
    assert result["id"] != template_id
