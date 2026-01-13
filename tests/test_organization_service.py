"""
Unit tests for OrganizationService.

Tests cover:
- Creating FARMING organizations
- Creating FSP organizations with services
- Duplicate name validation
"""
import pytest
from sqlalchemy.orm import Session
from uuid import uuid4

from app.services.organization_service import OrganizationService
from app.schemas.organization import OrganizationCreate, FSPServiceListingCreate
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.fsp_service import FSPServiceListing, MasterService
from app.models.rbac import Role
from app.models.subscription import SubscriptionPlan
from app.models.user import User
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope,
    ServiceStatus
)
from app.core.exceptions import ConflictError


@pytest.fixture
def owner_role(db: Session) -> Role:
    """Get or create OWNER role for FARMING organizations."""
    role = db.query(Role).filter(Role.code == 'OWNER').first()
    if not role:
        role = Role(
            code='OWNER',
            name='Owner',
            display_name='Organization Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of farming organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def fsp_owner_role(db: Session) -> Role:
    """Get or create FSP_OWNER role for FSP organizations."""
    role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
    if not role:
        role = Role(
            code='FSP_OWNER',
            name='FSP Owner',
            display_name='FSP Organization Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of FSP organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def farming_subscription_plan(db: Session) -> SubscriptionPlan:
    """Get existing BASIC subscription plan for FARMING organizations."""
    # Use existing plan from database (FREE, BASIC, PREMIUM, ENTERPRISE)
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == 'BASIC',
        SubscriptionPlan.category == 'FARMING'
    ).first()
    if not plan:
        # Fallback to FREE plan if BASIC not found
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == 'FREE'
        ).first()
    return plan


@pytest.fixture
def fsp_subscription_plan(db: Session) -> SubscriptionPlan:
    """Get existing BASIC subscription plan for FSP organizations."""
    # FSP organizations can use universal plans (category=NULL) or FARMING plans
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.name == 'BASIC'
    ).first()
    if not plan:
        # Fallback to FREE plan
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.name == 'FREE'
        ).first()
    return plan


@pytest.fixture
def master_service(db: Session) -> MasterService:
    """Get or create a master service for FSP testing."""
    service = db.query(MasterService).filter(MasterService.code == 'SOIL_TESTING').first()
    if not service:
        service = MasterService(
            code='SOIL_TESTING',
            name='Soil Testing',
            description='Professional soil testing and analysis',
            status=ServiceStatus.ACTIVE,
            sort_order=1
        )
        db.add(service)
        db.commit()
        db.refresh(service)
    return service


class TestOrganizationServiceCreateFarming:
    """Tests for creating FARMING organizations."""
    
    def test_create_farming_organization_success(
        self,
        db: Session,
        test_user: User,
        owner_role: Role,
        farming_subscription_plan: SubscriptionPlan
    ):
        """Test successful FARMING organization creation."""
        service = OrganizationService(db)
        
        org_data = OrganizationCreate(
            name="Green Valley Farm",
            organization_type=OrganizationType.FARMING,
            description="A sustainable farming organization",
            district="Coimbatore",
            pincode="641001",
            contact_email="contact@greenvalley.com",
            contact_phone="+919876543210"
        )
        
        org = service.create_organization(org_data, test_user.id)
        
        # Verify organization created
        assert org.id is not None
        assert org.name == "Green Valley Farm"
        assert org.organization_type == OrganizationType.FARMING
        assert org.status == OrganizationStatus.ACTIVE  # FARMING orgs are ACTIVE immediately
        assert org.description == "A sustainable farming organization"
        assert org.district == "Coimbatore"
        assert org.pincode == "641001"
        assert org.contact_email == "contact@greenvalley.com"
        assert org.contact_phone == "+919876543210"
        assert org.created_by == test_user.id
        
        # Verify subscription assigned
        assert org.subscription_plan_id is not None
        assert org.subscription_start_date is not None
        assert org.subscription_end_date is not None
        
        # Verify owner membership created
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org.id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        # Verify owner role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == org.id,
            OrgMemberRole.user_id == test_user.id
        ).first()
        assert member_role is not None
        assert member_role.role_id == owner_role.id
        assert member_role.is_primary is True
    
    def test_create_farming_organization_minimal_data(
        self,
        db: Session,
        test_user: User,
        owner_role: Role,
        farming_subscription_plan: SubscriptionPlan
    ):
        """Test FARMING organization creation with minimal required data."""
        service = OrganizationService(db)
        
        org_data = OrganizationCreate(
            name="Simple Farm",
            organization_type=OrganizationType.FARMING
        )
        
        org = service.create_organization(org_data, test_user.id)
        
        # Verify organization created with minimal data
        assert org.id is not None
        assert org.name == "Simple Farm"
        assert org.organization_type == OrganizationType.FARMING
        assert org.status == OrganizationStatus.ACTIVE
        assert org.description is None
        assert org.district is None
        assert org.created_by == test_user.id
        
        # Verify owner membership and role created
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org.id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None


