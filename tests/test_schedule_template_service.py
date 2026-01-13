"""
Unit tests for ScheduleTemplateService.

Tests cover:
- Template creation with access control
- Template ownership validation
- Template copying functionality
"""
import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.services.schedule_template_service import ScheduleTemplateService
from app.schemas.schedule_template import ScheduleTemplateCreate, ScheduleTemplateTranslationCreate
from app.models.schedule_template import ScheduleTemplate
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.user import User
from app.models.crop_data import CropType
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope
)
from app.core.exceptions import PermissionError, ValidationError


@pytest.fixture
def crop_type(db: Session) -> CropType:
    """Get or create a test crop type."""
    # Try to get existing TOMATO crop type
    crop_type = db.query(CropType).filter(CropType.code == 'TOMATO').first()
    
    if crop_type:
        return crop_type
    
    # Create if doesn't exist
    from app.models.crop_data import CropCategory
    category = db.query(CropCategory).first()
    if not category:
        category = CropCategory(
            code='VEGETABLES',
            is_active=True
        )
        db.add(category)
        db.flush()
    
    # Create crop type
    crop_type = CropType(
        code='TOMATO',
        category_id=category.id,
        is_active=True
    )
    db.add(crop_type)
    db.commit()
    db.refresh(crop_type)
    return crop_type


@pytest.fixture
def system_user(db: Session) -> User:
    """Create a system user with SuperAdmin role."""
    # Create SuperAdmin role if not exists
    role = db.query(Role).filter(Role.code == 'SuperAdmin').first()
    if not role:
        role = Role(
            code='SuperAdmin',
            name='Super Administrator',
            display_name='Super Administrator',
            scope=UserRoleScope.SYSTEM,
            description='System administrator with full access',
            is_active=True
        )
        db.add(role)
        db.flush()
    
    # Create user
    user = User(
        email=f'admin_{uuid4()}@test.com',
        phone=f'+91{uuid4().hex[:10]}',
        password_hash='hashed_password',
        is_active=True
    )
    db.add(user)
    db.flush()
    
    # Assign SuperAdmin role
    member_role = OrgMemberRole(
        user_id=user.id,
        role_id=role.id,
        organization_id=None  # System role
    )
    db.add(member_role)
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture
def farming_user(db: Session) -> User:
    """Create a farming organization user."""
    user = User(
        email=f'farmer_{uuid4()}@test.com',
        phone=f'+91{uuid4().hex[:10]}',
        password_hash='hashed_password',
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_system_user_can_create_system_template(
    db: Session,
    system_user: User,
    crop_type: CropType
):
    """Test that system user can create system-defined template."""
    service = ScheduleTemplateService(db)
    
    data = ScheduleTemplateCreate(
        code='TOMATO_BASIC',
        crop_type_id=crop_type.id,
        is_system_defined=True,
        owner_org_id=None,
        translations=[
            ScheduleTemplateTranslationCreate(
                language_code='en',
                name='Basic Tomato Schedule',
                description='Standard schedule for tomato cultivation'
            )
        ]
    )
    
    template = service.create_template(
        user_id=system_user.id,
        data=data
    )
    
    assert template.id is not None
    assert template.code == 'TOMATO_BASIC'
    assert template.is_system_defined is True
    assert template.owner_org_id is None
    assert template.version == 1
    assert len(template.translations) == 1


def test_farming_user_cannot_create_template(
    db: Session,
    farming_user: User,
    crop_type: CropType
):
    """Test that farming organization user cannot create templates."""
    service = ScheduleTemplateService(db)
    
    data = ScheduleTemplateCreate(
        code='TOMATO_CUSTOM',
        crop_type_id=crop_type.id,
        is_system_defined=False,
        owner_org_id=None
    )
    
    with pytest.raises(PermissionError) as exc_info:
        service.create_template(
            user_id=farming_user.id,
            data=data
        )
    
    assert exc_info.value.error_code == 'TEMPLATE_CREATION_FORBIDDEN'


def test_system_template_is_immutable(
    db: Session,
    system_user: User,
    crop_type: CropType
):
    """Test that system-defined templates cannot be modified."""
    service = ScheduleTemplateService(db)
    
    # Create system template
    data = ScheduleTemplateCreate(
        code='TOMATO_SYSTEM',
        crop_type_id=crop_type.id,
        is_system_defined=True,
        owner_org_id=None
    )
    
    template = service.create_template(
        user_id=system_user.id,
        data=data
    )
    
    # Try to validate ownership for modification
    with pytest.raises(PermissionError) as exc_info:
        service.validate_template_ownership(
            template_id=template.id,
            user_id=system_user.id
        )
    
    assert exc_info.value.error_code == 'SYSTEM_TEMPLATE_IMMUTABLE'


def test_duplicate_template_code_rejected(
    db: Session,
    system_user: User,
    crop_type: CropType
):
    """Test that duplicate template codes are rejected."""
    service = ScheduleTemplateService(db)
    
    # Create first template
    data = ScheduleTemplateCreate(
        code='TOMATO_DUP',
        crop_type_id=crop_type.id,
        is_system_defined=True,
        owner_org_id=None
    )
    
    service.create_template(
        user_id=system_user.id,
        data=data
    )
    
    # Try to create duplicate
    with pytest.raises(ValidationError) as exc_info:
        service.create_template(
            user_id=system_user.id,
            data=data
        )
    
    assert exc_info.value.error_code == 'DUPLICATE_TEMPLATE_CODE'


def test_get_templates_filters_by_ownership(
    db: Session,
    system_user: User,
    farming_user: User,
    crop_type: CropType
):
    """Test that get_templates returns system templates for all users."""
    service = ScheduleTemplateService(db)
    
    # Create system template
    data = ScheduleTemplateCreate(
        code='TOMATO_PUBLIC',
        crop_type_id=crop_type.id,
        is_system_defined=True,
        owner_org_id=None
    )
    
    service.create_template(
        user_id=system_user.id,
        data=data
    )
    
    # Farming user should see system templates
    templates, total = service.get_templates(
        user_id=farming_user.id,
        page=1,
        limit=20
    )
    
    assert total >= 1
    assert any(t.code == 'TOMATO_PUBLIC' for t in templates)
