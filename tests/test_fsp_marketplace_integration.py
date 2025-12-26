"""
Integration tests for FSP Marketplace.

Task 13.1: Write integration tests for FSP marketplace
- Test service listing creation and approval workflow
- Test marketplace browsing with filters
- Requirements: 1.1, 1.7, 14.4

These tests verify the complete FSP marketplace flow including:
1. Service listing creation (requires ACTIVE FSP organization)
2. FSP organization approval workflow (SuperAdmin)
3. Marketplace browsing with various filters
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.fsp_service import MasterService, FSPServiceListing, FSPApprovalDocument
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope,
    ServiceStatus
)


@pytest.fixture
def fsp_owner_role(db: Session) -> Role:
    """Get or create FSP_OWNER role."""
    role = db.query(Role).filter(Role.code == 'FSP_OWNER').first()
    if not role:
        role = Role(
            code='FSP_OWNER',
            name='FSP_OWNER',
            display_name='FSP Owner',
            scope=UserRoleScope.ORGANIZATION,
            description='Owner of FSP organization',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def super_admin_role(db: Session) -> Role:
    """Get or create SUPER_ADMIN role."""
    role = db.query(Role).filter(Role.code == 'SUPER_ADMIN').first()
    if not role:
        role = Role(
            code='SUPER_ADMIN',
            name='SUPER_ADMIN',
            display_name='Super Administrator',
            scope=UserRoleScope.SYSTEM,
            description='System super administrator',
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@pytest.fixture
def master_service_consultancy(db: Session) -> MasterService:
    """Get or create consultancy master service."""
    service = db.query(MasterService).filter(MasterService.code == 'CONSULTANCY').first()
    if not service:
        service = MasterService(
            code='CONSULTANCY',
            name='Agricultural Consultancy',
            description='Professional agricultural consulting services',
            status=ServiceStatus.ACTIVE,
            sort_order=1
        )
        db.add(service)
        db.commit()
        db.refresh(service)
    return service


@pytest.fixture
def master_service_soil_testing(db: Session) -> MasterService:
    """Get or create soil testing master service."""
    service = db.query(MasterService).filter(MasterService.code == 'SOIL_TESTING').first()
    if not service:
        service = MasterService(
            code='SOIL_TESTING',
            name='Soil Testing',
            description='Professional soil testing and analysis',
            status=ServiceStatus.ACTIVE,
            sort_order=2
        )
        db.add(service)
        db.commit()
        db.refresh(service)
    return service


@pytest.fixture
def active_fsp_org(db: Session, test_user: User, fsp_owner_role: Role) -> Organization:
    """Create an ACTIVE FSP organization for testing."""
    org = Organization(
        name="Active FSP Org",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE,
        description="Active FSP for testing",
        district="Coimbatore",
        created_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create membership
    member = OrgMember(
        user_id=test_user.id,
        organization_id=org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
    # Assign FSP_OWNER role
    member_role = OrgMemberRole(
        user_id=test_user.id,
        organization_id=org.id,
        role_id=fsp_owner_role.id,
        is_primary=True,
        assigned_by=test_user.id
    )
    db.add(member_role)
    db.commit()
    
    return org


@pytest.fixture
def not_started_fsp_org(db: Session, test_user: User, fsp_owner_role: Role) -> Organization:
    """Create a NOT_STARTED FSP organization for testing."""
    org = Organization(
        name="Not Started FSP Org",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.NOT_STARTED,
        description="Not started FSP for testing",
        district="Chennai",
        created_by=test_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create membership
    member = OrgMember(
        user_id=test_user.id,
        organization_id=org.id,
        status=MemberStatus.ACTIVE
    )
    db.add(member)
    db.commit()
    
    # Assign FSP_OWNER role
    member_role = OrgMemberRole(
        user_id=test_user.id,
        organization_id=org.id,
        role_id=fsp_owner_role.id,
        is_primary=True,
        assigned_by=test_user.id
    )
    db.add(member_role)
    db.commit()
    
    return org


@pytest.fixture
def super_admin_user(db: Session, super_admin_role: Role) -> User:
    """Create a SuperAdmin user for testing."""
    from app.core.security import get_password_hash
    
    user = User(
        email="superadmin@example.com",
        password_hash=get_password_hash("SuperAdmin123!"),
        first_name="Super",
        last_name="Admin",
        phone="+919999999999",
        preferred_language="en",
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign SUPER_ADMIN role (system-level, no organization)
    member_role = OrgMemberRole(
        user_id=user.id,
        organization_id=None,  # System-level role
        role_id=super_admin_role.id,
        is_primary=True,
        assigned_by=user.id
    )
    db.add(member_role)
    db.commit()
    
    return user


@pytest.fixture
def super_admin_headers(client: TestClient, super_admin_user: User) -> dict:
    """Get authentication headers for SuperAdmin user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": super_admin_user.email,
            "password": "SuperAdmin123!",
            "remember_me": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    access_token = data["tokens"]["access_token"]
    
    return {"Authorization": f"Bearer {access_token}"}


