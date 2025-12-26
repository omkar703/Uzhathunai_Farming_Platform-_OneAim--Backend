"""
Unit tests for TemplateService.

Tests cover:
- Creating templates (system and organization)
- Updating templates
- Adding sections to templates
- Adding parameters to template sections
- Template copying with permission validation
"""
import pytest
from sqlalchemy.orm import Session
from uuid import uuid4, UUID

from app.services.template_service import TemplateService
from app.schemas.template import (
    TemplateCreate, TemplateUpdate, TemplateCopy,
    TemplateSectionAdd, TemplateParameterAdd,
    TemplateTranslationCreate
)
from app.models.template import Template, TemplateTranslation, TemplateSection, TemplateParameter
from app.models.section import Section, SectionTranslation
from app.models.parameter import Parameter, ParameterTranslation, ParameterType
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import OrganizationType
from app.core.exceptions import NotFoundError, PermissionError, ConflictError


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
    
    # Add translation
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
    
    # Add translation
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


def test_create_system_template(db: Session, test_user: User):
    """Test creating a system-defined template."""
    service = TemplateService(db)
    
    data = TemplateCreate(
        code=f"TEST_TEMPLATE_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Test Template",
                description="Test template description"
            )
        ]
    )
    
    template = service.create_template(data, test_user.id, organization_id=None)
    
    assert template.id is not None
    assert template.code == data.code
    assert template.is_system_defined is True
    assert template.owner_org_id is None
    assert template.version == 1
    assert len(template.translations) == 1


def test_create_organization_template(db: Session, test_user: User, test_organization: Organization):
    """Test creating an organization-specific template."""
    service = TemplateService(db)
    
    data = TemplateCreate(
        code=f"ORG_TEMPLATE_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Org Template",
                description="Organization template"
            )
        ]
    )
    
    template = service.create_template(data, test_user.id, organization_id=test_organization.id)
    
    assert template.id is not None
    assert template.is_system_defined is False
    assert template.owner_org_id == test_organization.id


def test_duplicate_template_code(db: Session, test_user: User):
    """Test that duplicate template codes are rejected."""
    service = TemplateService(db)
    
    code = f"DUPLICATE_{uuid4().hex[:8]}"
    data = TemplateCreate(
        code=code,
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Test Template",
                description="Test"
            )
        ]
    )
    
    # Create first template
    service.create_template(data, test_user.id, organization_id=None)
    
    # Try to create duplicate
    with pytest.raises(ConflictError) as exc_info:
        service.create_template(data, test_user.id, organization_id=None)
    
    assert "already exists" in str(exc_info.value.message).lower()


def test_add_section_to_template(
    db: Session,
    test_user: User,
    test_section: Section
):
    """Test adding a section to a template."""
    service = TemplateService(db)
    
    # Create template
    template_data = TemplateCreate(
        code=f"TEMPLATE_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Test Template",
                description="Test"
            )
        ]
    )
    template = service.create_template(template_data, test_user.id, organization_id=None)
    
    # Add section
    section_data = TemplateSectionAdd(
        section_id=test_section.id,
        sort_order=1
    )
    template_section = service.add_section_to_template(
        template.id,
        section_data,
        organization_id=None
    )
    
    assert template_section.id is not None
    assert template_section.template_id == template.id
    assert template_section.section_id == test_section.id
    assert template_section.sort_order == 1


def test_add_parameter_to_template_section(
    db: Session,
    test_user: User,
    test_section: Section,
    test_parameter: Parameter
):
    """Test adding a parameter to a template section."""
    service = TemplateService(db)
    
    # Create template
    template_data = TemplateCreate(
        code=f"TEMPLATE_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Test Template",
                description="Test"
            )
        ]
    )
    template = service.create_template(template_data, test_user.id, organization_id=None)
    
    # Add section
    section_data = TemplateSectionAdd(
        section_id=test_section.id,
        sort_order=1
    )
    template_section = service.add_section_to_template(
        template.id,
        section_data,
        organization_id=None
    )
    
    # Add parameter
    param_data = TemplateParameterAdd(
        parameter_id=test_parameter.id,
        is_required=True,
        sort_order=1
    )
    template_param = service.add_parameter_to_template_section(
        template.id,
        test_section.id,
        param_data,
        organization_id=None
    )
    
    assert template_param.id is not None
    assert template_param.template_section_id == template_section.id
    assert template_param.parameter_id == test_parameter.id
    assert template_param.is_required is True
    assert template_param.parameter_snapshot is not None


