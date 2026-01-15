"""
Pytest tests for Admin API endpoints.
Tests the Super Admin organization management functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization, OrganizationStatus, OrganizationType
from app.models.rbac import Role
from app.core.security import get_password_hash


@pytest.fixture
def super_admin_user(db: Session) -> User:
    """
    Create a super admin user for testing.
    """
    user = User(
        email="superadmin@test.com",
        password_hash=get_password_hash("SuperAdmin123!"),
        first_name="Super",
        last_name="Admin",
        phone="+1234567899",
        preferred_language="en",
        is_active=True,
        is_verified=True,
        is_super_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def super_admin_headers(client: TestClient, super_admin_user: User) -> dict:
    """
    Get authentication headers for super admin user.
    """
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


@pytest.fixture
def pending_organization(db: Session) -> Organization:
    """
    Create a pending organization for testing.
    """
    org = Organization(
        name="Test Pending Org",
        organization_type=OrganizationType.FARMING,
        status=OrganizationStatus.PENDING,
        is_approved=False,
        registration_number="REG123",
        email="pending@test.com"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


class TestAdminOrganizationApproval:
    """Tests for organization approval endpoint."""
    
    def test_approve_organization_success(
        self, 
        client: TestClient, 
        super_admin_headers: dict, 
        pending_organization: Organization
    ):
        """Test successful organization approval."""
        response = client.post(
            f"/api/v1/admin/organizations/{pending_organization.id}/approve",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["is_approved"] is True
        assert data["data"]["status"] == "ACTIVE"
    
    def test_approve_organization_not_found(
        self, 
        client: TestClient, 
        super_admin_headers: dict
    ):
        """Test approval of non-existent organization."""
        fake_id = str(uuid4())
        response = client.post(
            f"/api/v1/admin/organizations/{fake_id}/approve",
            headers=super_admin_headers
        )
        
        assert response.status_code == 404
    
    def test_approve_organization_unauthorized(
        self, 
        client: TestClient, 
        pending_organization: Organization,
        auth_headers: dict  # Regular user headers
    ):
        """Test that regular users cannot approve organizations."""
        response = client.post(
            f"/api/v1/admin/organizations/{pending_organization.id}/approve",
            headers=auth_headers
        )
        
        assert response.status_code in [401, 403]
    
    def test_approve_organization_no_auth(
        self, 
        client: TestClient, 
        pending_organization: Organization
    ):
        """Test approval without authentication."""
        response = client.post(
            f"/api/v1/admin/organizations/{pending_organization.id}/approve"
        )
        
        assert response.status_code == 401


class TestAdminOrganizationList:
    """Tests for organization listing endpoint."""
    
    def test_list_organizations_success(
        self, 
        client: TestClient, 
        super_admin_headers: dict,
        pending_organization: Organization
    ):
        """Test successful organization listing."""
        response = client.get(
            "/api/v1/admin/organizations",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "limit" in data["data"]
    
    def test_list_organizations_with_status_filter(
        self, 
        client: TestClient, 
        super_admin_headers: dict
    ):
        """Test organization listing with status filter."""
        response = client.get(
            "/api/v1/admin/organizations?status=PENDING",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # All returned items should have PENDING status
        for item in data["data"]["items"]:
            assert item["status"] == "PENDING"
    
    def test_list_organizations_with_approval_filter(
        self, 
        client: TestClient, 
        super_admin_headers: dict
    ):
        """Test organization listing with approval filter."""
        response = client.get(
            "/api/v1/admin/organizations?is_approved=false",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # All returned items should be not approved
        for item in data["data"]["items"]:
            assert item["is_approved"] is False
    
    def test_list_organizations_pagination(
        self, 
        client: TestClient, 
        super_admin_headers: dict
    ):
        """Test organization listing with pagination."""
        response = client.get(
            "/api/v1/admin/organizations?page=1&limit=5",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 5
        assert len(data["data"]["items"]) <= 5
    
    def test_list_organizations_unauthorized(
        self, 
        client: TestClient, 
        auth_headers: dict  # Regular user headers
    ):
        """Test that regular users cannot list all organizations."""
        response = client.get(
            "/api/v1/admin/organizations",
            headers=auth_headers
        )
        
        assert response.status_code in [401, 403]
    
    def test_list_organizations_no_auth(self, client: TestClient):
        """Test listing without authentication."""
        response = client.get("/api/v1/admin/organizations")
        
        assert response.status_code == 401
