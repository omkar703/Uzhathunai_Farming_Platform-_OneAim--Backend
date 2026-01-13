"""
Integration tests for BFF Dashboard endpoints.

Tests cover:
- GET /api/v1/bff/farming/dashboard
- GET /api/v1/bff/fsp/dashboard
- GET /api/v1/notifications/unread-count
- Permission validation
- Data aggregation accuracy

Requirements: 3.1, 3.2, 1.3
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.user import User
from app.models.organization import Organization, OrgMember, OrgMemberRole
from app.models.farm import Farm
from app.models.plot import Plot
from app.models.crop import Crop
from app.models.schedule import Schedule, ScheduleTask
from app.models.work_order import WorkOrder
from app.models.query import Query
from app.models.audit import Audit
from app.models.rbac import Role
from app.models.measurement_unit import MeasurementUnit
from app.models.enums import (
    OrganizationType,
    OrganizationStatus,
    MemberStatus,
    CropLifecycle,
    WorkOrderStatus,
    QueryStatus,
    AuditStatus,
    TaskStatus,
    UserRoleScope,
    MeasurementUnitCategory
)


@pytest.fixture
def farming_org(db: Session, test_user: User) -> Organization:
    """Create a test farming organization."""
    org = Organization(
        name="Test Farming Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id
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
def fsp_org(db: Session, test_user: User) -> Organization:
    """Create a test FSP organization."""
    org = Organization(
        name="Test FSP Org",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE,
        created_by=test_user.id
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
def area_unit(db: Session) -> MeasurementUnit:
    """Get or create area measurement unit."""
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


class TestFarmingDashboard:
    """Tests for GET /api/v1/bff/farming/dashboard."""
    
    def test_farming_dashboard_empty_organization(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization
    ):
        """Test farming dashboard with no data."""
        # Requirement 3.1: Dashboard displays quick stats
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "stats" in data
        assert "actionRequired" in data
        assert "recentActivity" in data
        
        # Verify empty stats
        stats = data["stats"]
        assert stats["farms"] == 0
        assert stats["activeCrops"] == 0
        assert stats["activeSchedules"] == 0
        assert stats["activeServices"] == 0
        assert stats["openIssues"] == 0
        assert stats["activeUsers"] == 1  # Test user is a member
        
        # Verify empty action items
        action_required = data["actionRequired"]
        assert len(action_required["pendingRecommendations"]) == 0
        assert len(action_required["unansweredQueries"]) == 0
        assert len(action_required["pendingWorkOrders"]) == 0
        assert len(action_required["unresolvedIssues"]) == 0
        assert len(action_required["overdueTasks"]) == 0
        
        # Verify empty activity
        assert len(data["recentActivity"]) == 0
    
    def test_farming_dashboard_with_farms(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        area_unit: MeasurementUnit,
        db: Session
    ):
        """Test farming dashboard counts farms correctly."""
        # Requirement 3.1: Dashboard displays farm count
        # Create test farms
        for i in range(3):
            farm = Farm(
                name=f"Test Farm {i+1}",
                organization_id=farming_org.id,
                location=f'SRID=4326;POINT({77.5946 + i*0.01} {12.9716 + i*0.01})',
                area=Decimal("10.5"),
                area_unit_id=area_unit.id,
                created_by=farming_org.created_by
            )
            db.add(farm)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify farm count
        assert data["stats"]["farms"] == 3
    
    def test_farming_dashboard_with_active_crops(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        area_unit: MeasurementUnit,
        db: Session
    ):
        """Test farming dashboard counts active crops correctly."""
        # Requirement 3.1: Dashboard displays active crop count
        # Create farm and plot
        farm = Farm(
            name="Test Farm",
            organization_id=farming_org.id,
            location='SRID=4326;POINT(77.5946 12.9716)',
            area=Decimal("10.5"),
            area_unit_id=area_unit.id,
            created_by=farming_org.created_by
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        plot = Plot(
            name="Test Plot",
            farm_id=farm.id,
            boundary='SRID=4326;POLYGON((77.5946 12.9716, 77.5956 12.9716, 77.5956 12.9726, 77.5946 12.9726, 77.5946 12.9716))',
            area=Decimal("5.0"),
            area_unit_id=area_unit.id,
            created_by=farming_org.created_by
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)
        
        # Create active crops
        for i in range(2):
            crop = Crop(
                plot_id=plot.id,
                name=f"Test Crop {i+1}",
                lifecycle=CropLifecycle.PRODUCTION,
                created_by=farming_org.created_by
            )
            db.add(crop)
        
        # Create completed crop (should not be counted)
        completed_crop = Crop(
            plot_id=plot.id,
            name="Completed Crop",
            lifecycle=CropLifecycle.COMPLETED,
            created_by=farming_org.created_by
        )
        db.add(completed_crop)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify active crop count (should not include completed)
        assert data["stats"]["activeCrops"] == 2
    
    def test_farming_dashboard_with_work_orders(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        fsp_org: Organization,
        db: Session
    ):
        """Test farming dashboard counts active work orders."""
        # Requirement 3.2: Dashboard displays active services count
        # Create work orders
        for status in [WorkOrderStatus.PENDING, WorkOrderStatus.ACCEPTED, WorkOrderStatus.ACTIVE]:
            wo = WorkOrder(
                farming_organization_id=farming_org.id,
                fsp_organization_id=fsp_org.id,
                title=f"Work Order {status.value}",
                status=status,
                created_by=farming_org.created_by
            )
            db.add(wo)
        
        # Create cancelled work order (should not be counted)
        cancelled_wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Cancelled Work Order",
            status=WorkOrderStatus.CANCELLED,
            created_by=farming_org.created_by
        )
        db.add(cancelled_wo)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify active work order count
        assert data["stats"]["activeServices"] == 3
    
    def test_farming_dashboard_with_queries(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        fsp_org: Organization,
        db: Session
    ):
        """Test farming dashboard counts open queries."""
        # Requirement 3.3: Dashboard displays open issues count
        # Create a work order first (required for queries)
        wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Test Work Order",
            created_by=farming_org.created_by
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)
        
        # Create open queries
        for i in range(2):
            query = Query(
                farming_organization_id=farming_org.id,
                fsp_organization_id=fsp_org.id,
                work_order_id=wo.id,
                title=f"Test Query {i+1}",
                description=f"Description for query {i+1}",
                status=QueryStatus.OPEN,
                created_by=farming_org.created_by
            )
            db.add(query)
        
        # Create closed query (should not be counted)
        closed_query = Query(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            work_order_id=wo.id,
            title="Closed Query",
            description="Closed query description",
            status=QueryStatus.CLOSED,
            created_by=farming_org.created_by
        )
        db.add(closed_query)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify open query count
        assert data["stats"]["openIssues"] == 2
    
    def test_farming_dashboard_action_required_items(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        fsp_org: Organization,
        db: Session
    ):
        """Test farming dashboard returns action required items."""
        # Requirement 3.4: Dashboard displays action required section
        # Create pending work order
        wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Pending Work Order",
            status=WorkOrderStatus.PENDING,
            created_by=farming_org.created_by
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)
        
        # Create unanswered query
        query = Query(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            work_order_id=wo.id,
            title="Unanswered Query",
            description="Query description",
            status=QueryStatus.OPEN,
            created_by=farming_org.created_by
        )
        db.add(query)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify action required items
        action_required = data["actionRequired"]
        assert len(action_required["pendingWorkOrders"]) > 0
        assert len(action_required["unansweredQueries"]) > 0
        
        # Verify item structure
        work_order_item = action_required["pendingWorkOrders"][0]
        assert "id" in work_order_item
        assert "type" in work_order_item
        assert "title" in work_order_item
        assert "urgency" in work_order_item
        assert "timestamp" in work_order_item
    
    def test_farming_dashboard_recent_activity(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        area_unit: MeasurementUnit,
        db: Session
    ):
        """Test farming dashboard returns recent activity."""
        # Requirement 3.5: Dashboard displays recent activity feed
        # Create farm
        farm = Farm(
            name="Recent Farm",
            organization_id=farming_org.id,
            location='SRID=4326;POINT(77.5946 12.9716)',
            area=Decimal("10.5"),
            area_unit_id=area_unit.id,
            created_by=farming_org.created_by
        )
        db.add(farm)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify recent activity
        recent_activity = data["recentActivity"]
        assert len(recent_activity) > 0
        
        # Verify activity structure
        activity = recent_activity[0]
        assert "id" in activity
        assert "icon" in activity
        assert "description" in activity
        assert "timestamp" in activity
    
    def test_farming_dashboard_unauthorized(
        self,
        client: TestClient
    ):
        """Test farming dashboard requires authentication."""
        response = client.get("/api/v1/bff/farming/dashboard")
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]
    
    def test_farming_dashboard_permission_validation(
        self,
        client: TestClient,
        db: Session
    ):
        """Test farming dashboard validates organization membership."""
        # Create user not in any organization
        from app.core.security import get_password_hash
        other_user = User(
            email="other@example.com",
            password_hash=get_password_hash("TestPass123!"),
            first_name="Other",
            last_name="User",
            phone="+919999999999",
            preferred_language="en",
            is_active=True
        )
        db.add(other_user)
        db.commit()
        
        # Login as other user
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "other@example.com",
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["tokens"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=headers
        )
        
        # Should return empty dashboard for user with no organizations
        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["farms"] == 0


class TestFSPDashboard:
    """Tests for GET /api/v1/bff/fsp/dashboard."""
    
    def test_fsp_dashboard_empty_organization(
        self,
        client: TestClient,
        auth_headers: dict,
        fsp_org: Organization
    ):
        """Test FSP dashboard with no data."""
        # Requirement 3.1: Dashboard displays quick stats
        response = client.get(
            "/api/v1/bff/fsp/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "stats" in data
        assert "actionRequired" in data
        assert "recentActivity" in data
        
        # Verify empty stats
        stats = data["stats"]
        assert stats["activeClients"] == 0
        assert stats["activeOrders"] == 0
        assert stats["auditsInProgress"] == 0
        assert stats["pendingRecommendations"] == 0
        assert stats["pendingQueries"] == 0
        assert stats["activeTeam"] == 1  # Test user is a member
    
    def test_fsp_dashboard_with_clients(
        self,
        client: TestClient,
        auth_headers: dict,
        fsp_org: Organization,
        db: Session,
        test_user: User
    ):
        """Test FSP dashboard counts unique clients."""
        # Requirement 3.1: Dashboard displays client count
        # Create client organizations
        client_org1 = Organization(
            name="Client Org 1",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(client_org1)
        
        client_org2 = Organization(
            name="Client Org 2",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(client_org2)
        db.commit()
        
        # Create work orders with different clients
        wo1 = WorkOrder(
            farming_organization_id=client_org1.id,
            fsp_organization_id=fsp_org.id,
            title="Work Order 1",
            status=WorkOrderStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(wo1)
        
        wo2 = WorkOrder(
            farming_organization_id=client_org2.id,
            fsp_organization_id=fsp_org.id,
            title="Work Order 2",
            status=WorkOrderStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(wo2)
        
        # Another work order with same client (should not increase count)
        wo3 = WorkOrder(
            farming_organization_id=client_org1.id,
            fsp_organization_id=fsp_org.id,
            title="Work Order 3",
            status=WorkOrderStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(wo3)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/fsp/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify unique client count
        assert data["stats"]["activeClients"] == 2
    
    def test_fsp_dashboard_with_work_orders(
        self,
        client: TestClient,
        auth_headers: dict,
        fsp_org: Organization,
        db: Session,
        test_user: User
    ):
        """Test FSP dashboard counts active work orders."""
        # Requirement 3.2: Dashboard displays active orders count
        # Create client organization
        client_org = Organization(
            name="Client Org",
            organization_type=OrganizationType.FARMING,
            status=OrganizationStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(client_org)
        db.commit()
        
        # Create active work orders
        for status in [WorkOrderStatus.PENDING, WorkOrderStatus.ACCEPTED]:
            wo = WorkOrder(
                farming_organization_id=client_org.id,
                fsp_organization_id=fsp_org.id,
                title=f"Work Order {status.value}",
                status=status,
                created_by=test_user.id
            )
            db.add(wo)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/fsp/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify active work order count
        assert data["stats"]["activeOrders"] == 2
    
    def test_fsp_dashboard_with_audits(
        self,
        client: TestClient,
        auth_headers: dict,
        fsp_org: Organization,
        farming_org: Organization,
        area_unit: MeasurementUnit,
        db: Session,
        test_user: User
    ):
        """Test FSP dashboard counts audits in progress."""
        # Requirement 3.3: Dashboard displays audits in progress count
        # Create farm, plot, and crop (required for audits)
        farm = Farm(
            name="Test Farm",
            organization_id=farming_org.id,
            location='SRID=4326;POINT(77.5946 12.9716)',
            area=Decimal("10.5"),
            area_unit_id=area_unit.id,
            created_by=test_user.id
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        plot = Plot(
            name="Test Plot",
            farm_id=farm.id,
            boundary='SRID=4326;POLYGON((77.5946 12.9716, 77.5956 12.9716, 77.5956 12.9726, 77.5946 12.9726, 77.5946 12.9716))',
            area=Decimal("5.0"),
            area_unit_id=area_unit.id,
            created_by=test_user.id
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)
        
        crop = Crop(
            plot_id=plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PRODUCTION,
            created_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        # Create a template (required for audits)
        from app.models.template import Template
        template = Template(
            name="Test Template",
            fsp_organization_id=fsp_org.id,
            is_active=True,
            created_by=test_user.id
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        
        # Create audits
        for i in range(2):
            audit = Audit(
                farming_organization_id=farming_org.id,
                fsp_organization_id=fsp_org.id,
                crop_id=crop.id,
                template_id=template.id,
                name=f"Test Audit {i+1}",
                status=AuditStatus.IN_PROGRESS,
                created_by=test_user.id
            )
            db.add(audit)
        
        # Create finalized audit (should not be counted)
        finalized_audit = Audit(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            crop_id=crop.id,
            template_id=template.id,
            name="Finalized Audit",
            status=AuditStatus.FINALIZED,
            created_by=test_user.id
        )
        db.add(finalized_audit)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/fsp/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify audit count
        assert data["stats"]["auditsInProgress"] == 2
    
    def test_fsp_dashboard_action_required_items(
        self,
        client: TestClient,
        auth_headers: dict,
        fsp_org: Organization,
        farming_org: Organization,
        area_unit: MeasurementUnit,
        db: Session,
        test_user: User
    ):
        """Test FSP dashboard returns action required items."""
        # Requirement 3.4: Dashboard displays action required section
        # Create new work order request
        wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Pending Work Order",
            status=WorkOrderStatus.PENDING,
            created_by=test_user.id
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)
        
        # Create farm, plot, crop, and template for audit
        farm = Farm(
            name="Test Farm",
            organization_id=farming_org.id,
            location='SRID=4326;POINT(77.5946 12.9716)',
            area=Decimal("10.5"),
            area_unit_id=area_unit.id,
            created_by=test_user.id
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        plot = Plot(
            name="Test Plot",
            farm_id=farm.id,
            boundary='SRID=4326;POLYGON((77.5946 12.9716, 77.5956 12.9716, 77.5956 12.9726, 77.5946 12.9726, 77.5946 12.9716))',
            area=Decimal("5.0"),
            area_unit_id=area_unit.id,
            created_by=test_user.id
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)
        
        crop = Crop(
            plot_id=plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PRODUCTION,
            created_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        from app.models.template import Template
        template = Template(
            name="Test Template",
            fsp_organization_id=fsp_org.id,
            is_active=True,
            created_by=test_user.id
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        
        # Create audit to finalize
        audit = Audit(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            crop_id=crop.id,
            template_id=template.id,
            name="Audit to Finalize",
            status=AuditStatus.IN_PROGRESS,
            created_by=test_user.id
        )
        db.add(audit)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/fsp/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify action required items
        action_required = data["actionRequired"]
        assert len(action_required["newWorkOrderRequests"]) > 0
        assert len(action_required["auditsToFinalize"]) > 0
    
    def test_fsp_dashboard_unauthorized(
        self,
        client: TestClient
    ):
        """Test FSP dashboard requires authentication."""
        response = client.get("/api/v1/bff/fsp/dashboard")
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]


class TestNotificationCount:
    """Tests for GET /api/v1/notifications/unread-count."""
    
    def test_notification_count_success(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test getting unread notification count."""
        # Requirement 1.3: Display unread notification count
        response = client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
    
    def test_notification_count_unauthorized(
        self,
        client: TestClient
    ):
        """Test notification count requires authentication."""
        response = client.get("/api/v1/notifications/unread-count")
        
        # Should fail with unauthorized error
        assert response.status_code in [401, 403]
    
    def test_notification_count_accuracy(
        self,
        client: TestClient,
        auth_headers: dict
    ):
        """Test notification count returns accurate count."""
        # Requirement 1.3: Accurate notification count
        # Note: This is a placeholder test since notification model is not yet implemented
        response = client.get(
            "/api/v1/notifications/unread-count",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # For now, count should be 0 (placeholder implementation)
        assert data["count"] == 0


class TestDashboardDataAggregation:
    """Tests for dashboard data aggregation accuracy."""
    
    def test_farming_dashboard_aggregates_all_data(
        self,
        client: TestClient,
        auth_headers: dict,
        farming_org: Organization,
        fsp_org: Organization,
        area_unit: MeasurementUnit,
        db: Session
    ):
        """Test farming dashboard aggregates data from all sources."""
        # Requirement 3.1, 3.2: Dashboard aggregates data from multiple services
        # Create comprehensive test data
        
        # Create farm
        farm = Farm(
            name="Test Farm",
            organization_id=farming_org.id,
            location='SRID=4326;POINT(77.5946 12.9716)',
            area=Decimal("10.5"),
            area_unit_id=area_unit.id,
            created_by=farming_org.created_by
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        # Create plot
        plot = Plot(
            name="Test Plot",
            farm_id=farm.id,
            boundary='SRID=4326;POLYGON((77.5946 12.9716, 77.5956 12.9716, 77.5956 12.9726, 77.5946 12.9726, 77.5946 12.9716))',
            area=Decimal("5.0"),
            area_unit_id=area_unit.id,
            created_by=farming_org.created_by
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)
        
        # Create crop
        crop = Crop(
            plot_id=plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PRODUCTION,
            created_by=farming_org.created_by
        )
        db.add(crop)
        db.commit()
        
        # Create work order
        wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Test Work Order",
            status=WorkOrderStatus.ACTIVE,
            created_by=farming_org.created_by
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)
        
        # Create query
        query = Query(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            work_order_id=wo.id,
            title="Test Query",
            description="Test query description",
            status=QueryStatus.OPEN,
            created_by=farming_org.created_by
        )
        db.add(query)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/farming/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all data is aggregated correctly
        stats = data["stats"]
        assert stats["farms"] == 1
        assert stats["activeCrops"] == 1
        assert stats["activeServices"] == 1
        assert stats["openIssues"] == 1
        assert stats["activeUsers"] == 1
    
    def test_fsp_dashboard_aggregates_all_data(
        self,
        client: TestClient,
        auth_headers: dict,
        fsp_org: Organization,
        farming_org: Organization,
        area_unit: MeasurementUnit,
        db: Session,
        test_user: User
    ):
        """Test FSP dashboard aggregates data from all sources."""
        # Requirement 3.1, 3.2: Dashboard aggregates data from multiple services
        # Create work order
        wo = WorkOrder(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            title="Test Work Order",
            status=WorkOrderStatus.ACTIVE,
            created_by=test_user.id
        )
        db.add(wo)
        db.commit()
        db.refresh(wo)
        
        # Create farm, plot, crop for audit
        farm = Farm(
            name="Test Farm",
            organization_id=farming_org.id,
            location='SRID=4326;POINT(77.5946 12.9716)',
            area=Decimal("10.5"),
            area_unit_id=area_unit.id,
            created_by=test_user.id
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        plot = Plot(
            name="Test Plot",
            farm_id=farm.id,
            boundary='SRID=4326;POLYGON((77.5946 12.9716, 77.5956 12.9716, 77.5956 12.9726, 77.5946 12.9726, 77.5946 12.9716))',
            area=Decimal("5.0"),
            area_unit_id=area_unit.id,
            created_by=test_user.id
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)
        
        crop = Crop(
            plot_id=plot.id,
            name="Test Crop",
            lifecycle=CropLifecycle.PRODUCTION,
            created_by=test_user.id
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        
        from app.models.template import Template
        template = Template(
            name="Test Template",
            fsp_organization_id=fsp_org.id,
            is_active=True,
            created_by=test_user.id
        )
        db.add(template)
        db.commit()
        db.refresh(template)
        
        # Create audit
        audit = Audit(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            crop_id=crop.id,
            template_id=template.id,
            name="Test Audit",
            status=AuditStatus.IN_PROGRESS,
            created_by=test_user.id
        )
        db.add(audit)
        
        # Create query
        query = Query(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            work_order_id=wo.id,
            title="Test Query",
            description="Test query description",
            status=QueryStatus.OPEN,
            created_by=test_user.id
        )
        db.add(query)
        db.commit()
        
        response = client.get(
            "/api/v1/bff/fsp/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all data is aggregated correctly
        stats = data["stats"]
        assert stats["activeClients"] == 1
        assert stats["activeOrders"] == 1
        assert stats["auditsInProgress"] == 1
        assert stats["pendingQueries"] == 1
        assert stats["activeTeam"] == 1