class TestOrganizationServiceCreateFSP:
    """Tests for creating FSP organizations with services."""
    
    def test_create_fsp_organization_with_services(
        self,
        db: Session,
        test_user: User,
        fsp_owner_role: Role,
        fsp_subscription_plan: SubscriptionPlan,
        master_service: MasterService
    ):
        """Test successful FSP organization creation with services."""
        service = OrganizationService(db)
        
        org_data = OrganizationCreate(
            name="AgriConsult Services",
            organization_type=OrganizationType.FSP,
            description="Professional agricultural consulting",
            district="Chennai",
            pincode="600001",
            contact_email="info@agriconsult.com",
            contact_phone="+919123456789",
            services=[
                FSPServiceListingCreate(
                    service_id=master_service.id,
                    title="Expert Soil Testing",
                    description="Comprehensive soil analysis with recommendations",
                    service_area_districts=["Chennai", "Kanchipuram", "Tiruvallur"],
                    pricing_model="PER_ACRE",
                    base_price=500.00
                )
            ]
        )
        
        org = service.create_organization(org_data, test_user.id)
        
        # Verify organization created
        assert org.id is not None
        assert org.name == "AgriConsult Services"
        assert org.organization_type == OrganizationType.FSP
        assert org.status == OrganizationStatus.NOT_STARTED  # FSP with services starts NOT_STARTED
        assert org.description == "Professional agricultural consulting"
        assert org.district == "Chennai"
        assert org.created_by == test_user.id
        
        # Verify FSP service listing created
        service_listing = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == org.id
        ).first()
        assert service_listing is not None
        assert service_listing.service_id == master_service.id
        assert service_listing.title == "Expert Soil Testing"
        assert service_listing.description == "Comprehensive soil analysis with recommendations"
        assert service_listing.service_area_districts == ["Chennai", "Kanchipuram", "Tiruvallur"]
        assert service_listing.pricing_model == "PER_ACRE"
        assert float(service_listing.base_price) == 500.00
        assert service_listing.status == ServiceStatus.ACTIVE
        assert service_listing.created_by == test_user.id
        
        # Verify owner membership created
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org.id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        # Verify FSP owner role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == org.id,
            OrgMemberRole.user_id == test_user.id
        ).first()
        assert member_role is not None
        assert member_role.role_id == fsp_owner_role.id
        assert member_role.is_primary is True
    
    def test_create_fsp_organization_multiple_services(
        self,
        db: Session,
        test_user: User,
        fsp_owner_role: Role,
        fsp_subscription_plan: SubscriptionPlan,
        master_service: MasterService
    ):
        """Test FSP organization creation with multiple services."""
        # Create another master service
        service2 = MasterService(
            code='CROP_ADVISORY',
            name='Crop Advisory',
            description='Expert crop management advice',
            status=ServiceStatus.ACTIVE,
            sort_order=2
        )
        db.add(service2)
        db.commit()
        db.refresh(service2)
        
        service = OrganizationService(db)
        
        org_data = OrganizationCreate(
            name="Multi-Service FSP",
            organization_type=OrganizationType.FSP,
            services=[
                FSPServiceListingCreate(
                    service_id=master_service.id,
                    title="Soil Testing Service",
                    description="Professional soil testing",
                    service_area_districts=["Chennai"],
                    pricing_model="PER_ACRE",
                    base_price=500.00
                ),
                FSPServiceListingCreate(
                    service_id=service2.id,
                    title="Crop Advisory Service",
                    description="Expert crop management",
                    service_area_districts=["Chennai", "Vellore"],
                    pricing_model="PER_HOUR",
                    base_price=200.00
                )
            ]
        )
        
        org = service.create_organization(org_data, test_user.id)
        
        # Verify both service listings created
        service_listings = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == org.id
        ).all()
        assert len(service_listings) == 2
        
        # Verify service details
        titles = [sl.title for sl in service_listings]
        assert "Soil Testing Service" in titles
        assert "Crop Advisory Service" in titles


class TestOrganizationServiceDuplicateValidation:
    """Tests for duplicate organization name validation."""
    
    def test_create_organization_duplicate_name(
        self,
        db: Session,
        test_user: User,
        owner_role: Role,
        farming_subscription_plan: SubscriptionPlan
    ):
        """Test that duplicate organization names are rejected for same user."""
        service = OrganizationService(db)
        
        # Create first organization
        org_data1 = OrganizationCreate(
            name="Duplicate Farm",
            organization_type=OrganizationType.FARMING
        )
        org1 = service.create_organization(org_data1, test_user.id)
        assert org1.id is not None
        
        # Try to create second organization with same name
        org_data2 = OrganizationCreate(
            name="Duplicate Farm",
            organization_type=OrganizationType.FARMING
        )
        
        with pytest.raises(ConflictError) as exc_info:
            service.create_organization(org_data2, test_user.id)
        
        assert exc_info.value.error_code == "ORG_NAME_EXISTS"
        assert "already exists" in str(exc_info.value.message).lower()
    
    def test_create_organization_same_name_different_users(
        self,
        db: Session,
        test_user: User,
        owner_role: Role,
        farming_subscription_plan: SubscriptionPlan
    ):
        """Test that same organization name is allowed for different users."""
        service = OrganizationService(db)
        
        # Create second user
        from app.core.security import get_password_hash
        user2 = User(
            email="user2@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="User",
            last_name="Two",
            phone="+919876543211",
            preferred_language="en",
            is_active=True,
            is_verified=False
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)
        
        # Create organization for first user
        org_data1 = OrganizationCreate(
            name="Common Farm Name",
            organization_type=OrganizationType.FARMING
        )
        org1 = service.create_organization(org_data1, test_user.id)
        assert org1.id is not None
        
        # Create organization with same name for second user - should succeed
        org_data2 = OrganizationCreate(
            name="Common Farm Name",
            organization_type=OrganizationType.FARMING
        )
        org2 = service.create_organization(org_data2, user2.id)
        assert org2.id is not None
        assert org2.id != org1.id
        assert org2.name == org1.name
