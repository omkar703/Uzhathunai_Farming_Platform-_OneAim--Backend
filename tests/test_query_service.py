"""
Tests for Query service.

Tests query creation, status updates, and filtering.
"""
import pytest
from uuid import uuid4
from sqlalchemy.orm import Session

from app.services.query_service import QueryService
from app.models.query import Query
from app.models.work_order import WorkOrder
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import QueryStatus, WorkOrderStatus, OrganizationType, OrganizationStatus
from app.core.exceptions import NotFoundError, ValidationError


def test_create_query_success(db: Session):
    """Test successful query creation with active work order."""
    # Create test data
    farming_org = Organization(
        name="Test Farm",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE
    )
    fsp_org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE
    )
    db.add_all([farming_org, fsp_org])
    db.flush()
    
    user = User(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    work_order = WorkOrder(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_number="WO-001",
        title="Test Work Order",
        description="Test",
        status=WorkOrderStatus.ACTIVE,
        created_by=user.id,
        updated_by=user.id
    )
    db.add(work_order)
    db.commit()
    
    # Create query
    service = QueryService(db)
    query = service.create_query(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_id=work_order.id,
        title="Test Query",
        description="Need help with pest control",
        user_id=user.id,
        priority="HIGH"
    )
    
    assert query.id is not None
    assert query.query_number is not None
    assert query.title == "Test Query"
    assert query.status == QueryStatus.OPEN
    assert query.priority == "HIGH"
    assert query.farming_organization_id == farming_org.id
    assert query.fsp_organization_id == fsp_org.id
    assert query.work_order_id == work_order.id


def test_create_query_work_order_not_active(db: Session):
    """Test query creation fails when work order is not ACTIVE."""
    # Create test data
    farming_org = Organization(
        name="Test Farm",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE
    )
    fsp_org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE
    )
    db.add_all([farming_org, fsp_org])
    db.flush()
    
    user = User(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    work_order = WorkOrder(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_number="WO-001",
        title="Test Work Order",
        description="Test",
        status=WorkOrderStatus.PENDING,  # Not ACTIVE
        created_by=user.id,
        updated_by=user.id
    )
    db.add(work_order)
    db.commit()
    
    # Try to create query
    service = QueryService(db)
    
    with pytest.raises(ValidationError) as exc_info:
        service.create_query(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            work_order_id=work_order.id,
            title="Test Query",
            description="Need help",
            user_id=user.id
        )
    
    assert "Work order must be ACTIVE" in str(exc_info.value.message)


def test_create_query_invalid_priority(db: Session):
    """Test query creation fails with invalid priority."""
    # Create test data
    farming_org = Organization(
        name="Test Farm",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE
    )
    fsp_org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE
    )
    db.add_all([farming_org, fsp_org])
    db.flush()
    
    user = User(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    work_order = WorkOrder(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_number="WO-001",
        title="Test Work Order",
        description="Test",
        status=WorkOrderStatus.ACTIVE,
        created_by=user.id,
        updated_by=user.id
    )
    db.add(work_order)
    db.commit()
    
    # Try to create query with invalid priority
    service = QueryService(db)
    
    with pytest.raises(ValidationError) as exc_info:
        service.create_query(
            farming_organization_id=farming_org.id,
            fsp_organization_id=fsp_org.id,
            work_order_id=work_order.id,
            title="Test Query",
            description="Need help",
            user_id=user.id,
            priority="INVALID"
        )
    
    assert "Invalid priority level" in str(exc_info.value.message)


def test_update_query_status(db: Session):
    """Test updating query status."""
    # Create test data
    farming_org = Organization(
        name="Test Farm",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE
    )
    fsp_org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE
    )
    db.add_all([farming_org, fsp_org])
    db.flush()
    
    user = User(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    work_order = WorkOrder(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_number="WO-001",
        title="Test Work Order",
        description="Test",
        status=WorkOrderStatus.ACTIVE,
        created_by=user.id,
        updated_by=user.id
    )
    db.add(work_order)
    db.commit()
    
    # Create query
    service = QueryService(db)
    query = service.create_query(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_id=work_order.id,
        title="Test Query",
        description="Need help",
        user_id=user.id
    )
    
    assert query.status == QueryStatus.OPEN
    
    # Update status
    updated_query = service.update_query_status(
        query_id=query.id,
        status=QueryStatus.IN_PROGRESS,
        user_id=user.id
    )
    
    assert updated_query.status == QueryStatus.IN_PROGRESS


def test_get_queries_with_filters(db: Session):
    """Test getting queries with filters."""
    # Create test data
    farming_org = Organization(
        name="Test Farm",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.ACTIVE
    )
    fsp_org = Organization(
        name="Test FSP",
        organization_type=OrganizationType.FSP,
        status=OrganizationStatus.ACTIVE
    )
    db.add_all([farming_org, fsp_org])
    db.flush()
    
    user = User(
        email="test@example.com",
        password_hash="hashed",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    work_order = WorkOrder(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_number="WO-001",
        title="Test Work Order",
        description="Test",
        status=WorkOrderStatus.ACTIVE,
        created_by=user.id,
        updated_by=user.id
    )
    db.add(work_order)
    db.commit()
    
    # Create multiple queries
    service = QueryService(db)
    
    query1 = service.create_query(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_id=work_order.id,
        title="Query 1",
        description="Need help",
        user_id=user.id,
        priority="HIGH"
    )
    
    query2 = service.create_query(
        farming_organization_id=farming_org.id,
        fsp_organization_id=fsp_org.id,
        work_order_id=work_order.id,
        title="Query 2",
        description="Need help",
        user_id=user.id,
        priority="LOW"
    )
    
    # Get all queries
    queries, total = service.get_queries()
    assert total >= 2  # May have other queries from other tests
    
    # Filter by priority
    queries, total = service.get_queries(priority="HIGH")
    assert total >= 1
    assert any(q.id == query1.id for q in queries)
    
    # Filter by status
    queries, total = service.get_queries(status=QueryStatus.OPEN)
    assert total >= 2
