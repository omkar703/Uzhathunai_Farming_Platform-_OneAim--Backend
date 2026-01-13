"""
Integration tests for Authentication API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, RefreshToken


class TestRegisterEndpoint:
    """Tests for POST /api/v1/auth/register"""
    
    def test_register_success(self, client: TestClient, test_user_data: dict):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "tokens" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == test_user_data["email"]
        assert user["first_name"] == test_user_data["first_name"]
        assert user["last_name"] == test_user_data["last_name"]
        assert user["phone"] == test_user_data["phone"]
        assert user["preferred_language"] == test_user_data["preferred_language"]
        assert user["is_active"] is True
        assert user["is_verified"] is False
        assert "id" in user
        assert "created_at" in user
        
        # Verify tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] == 1800  # 30 minutes
    
    def test_register_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
                "first_name": "Another",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "EMAIL_EXISTS" in data["error_code"]
    
    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "email" in str(data).lower()
    
    def test_register_weak_password(self, client: TestClient):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "password" in str(data).lower()
    
    def test_register_minimal_data(self, client: TestClient):
        """Test registration with minimal required data."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "minimal@example.com",
                "password": "MinPass123!"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "minimal@example.com"
        assert data["user"]["preferred_language"] == "en"


class TestLoginEndpoint:
    """Tests for POST /api/v1/auth/login"""
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "user" in data
        assert "tokens" in data
        
        # Verify user data
        user = data["user"]
        assert user["email"] == test_user.email
        assert user["id"] == str(test_user.id)
        
        # Verify tokens
        tokens = data["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with invalid email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "INVALID_CREDENTIALS" in data["error_code"]
    
    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with invalid password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!",
                "remember_me": False
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "INVALID_CREDENTIALS" in data["error_code"]
    
    def test_login_remember_me(self, client: TestClient, test_user: User):
        """Test login with remember_me option."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
                "remember_me": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data


class TestRefreshEndpoint:
    """Tests for POST /api/v1/auth/refresh"""
    
    def test_refresh_success(self, client: TestClient, test_user: User):
        """Test successful token refresh."""
        # Login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        
        # Refresh access token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_invalid_token(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False


class TestLogoutEndpoint:
    """Tests for POST /api/v1/auth/logout"""
    
    def test_logout_success(self, client: TestClient, auth_headers: dict):
        """Test successful logout."""
        response = client.post(
            "/api/v1/auth/logout",
            json={"logout_all_devices": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Logged out successfully" in data["message"]
    
    def test_logout_all_devices(self, client: TestClient, auth_headers: dict):
        """Test logout from all devices."""
        response = client.post(
            "/api/v1/auth/logout",
            json={"logout_all_devices": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "all devices" in data["message"].lower()
    
    def test_logout_without_auth(self, client: TestClient):
        """Test logout without authentication."""
        response = client.post(
            "/api/v1/auth/logout",
            json={"logout_all_devices": False}
        )
        
        assert response.status_code == 403  # No credentials provided


class TestGetMeEndpoint:
    """Tests for GET /api/v1/auth/me"""
    
    def test_get_me_success(self, client: TestClient, test_user: User, auth_headers: dict):
        """Test get current user profile."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == test_user.email
        assert data["id"] == str(test_user.id)
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert "password" not in data
        assert "password_hash" not in data
    
    def test_get_me_without_auth(self, client: TestClient):
        """Test get profile without authentication."""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403


class TestUpdateMeEndpoint:
    """Tests for PUT /api/v1/auth/me"""
    
    def test_update_me_success(self, client: TestClient, auth_headers: dict):
        """Test successful profile update."""
        response = client.put(
            "/api/v1/auth/me",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "phone": "+9876543210",
                "preferred_language": "ta"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["phone"] == "+9876543210"
        assert data["preferred_language"] == "ta"
    
    def test_update_me_partial(self, client: TestClient, auth_headers: dict):
        """Test partial profile update."""
        response = client.put(
            "/api/v1/auth/me",
            json={"first_name": "PartialUpdate"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "PartialUpdate"
    
    def test_update_me_without_auth(self, client: TestClient):
        """Test update profile without authentication."""
        response = client.put(
            "/api/v1/auth/me",
            json={"first_name": "Updated"}
        )
        
        assert response.status_code == 403


class TestChangePasswordEndpoint:
    """Tests for POST /api/v1/auth/change-password"""
    
    def test_change_password_success(self, client: TestClient, auth_headers: dict):
        """Test successful password change."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPass456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Password changed successfully" in data["message"]
    
    def test_change_password_invalid_current(self, client: TestClient, auth_headers: dict):
        """Test password change with invalid current password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPass456!"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
    
    def test_change_password_without_auth(self, client: TestClient):
        """Test password change without authentication."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "TestPass123!",
                "new_password": "NewPass456!"
            }
        )
        
        assert response.status_code == 403


class TestAuthFlow:
    """Tests for complete authentication flows."""
    
    def test_complete_auth_flow(self, client: TestClient, test_user_data: dict):
        """Test complete authentication flow: register → login → get profile → update → logout."""
        
        # 1. Register
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        tokens = register_response.json()["tokens"]
        access_token = tokens["access_token"]
        
        # 2. Get profile
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        # 3. Update profile
        update_response = client.put(
            "/api/v1/auth/me",
            json={"first_name": "Updated"},
            headers=headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["first_name"] == "Updated"
        
        # 4. Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            json={"logout_all_devices": False},
            headers=headers
        )
        assert logout_response.status_code == 200
    
    def test_token_refresh_flow(self, client: TestClient, test_user: User):
        """Test token refresh flow."""
        
        # 1. Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPass123!",
                "remember_me": False
            }
        )
        assert login_response.status_code == 200
        tokens = login_response.json()["tokens"]
        refresh_token = tokens["refresh_token"]
        
        # 2. Refresh access token
        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_access_token = refresh_response.json()["access_token"]
        
        # 3. Use new access token
        headers = {"Authorization": f"Bearer {new_access_token}"}
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