class TestServiceListingCreation:
    """
    Integration tests for service listing creation.
    
    Requirements: 1.1, 1.7
    """
    
    def test_create_service_listing_success_active_fsp(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test successful service listing creation for ACTIVE FSP organization.
        
        Requirement 1.1: Service listing creation with required fields
        """
        payload = {
            "service_id": str(master_service_consultancy.id),
            "title": "Expert Agricultural Consultancy",
            "description": "Professional consulting for crop management",
            "service_area_districts": ["Coimbatore", "Erode", "Tiruppur"],
            "pricing_model": "PER_HOUR",
            "base_price": 500.00
        }
        
        response = client.post(
            f"/api/v1/fsp-services/organizations/{active_fsp_org.id}/services",
            json=payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert response.status_code == 201
        data = response.json()
        
        assert "id" in data
        assert data["service_id"] == str(master_service_consultancy.id)
        assert data["title"] == "Expert Agricultural Consultancy"
        assert data["description"] == "Professional consulting for crop management"
        assert data["service_area_districts"] == ["Coimbatore", "Erode", "Tiruppur"]
        assert data["pricing_model"] == "PER_HOUR"
        assert float(data["base_price"]) == 500.00
        assert data["status"] == "ACTIVE"
        assert "created_at" in data
        assert "updated_at" in data
        
        # Verify in database
        listing = db.query(FSPServiceListing).filter(
            FSPServiceListing.id == data["id"]
        ).first()
        
        assert listing is not None
        assert listing.fsp_organization_id == active_fsp_org.id
        assert listing.service_id == master_service_consultancy.id
        assert listing.title == "Expert Agricultural Consultancy"
        assert listing.status == ServiceStatus.ACTIVE
    
    def test_create_service_listing_fails_not_started_fsp(
        self,
        client: TestClient,
        auth_headers: dict,
        not_started_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test service listing creation fails for NOT_STARTED FSP organization.
        
        Requirement 1.7: FSP organization status gates service listings
        """
        payload = {
            "service_id": str(master_service_consultancy.id),
            "title": "Test Service",
            "description": "This should fail",
            "service_area_districts": ["Chennai"],
            "pricing_model": "PER_HOUR",
            "base_price": 500.00
        }
        
        response = client.post(
            f"/api/v1/fsp-services/organizations/{not_started_fsp_org.id}/services",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with permission error
        assert response.status_code == 403
        data = response.json()
        
        # Verify error message mentions approval requirement
        error_message = data.get("message", "").lower()
        assert "approve" in error_message or "not_started" in error_message or "active" in error_message
        
        # Verify no listing was created in database
        listing_count = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == not_started_fsp_org.id
        ).count()
        
        assert listing_count == 0
    
    def test_create_service_listing_validation_errors(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService
    ):
        """
        Test service listing creation with validation errors.
        
        Requirement 1.1: Required fields validation
        """
        # Missing required fields
        payload = {
            "service_id": str(master_service_consultancy.id),
            # Missing title
            "description": "Test",
            "pricing_model": "PER_HOUR",
            "base_price": 500.00
        }
        
        response = client.post(
            f"/api/v1/fsp-services/organizations/{active_fsp_org.id}/services",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422


class TestFSPApprovalWorkflow:
    """
    Integration tests for FSP organization approval workflow.
    
    Requirements: 14.4
    """
    
    def test_fsp_approval_workflow_complete(
        self,
        client: TestClient,
        super_admin_headers: dict,
        not_started_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test complete FSP approval workflow from NOT_STARTED to ACTIVE.
        
        Requirement 14.4: SuperAdmin approval workflow
        """
        # Step 1: Verify FSP organization is NOT_STARTED
        org = db.query(Organization).filter(Organization.id == not_started_fsp_org.id).first()
        assert org.status == OrganizationStatus.NOT_STARTED
        
        # Step 2: Get pending approvals (SuperAdmin)
        response = client.get(
            "/api/v1/fsp-services/admin/fsp-approvals",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        
        # Verify our FSP org is in the list
        org_ids = [org["id"] for org in data["items"]]
        assert str(not_started_fsp_org.id) in org_ids
        
        # Step 3: Approve FSP organization (SuperAdmin)
        response = client.post(
            f"/api/v1/fsp-services/admin/fsp-approvals/{not_started_fsp_org.id}/approve",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(not_started_fsp_org.id)
        assert data["status"] == "ACTIVE"
        
        # Step 4: Verify organization status changed in database
        db.refresh(org)
        assert org.status == OrganizationStatus.ACTIVE
        
        # Step 5: Verify FSP can now create service listings
        # (This would be tested in a separate test, but we verify the status change enables it)
        assert org.status == OrganizationStatus.ACTIVE
    
    def test_fsp_approval_requires_super_admin(
        self,
        client: TestClient,
        auth_headers: dict,
        not_started_fsp_org: Organization
    ):
        """
        Test that FSP approval requires SuperAdmin role.
        
        Requirement 14.4: SuperAdmin-only approval
        """
        # Try to approve with regular user (not SuperAdmin)
        response = client.post(
            f"/api/v1/fsp-services/admin/fsp-approvals/{not_started_fsp_org.id}/approve",
            headers=auth_headers
        )
        
        # Should fail with permission error
        assert response.status_code == 403
    
    def test_fsp_rejection_workflow(
        self,
        client: TestClient,
        super_admin_headers: dict,
        not_started_fsp_org: Organization,
        db: Session
    ):
        """
        Test FSP organization rejection workflow.
        
        Requirement 14.4: SuperAdmin can reject FSP
        """
        # Reject FSP organization
        response = client.post(
            f"/api/v1/fsp-services/admin/fsp-approvals/{not_started_fsp_org.id}/reject",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == str(not_started_fsp_org.id)
        assert data["status"] == "NOT_STARTED"
        
        # Verify in database
        org = db.query(Organization).filter(Organization.id == not_started_fsp_org.id).first()
        assert org.status == OrganizationStatus.NOT_STARTED


class TestMarketplaceBrowsing:
    """
    Integration tests for marketplace browsing with filters.
    
    Requirements: 1.1, 1.4, 1.5
    """
    
    def test_browse_marketplace_all_listings(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        master_service_soil_testing: MasterService,
        db: Session
    ):
        """
        Test browsing marketplace without filters.
        
        Requirement 1.4: Display service listings
        """
        # Create multiple service listings
        listing1 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Consultancy Service",
            description="Expert consulting",
            service_area_districts=["Coimbatore", "Erode"],
            pricing_model="PER_HOUR",
            base_price=500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing1)
        
        listing2 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_soil_testing.id,
            title="Soil Testing Service",
            description="Professional soil analysis",
            service_area_districts=["Coimbatore", "Chennai"],
            pricing_model="PER_ACRE",
            base_price=1500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing2)
        db.commit()
        
        # Browse marketplace
        response = client.get(
            "/api/v1/fsp-services/fsp-marketplace/services",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify pagination structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        
        # Verify listings are returned
        items = data["items"]
        assert len(items) >= 2
        
        # Verify listing structure
        for item in items:
            assert "id" in item
            assert "service_id" in item
            assert "title" in item
            assert "description" in item
            assert "service_area_districts" in item
            assert "pricing_model" in item
            assert "base_price" in item
            assert "status" in item
    
    def test_filter_marketplace_by_service_type(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        master_service_soil_testing: MasterService,
        db: Session
    ):
        """
        Test filtering marketplace by service type.
        
        Requirement 1.5: Filter by service type
        """
        # Create listings for different services
        listing1 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Consultancy Service",
            description="Expert consulting",
            service_area_districts=["Coimbatore"],
            pricing_model="PER_HOUR",
            base_price=500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing1)
        
        listing2 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_soil_testing.id,
            title="Soil Testing Service",
            description="Professional soil analysis",
            service_area_districts=["Coimbatore"],
            pricing_model="PER_ACRE",
            base_price=1500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing2)
        db.commit()
        
        # Filter by consultancy service
        response = client.get(
            f"/api/v1/fsp-services/fsp-marketplace/services?service_type={master_service_consultancy.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify only consultancy listings returned
        items = data["items"]
        for item in items:
            assert item["service_id"] == str(master_service_consultancy.id)
    
    def test_filter_marketplace_by_district(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test filtering marketplace by district.
        
        Requirement 1.5: Filter by district
        """
        # Create listings with different service areas
        listing1 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Coimbatore Service",
            description="Service in Coimbatore",
            service_area_districts=["Coimbatore", "Erode"],
            pricing_model="PER_HOUR",
            base_price=500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing1)
        
        listing2 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Chennai Service",
            description="Service in Chennai",
            service_area_districts=["Chennai", "Kanchipuram"],
            pricing_model="PER_HOUR",
            base_price=600.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing2)
        db.commit()
        
        # Filter by Coimbatore district
        response = client.get(
            "/api/v1/fsp-services/fsp-marketplace/services?district=Coimbatore",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify only Coimbatore listings returned
        items = data["items"]
        for item in items:
            assert "Coimbatore" in item["service_area_districts"]
    
    def test_filter_marketplace_by_pricing_model(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test filtering marketplace by pricing model.
        
        Requirement 1.5: Filter by pricing model
        """
        # Create listings with different pricing models
        listing1 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Hourly Service",
            description="Charged per hour",
            service_area_districts=["Coimbatore"],
            pricing_model="PER_HOUR",
            base_price=500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing1)
        
        listing2 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Per Acre Service",
            description="Charged per acre",
            service_area_districts=["Coimbatore"],
            pricing_model="PER_ACRE",
            base_price=1500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing2)
        db.commit()
        
        # Filter by PER_HOUR pricing model
        response = client.get(
            "/api/v1/fsp-services/fsp-marketplace/services?pricing_model=PER_HOUR",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify only PER_HOUR listings returned
        items = data["items"]
        for item in items:
            assert item["pricing_model"] == "PER_HOUR"
    
    def test_filter_marketplace_combined_filters(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        master_service_soil_testing: MasterService,
        db: Session
    ):
        """
        Test filtering marketplace with multiple filters combined.
        
        Requirement 1.5: Combined filtering
        """
        # Create diverse listings
        listing1 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Coimbatore Hourly Consultancy",
            description="Consultancy in Coimbatore, charged per hour",
            service_area_districts=["Coimbatore", "Erode"],
            pricing_model="PER_HOUR",
            base_price=500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing1)
        
        listing2 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Chennai Hourly Consultancy",
            description="Consultancy in Chennai, charged per hour",
            service_area_districts=["Chennai"],
            pricing_model="PER_HOUR",
            base_price=600.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing2)
        
        listing3 = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_soil_testing.id,
            title="Coimbatore Soil Testing",
            description="Soil testing in Coimbatore, charged per acre",
            service_area_districts=["Coimbatore"],
            pricing_model="PER_ACRE",
            base_price=1500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(listing3)
        db.commit()
        
        # Filter by service type + district + pricing model
        response = client.get(
            f"/api/v1/fsp-services/fsp-marketplace/services?service_type={master_service_consultancy.id}&district=Coimbatore&pricing_model=PER_HOUR",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only return listing1
        items = data["items"]
        assert len(items) >= 1
        
        # Verify all filters applied
        for item in items:
            assert item["service_id"] == str(master_service_consultancy.id)
            assert "Coimbatore" in item["service_area_districts"]
            assert item["pricing_model"] == "PER_HOUR"
    
    def test_marketplace_pagination(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test marketplace pagination.
        
        Requirement 1.4: Pagination support
        """
        # Create multiple listings
        for i in range(5):
            listing = FSPServiceListing(
                fsp_organization_id=active_fsp_org.id,
                service_id=master_service_consultancy.id,
                title=f"Service {i}",
                description=f"Description {i}",
                service_area_districts=["Coimbatore"],
                pricing_model="PER_HOUR",
                base_price=500.00 + i * 100,
                status=ServiceStatus.ACTIVE,
                created_by=active_fsp_org.created_by
            )
            db.add(listing)
        db.commit()
        
        # Get first page with limit 2
        response = client.get(
            "/api/v1/fsp-services/fsp-marketplace/services?page=1&limit=2",
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
        
        # Verify pagination values
        assert data["page"] == 1
        assert data["limit"] == 2
        assert len(data["items"]) <= 2
        assert data["total"] >= 5
    
    def test_marketplace_only_shows_active_fsp_listings(
        self,
        client: TestClient,
        auth_headers: dict,
        active_fsp_org: Organization,
        not_started_fsp_org: Organization,
        master_service_consultancy: MasterService,
        db: Session
    ):
        """
        Test that marketplace only shows listings from ACTIVE FSP organizations.
        
        Requirement 1.7: Only ACTIVE FSP organizations visible in marketplace
        """
        # Create listing for ACTIVE FSP
        active_listing = FSPServiceListing(
            fsp_organization_id=active_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Active FSP Service",
            description="From active FSP",
            service_area_districts=["Coimbatore"],
            pricing_model="PER_HOUR",
            base_price=500.00,
            status=ServiceStatus.ACTIVE,
            created_by=active_fsp_org.created_by
        )
        db.add(active_listing)
        
        # Create listing for NOT_STARTED FSP (should not appear in marketplace)
        not_started_listing = FSPServiceListing(
            fsp_organization_id=not_started_fsp_org.id,
            service_id=master_service_consultancy.id,
            title="Not Started FSP Service",
            description="From not started FSP",
            service_area_districts=["Chennai"],
            pricing_model="PER_HOUR",
            base_price=600.00,
            status=ServiceStatus.ACTIVE,
            created_by=not_started_fsp_org.created_by
        )
        db.add(not_started_listing)
        db.commit()
        
        # Browse marketplace
        response = client.get(
            "/api/v1/fsp-services/fsp-marketplace/services",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify only ACTIVE FSP listings returned
        items = data["items"]
        listing_ids = [item["id"] for item in items]
        
        # Active FSP listing should be present
        assert str(active_listing.id) in listing_ids
        
        # NOT_STARTED FSP listing should NOT be present
        assert str(not_started_listing.id) not in listing_ids
