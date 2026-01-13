"""
End-to-End tests for Organization Creation Flow.

Task 12.1: Test organization creation flow (FARMING)
- Create FARMING organization
- Verify organization created in database
- Verify owner membership created
- Verify owner role assigned
- Verify status is ACTIVE

Task 12.2: Test organization creation flow (FSP with services)
- Create FSP organization with services
- Verify organization created with status NOT_STARTED
- Verify service listings created
- Verify owner membership created
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.rbac import Role
from app.models.subscription import SubscriptionPlan
from app.models.fsp_service import MasterService, FSPServiceListing
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    UserRoleScope,
    ServiceStatus
)


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
def master_service(db: Session) -> MasterService:
    """Get or create a master service for testing FSP organizations."""
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


class TestE2EOrganizationCreationFarming:
    """
    End-to-end test for FARMING organization creation flow.
    
    This test verifies the complete flow from API request to database state,
    ensuring all components work together correctly.
    """
    
    def test_farming_organization_creation_complete_flow(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """
        Test complete FARMING organization creation flow.
        
        Requirements: FR1.1
        
        Steps:
        1. Create FARMING organization via API
        2. Verify organization created in database with correct attributes
        3. Verify owner membership created
        4. Verify owner role assigned
        5. Verify status is ACTIVE
        6. Verify subscription assigned
        """
        # Step 1: Create FARMING organization via API
        payload = {
            "name": "E2E Test Farm",
            "organization_type": "FARMING",
            "description": "End-to-end test farming organization",
            "district": "Coimbatore",
            "pincode": "641001",
            "contact_email": "e2e@testfarm.com",
            "contact_phone": "+919876543210"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        response_data = response.json()
        
        assert "id" in response_data
        assert response_data["name"] == "E2E Test Farm"
        assert response_data["organization_type"] == "FARMING"
        assert response_data["status"] == "ACTIVE"
        assert response_data["description"] == "End-to-end test farming organization"
        assert response_data["district"] == "Coimbatore"
        assert response_data["pincode"] == "641001"
        assert response_data["contact_email"] == "e2e@testfarm.com"
        assert response_data["contact_phone"] == "+919876543210"
        
        org_id = response_data["id"]
        
        # Step 2: Verify organization created in database with correct attributes
        org = db.query(Organization).filter(Organization.id == org_id).first()
        
        assert org is not None, "Organization not found in database"
        assert org.name == "E2E Test Farm"
        assert org.organization_type == OrganizationType.FARMING
        assert org.status == OrganizationStatus.ACTIVE, f"Expected ACTIVE status, got {org.status}"
        assert org.description == "End-to-end test farming organization"
        assert org.district == "Coimbatore"
        assert org.pincode == "641001"
        assert org.contact_email == "e2e@testfarm.com"
        assert org.contact_phone == "+919876543210"
        assert org.created_by == test_user.id
        assert org.created_at is not None
        assert org.updated_at is not None
        
        # Step 3: Verify owner membership created
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == test_user.id
        ).first()
        
        assert member is not None, "Owner membership not found in database"
        assert member.status == MemberStatus.ACTIVE, f"Expected ACTIVE member status, got {member.status}"
        assert member.joined_at is not None
        assert member.left_at is None
        assert member.created_at is not None
        
        # Step 4: Verify owner role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == test_user.id
        ).first()
        
        assert member_role is not None, "Owner role assignment not found in database"
        assert member_role.role_id == owner_role.id, "Incorrect role assigned"
        assert member_role.is_primary is True, "Owner role should be marked as primary"
        assert member_role.assigned_at is not None
        assert member_role.assigned_by == test_user.id
        assert member_role.created_at is not None
        
        # Verify the role is actually OWNER
        role = db.query(Role).filter(Role.id == member_role.role_id).first()
        assert role is not None
        assert role.code == 'OWNER'
        assert role.name == 'OWNER'  # Role name matches code in database
        assert role.scope == UserRoleScope.ORGANIZATION
        
        # Step 5: Verify status is ACTIVE (already verified in step 2, but explicit check)
        assert org.status == OrganizationStatus.ACTIVE, \
            "FARMING organization should have ACTIVE status immediately after creation"
        
        # Step 6: Verify subscription assigned
        assert org.subscription_plan_id is not None, "Subscription plan not assigned"
        assert org.subscription_start_date is not None, "Subscription start date not set"
        assert org.subscription_end_date is not None, "Subscription end date not set"
        
        # Verify subscription plan exists
        subscription_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == org.subscription_plan_id
        ).first()
        assert subscription_plan is not None, "Subscription plan not found in database"
        assert subscription_plan.is_active is True
        
        # Additional verification: Check that subscription dates are logical
        assert org.subscription_end_date > org.subscription_start_date, \
            "Subscription end date should be after start date"
    
    def test_farming_organization_creation_minimal_data(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """
        Test FARMING organization creation with minimal required data.
        
        Requirements: FR1.1
        
        Verifies that organization can be created with only required fields
        and all necessary relationships are still established.
        """
        # Create organization with minimal data
        payload = {
            "name": "Minimal Farm",
            "organization_type": "FARMING"
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["name"] == "Minimal Farm"
        assert response_data["organization_type"] == "FARMING"
        assert response_data["status"] == "ACTIVE"
        assert response_data["description"] is None
        assert response_data["district"] is None
        
        org_id = response_data["id"]
        
        # Verify organization in database
        org = db.query(Organization).filter(Organization.id == org_id).first()
        assert org is not None
        assert org.status == OrganizationStatus.ACTIVE
        
        # Verify owner membership created
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        # Verify owner role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == test_user.id,
            OrgMemberRole.role_id == owner_role.id
        ).first()
        assert member_role is not None
        assert member_role.is_primary is True
    
    def test_farming_organization_user_can_access_after_creation(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """
        Test that user can immediately access organization after creation.
        
        Requirements: FR1.1, FR1.2, FR1.3
        
        Verifies that:
        1. Organization appears in user's organization list
        2. User can retrieve organization details
        3. User has proper permissions as owner
        """
        # Create organization
        payload = {
            "name": "Accessible Farm",
            "organization_type": "FARMING",
            "description": "Test accessibility"
        }
        
        create_response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        org_id = create_response.json()["id"]
        
        # Verify organization appears in user's list
        list_response = client.get(
            "/api/v1/organizations",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        organizations = list_response.json()
        
        org_ids = [org["id"] for org in organizations]
        assert org_id in org_ids, "Created organization not found in user's organization list"
        
        # Find the created organization in the list
        created_org = next((org for org in organizations if org["id"] == org_id), None)
        assert created_org is not None
        assert created_org["name"] == "Accessible Farm"
        assert created_org["organization_type"] == "FARMING"
        assert created_org["status"] == "ACTIVE"
        
        # Verify user can retrieve organization details
        detail_response = client.get(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers
        )
        
        assert detail_response.status_code == 200
        org_details = detail_response.json()
        
        assert org_details["id"] == org_id
        assert org_details["name"] == "Accessible Farm"
        assert org_details["description"] == "Test accessibility"
        
        # Verify database state matches
        org = db.query(Organization).filter(Organization.id == org_id).first()
        assert org is not None
        assert org.status == OrganizationStatus.ACTIVE
        
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
    
    def test_farming_organization_creation_idempotency(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        owner_role: Role,
        db: Session
    ):
        """
        Test that duplicate organization names are properly rejected.
        
        Requirements: FR1.1 (validation)
        
        Verifies that business rule preventing duplicate organization names
        per user is enforced.
        """
        # Create first organization
        payload = {
            "name": "Unique Farm Name",
            "organization_type": "FARMING"
        }
        
        first_response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        assert first_response.status_code == 201
        first_org_id = first_response.json()["id"]
        
        # Try to create second organization with same name
        second_response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with conflict error
        assert second_response.status_code == 409
        error_data = second_response.json()
        assert "detail" in error_data or "message" in error_data
        
        # Verify only one organization with this name exists for this user
        # Query directly using test_user.id to avoid detached instance issues
        orgs_count = db.query(Organization).join(OrgMember).filter(
            Organization.name == "Unique Farm Name",
            OrgMember.user_id == test_user.id
        ).count()
        
        assert orgs_count == 1, f"Should only have one organization with this name, found {orgs_count}"



class TestE2EOrganizationCreationFSP:
    """
    End-to-end test for FSP organization creation flow with services.
    
    This test verifies the complete flow for creating FSP organizations
    including service listings and approval workflow.
    """
    
    def test_fsp_organization_creation_with_services_complete_flow(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        fsp_owner_role: Role,
        master_service: MasterService,
        db: Session
    ):
        """
        Test complete FSP organization creation flow with services.
        
        Requirements: FR1.1, FR1.6.2
        
        Steps:
        1. Create FSP organization with services via API
        2. Verify organization created with status NOT_STARTED (pending approval)
        3. Verify service listings created
        4. Verify owner membership created
        5. Verify FSP_OWNER role assigned
        6. Verify subscription assigned
        """
        # Step 1: Create FSP organization with services via API
        payload = {
            "name": "E2E Test FSP",
            "organization_type": "FSP",
            "description": "End-to-end test FSP organization",
            "district": "Coimbatore",
            "pincode": "641001",
            "contact_email": "e2e@testfsp.com",
            "contact_phone": "+919876543210",
            "services": [
                {
                    "service_id": str(master_service.id),
                    "title": "Expert Agricultural Consultancy",
                    "description": "Professional consulting for crop management and farm optimization",
                    "service_area_districts": ["Coimbatore", "Erode", "Tiruppur"],
                    "pricing_model": "PER_HOUR",
                    "base_price": 500.00
                }
            ]
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        response_data = response.json()
        
        assert "id" in response_data
        assert response_data["name"] == "E2E Test FSP"
        assert response_data["organization_type"] == "FSP"
        assert response_data["status"] == "NOT_STARTED", \
            f"FSP organization should have NOT_STARTED status, got {response_data['status']}"
        assert response_data["description"] == "End-to-end test FSP organization"
        assert response_data["district"] == "Coimbatore"
        assert response_data["pincode"] == "641001"
        assert response_data["contact_email"] == "e2e@testfsp.com"
        assert response_data["contact_phone"] == "+919876543210"
        
        org_id = response_data["id"]
        
        # Step 2: Verify organization created in database with status NOT_STARTED
        org = db.query(Organization).filter(Organization.id == org_id).first()
        
        assert org is not None, "Organization not found in database"
        assert org.name == "E2E Test FSP"
        assert org.organization_type == OrganizationType.FSP
        assert org.status == OrganizationStatus.NOT_STARTED, \
            f"Expected NOT_STARTED status for FSP with services, got {org.status}"
        assert org.description == "End-to-end test FSP organization"
        assert org.district == "Coimbatore"
        assert org.pincode == "641001"
        assert org.contact_email == "e2e@testfsp.com"
        assert org.contact_phone == "+919876543210"
        assert org.created_by == test_user.id
        assert org.created_at is not None
        assert org.updated_at is not None
        
        # Step 3: Verify service listings created
        service_listings = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == org_id
        ).all()
        
        assert len(service_listings) == 1, f"Expected 1 service listing, found {len(service_listings)}"
        
        service_listing = service_listings[0]
        assert service_listing.service_id == master_service.id
        assert service_listing.title == "Expert Agricultural Consultancy"
        assert service_listing.description == "Professional consulting for crop management and farm optimization"
        assert service_listing.service_area_districts == ["Coimbatore", "Erode", "Tiruppur"]
        assert service_listing.pricing_model == "PER_HOUR"
        assert float(service_listing.base_price) == 500.00
        assert service_listing.currency == "INR"
        assert service_listing.status == ServiceStatus.ACTIVE
        assert service_listing.created_by == test_user.id
        assert service_listing.created_at is not None
        assert service_listing.updated_at is not None
        
        # Step 4: Verify owner membership created
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == test_user.id
        ).first()
        
        assert member is not None, "Owner membership not found in database"
        assert member.status == MemberStatus.ACTIVE, f"Expected ACTIVE member status, got {member.status}"
        assert member.joined_at is not None
        assert member.left_at is None
        assert member.created_at is not None
        
        # Step 5: Verify FSP_OWNER role assigned
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == test_user.id
        ).first()
        
        assert member_role is not None, "FSP_OWNER role assignment not found in database"
        assert member_role.role_id == fsp_owner_role.id, "Incorrect role assigned"
        assert member_role.is_primary is True, "FSP_OWNER role should be marked as primary"
        assert member_role.assigned_at is not None
        assert member_role.assigned_by == test_user.id
        assert member_role.created_at is not None
        
        # Verify the role is actually FSP_OWNER
        role = db.query(Role).filter(Role.id == member_role.role_id).first()
        assert role is not None
        assert role.code == 'FSP_OWNER'
        assert role.name == 'FSP_OWNER'
        assert role.scope == UserRoleScope.ORGANIZATION
        
        # Step 6: Verify subscription assigned
        assert org.subscription_plan_id is not None, "Subscription plan not assigned"
        assert org.subscription_start_date is not None, "Subscription start date not set"
        assert org.subscription_end_date is not None, "Subscription end date not set"
        
        # Verify subscription plan exists
        subscription_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == org.subscription_plan_id
        ).first()
        assert subscription_plan is not None, "Subscription plan not found in database"
        assert subscription_plan.is_active is True
        
        # Additional verification: Check that subscription dates are logical
        assert org.subscription_end_date > org.subscription_start_date, \
            "Subscription end date should be after start date"
    
    def test_fsp_organization_creation_with_multiple_services(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        fsp_owner_role: Role,
        master_service: MasterService,
        db: Session
    ):
        """
        Test FSP organization creation with multiple services.
        
        Requirements: FR1.1, FR1.6.2
        
        Verifies that FSP can offer multiple services at creation time.
        """
        # Create a second master service for testing
        second_service = db.query(MasterService).filter(
            MasterService.code == 'SOIL_TESTING'
        ).first()
        if not second_service:
            second_service = MasterService(
                code='SOIL_TESTING',
                name='Soil Testing Services',
                description='Professional soil analysis and testing',
                status=ServiceStatus.ACTIVE,
                sort_order=2
            )
            db.add(second_service)
            db.commit()
            db.refresh(second_service)
        
        # Create FSP organization with multiple services
        payload = {
            "name": "Multi-Service FSP",
            "organization_type": "FSP",
            "description": "FSP offering multiple services",
            "district": "Erode",
            "pincode": "638001",
            "services": [
                {
                    "service_id": str(master_service.id),
                    "title": "Agricultural Consultancy",
                    "description": "Expert consulting services",
                    "service_area_districts": ["Erode", "Salem"],
                    "pricing_model": "PER_HOUR",
                    "base_price": 600.00
                },
                {
                    "service_id": str(second_service.id),
                    "title": "Comprehensive Soil Testing",
                    "description": "Detailed soil analysis and recommendations",
                    "service_area_districts": ["Erode", "Salem", "Namakkal"],
                    "pricing_model": "PER_ACRE",
                    "base_price": 1500.00
                }
            ]
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Verify API response
        assert response.status_code == 201
        response_data = response.json()
        
        assert response_data["name"] == "Multi-Service FSP"
        assert response_data["organization_type"] == "FSP"
        assert response_data["status"] == "NOT_STARTED"
        
        org_id = response_data["id"]
        
        # Verify organization in database
        org = db.query(Organization).filter(Organization.id == org_id).first()
        assert org is not None
        assert org.status == OrganizationStatus.NOT_STARTED
        
        # Verify both service listings created
        service_listings = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == org_id
        ).all()
        
        assert len(service_listings) == 2, f"Expected 2 service listings, found {len(service_listings)}"
        
        # Verify first service
        consultancy_listing = next(
            (sl for sl in service_listings if sl.service_id == master_service.id),
            None
        )
        assert consultancy_listing is not None
        assert consultancy_listing.title == "Agricultural Consultancy"
        assert float(consultancy_listing.base_price) == 600.00
        assert consultancy_listing.pricing_model == "PER_HOUR"
        
        # Verify second service
        soil_testing_listing = next(
            (sl for sl in service_listings if sl.service_id == second_service.id),
            None
        )
        assert soil_testing_listing is not None
        assert soil_testing_listing.title == "Comprehensive Soil Testing"
        assert float(soil_testing_listing.base_price) == 1500.00
        assert soil_testing_listing.pricing_model == "PER_ACRE"
        
        # Verify owner membership and role
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        member_role = db.query(OrgMemberRole).filter(
            OrgMemberRole.organization_id == org_id,
            OrgMemberRole.user_id == test_user.id,
            OrgMemberRole.role_id == fsp_owner_role.id
        ).first()
        assert member_role is not None
        assert member_role.is_primary is True
    
    def test_fsp_organization_validation_requires_services(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        db: Session
    ):
        """
        Test that FSP organization creation requires at least one service.
        
        Requirements: FR1.1 (validation)
        
        Verifies that business rule requiring FSP organizations to offer
        at least one service is enforced.
        """
        # Try to create FSP organization without services
        payload = {
            "name": "FSP Without Services",
            "organization_type": "FSP",
            "description": "This should fail validation",
            "district": "Coimbatore",
            "services": []  # Empty services list
        }
        
        response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        # Should fail with validation error
        assert response.status_code == 422, \
            f"Expected 422 validation error, got {response.status_code}"
        
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data
        
        # Verify no organization was created
        orgs_count = db.query(Organization).filter(
            Organization.name == "FSP Without Services"
        ).count()
        assert orgs_count == 0, "Organization should not have been created"
    
    def test_fsp_organization_user_can_access_after_creation(
        self,
        client: TestClient,
        auth_headers: dict,
        test_user: User,
        fsp_owner_role: Role,
        master_service: MasterService,
        db: Session
    ):
        """
        Test that user can immediately access FSP organization after creation.
        
        Requirements: FR1.1, FR1.2, FR1.3
        
        Verifies that:
        1. FSP organization appears in user's organization list
        2. User can retrieve organization details
        3. User has proper permissions as FSP_OWNER
        """
        # Create FSP organization
        payload = {
            "name": "Accessible FSP",
            "organization_type": "FSP",
            "description": "Test FSP accessibility",
            "district": "Coimbatore",
            "services": [
                {
                    "service_id": str(master_service.id),
                    "title": "Test Service",
                    "description": "Test service description",
                    "service_area_districts": ["Coimbatore"],
                    "pricing_model": "FIXED",
                    "base_price": 1000.00
                }
            ]
        }
        
        create_response = client.post(
            "/api/v1/organizations",
            json=payload,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        org_id = create_response.json()["id"]
        
        # Verify organization appears in user's list
        list_response = client.get(
            "/api/v1/organizations",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        organizations = list_response.json()
        
        org_ids = [org["id"] for org in organizations]
        assert org_id in org_ids, "Created FSP organization not found in user's organization list"
        
        # Find the created organization in the list
        created_org = next((org for org in organizations if org["id"] == org_id), None)
        assert created_org is not None
        assert created_org["name"] == "Accessible FSP"
        assert created_org["organization_type"] == "FSP"
        assert created_org["status"] == "NOT_STARTED"
        
        # Verify user can retrieve organization details
        detail_response = client.get(
            f"/api/v1/organizations/{org_id}",
            headers=auth_headers
        )
        
        assert detail_response.status_code == 200
        org_details = detail_response.json()
        
        assert org_details["id"] == org_id
        assert org_details["name"] == "Accessible FSP"
        assert org_details["description"] == "Test FSP accessibility"
        assert org_details["status"] == "NOT_STARTED"
        
        # Verify database state matches
        org = db.query(Organization).filter(Organization.id == org_id).first()
        assert org is not None
        assert org.status == OrganizationStatus.NOT_STARTED
        
        member = db.query(OrgMember).filter(
            OrgMember.organization_id == org_id,
            OrgMember.user_id == test_user.id
        ).first()
        assert member is not None
        assert member.status == MemberStatus.ACTIVE
        
        # Verify service listing exists
        service_listing = db.query(FSPServiceListing).filter(
            FSPServiceListing.fsp_organization_id == org_id
        ).first()
        assert service_listing is not None
        assert service_listing.title == "Test Service"