def test_copy_template_system_user(
    db: Session,
    test_user: User,
    test_section: Section,
    test_parameter: Parameter
):
    """Test template copying by system user."""
    service = TemplateService(db)
    
    # Create source template with section and parameter
    source_data = TemplateCreate(
        code=f"SOURCE_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Source Template",
                description="Source description"
            )
        ]
    )
    source_template = service.create_template(source_data, test_user.id, organization_id=None)
    
    # Add section
    section_data = TemplateSectionAdd(
        section_id=test_section.id,
        sort_order=1
    )
    service.add_section_to_template(source_template.id, section_data, organization_id=None)
    
    # Add parameter
    param_data = TemplateParameterAdd(
        parameter_id=test_parameter.id,
        is_required=True,
        sort_order=1
    )
    service.add_parameter_to_template_section(
        source_template.id,
        test_section.id,
        param_data,
        organization_id=None
    )
    
    # Copy template
    copy_data = TemplateCopy(
        new_code=f"COPY_{uuid4().hex[:8]}",
        new_name_translations={"en": "Copied Template"},
        crop_type_id=None
    )
    copied_template = service.copy_template(
        source_template.id,
        copy_data,
        test_user.id,
        organization_id=None,
        has_consultancy_service=False
    )
    
    assert copied_template.id != source_template.id
    assert copied_template.code == copy_data.new_code
    assert copied_template.is_system_defined is True
    assert len(copied_template.translations) == 1
    assert copied_template.translations[0].name == "Copied Template"
    
    # Verify sections were copied
    copied_sections = db.query(TemplateSection).filter(
        TemplateSection.template_id == copied_template.id
    ).all()
    assert len(copied_sections) == 1
    assert copied_sections[0].section_id == test_section.id
    
    # Verify parameters were copied
    copied_params = db.query(TemplateParameter).filter(
        TemplateParameter.template_section_id == copied_sections[0].id
    ).all()
    assert len(copied_params) == 1
    assert copied_params[0].parameter_id == test_parameter.id


def test_copy_template_permission_denied(
    db: Session,
    test_user: User,
    test_organization: Organization
):
    """Test that organization users without consultancy service cannot copy templates."""
    service = TemplateService(db)
    
    # Create source template
    source_data = TemplateCreate(
        code=f"SOURCE_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="Source Template",
                description="Source"
            )
        ]
    )
    source_template = service.create_template(
        source_data,
        test_user.id,
        organization_id=test_organization.id
    )
    
    # Try to copy without consultancy service
    copy_data = TemplateCopy(
        new_code=f"COPY_{uuid4().hex[:8]}",
        new_name_translations={"en": "Copied Template"},
        crop_type_id=None
    )
    
    with pytest.raises(PermissionError) as exc_info:
        service.copy_template(
            source_template.id,
            copy_data,
            test_user.id,
            organization_id=test_organization.id,
            has_consultancy_service=False
        )
    
    assert "consultancy service" in str(exc_info.value.message).lower()


def test_cannot_modify_system_template(db: Session, test_user: User, test_organization: Organization):
    """Test that organization users cannot modify system templates."""
    service = TemplateService(db)
    
    # Create system template
    template_data = TemplateCreate(
        code=f"SYSTEM_{uuid4().hex[:8]}",
        crop_type_id=None,
        is_active=True,
        translations=[
            TemplateTranslationCreate(
                language_code="en",
                name="System Template",
                description="System"
            )
        ]
    )
    template = service.create_template(template_data, test_user.id, organization_id=None)
    
    # Try to update as organization user
    update_data = TemplateUpdate(
        code=f"MODIFIED_{uuid4().hex[:8]}"
    )
    
    with pytest.raises(PermissionError) as exc_info:
        service.update_template(
            template.id,
            update_data,
            test_user.id,
            organization_id=test_organization.id
        )
    
    assert "system-defined" in str(exc_info.value.message).lower()
