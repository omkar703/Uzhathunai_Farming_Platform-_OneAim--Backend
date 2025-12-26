"""
Unit tests for AuthService.
"""
import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister, UserLogin, ChangePassword
from app.schemas.user import UserUpdate
from app.models.user import User, RefreshToken
from app.core.security import verify_password, get_token_hash


class TestAuthServiceRegister:
    """Tests for user registration."""
    
    def test_register_user_success(self, db: Session, test_user_data: dict):
        """Test successful user registration."""
        auth_service = AuthService(db)
        
        user_data = UserRegister(**test_user_data)
        user, access_token, refresh_token = auth_service.register_user(user_data)
        
        # Verify user created
        assert user.email == test_user_data["email"]
        assert user.first_name == test_user_data["first_name"]
        assert user.last_name == test_user_data["last_name"]
        assert user.phone == test_user_data["phone"]
        assert user.preferred_language == test_user_data["preferred_language"]
        assert user.is_active is True
        assert user.is_verified is False
        
        # Verify password hashed
        assert user.password_hash != test_user_data["password"]
        assert verify_password(test_user_data["password"], user.password_hash)
        
        # Verify tokens returned
        assert access_token is not None
        assert refresh_token is not None
        
        # Verify refresh token stored in database
        db_token = db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id
        ).first()
        assert db_token is not None
        assert db_token.is_revoked is False
    
    def test_register_user_duplicate_email(self, db: Session, test_user: User):
        """Test registration with duplicate email."""
        from app.core.exceptions import ConflictError
        
        auth_service = AuthService(db)
        
        user_data = UserRegister(
            email=test_user.email,  # Duplicate email
            password="TestPass123!",
            first_name="Another",
            last_name="User"
        )
        
        with pytest.raises(ConflictError) as exc_info:
            auth_service.register_user(user_data)
        
        assert exc_info.value.error_code == "EMAIL_EXISTS"
    
    def test_register_user_minimal_data(self, db: Session):
        """Test registration with minimal required data."""
        auth_service = AuthService(db)
        
        user_data = UserRegister(
            email="minimal@example.com",
            password="MinPass123!"
        )
        
        user, access_token, refresh_token = auth_service.register_user(user_data)
        
        assert user.email == "minimal@example.com"
        assert user.first_name is None
        assert user.last_name is None
        assert user.phone is None
        assert user.preferred_language == "en"  # Default


class TestAuthServiceLogin:
    """Tests for user login."""
    
    def test_login_user_success(self, db: Session, test_user: User):
        """Test successful user login."""
        auth_service = AuthService(db)
        
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=False
        )
        
        user, access_token, refresh_token = auth_service.login_user(login_data)
        
        # Verify user returned
        assert user.id == test_user.id
        assert user.email == test_user.email
        
        # Verify tokens returned
        assert access_token is not None
        assert refresh_token is not None
        
        # Verify last_login updated
        db.refresh(test_user)
        assert test_user.last_login is not None
    
    def test_login_user_invalid_email(self, db: Session):
        """Test login with invalid email."""
        from app.core.exceptions import AuthenticationError
        
        auth_service = AuthService(db)
        
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="TestPass123!",
            remember_me=False
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login_user(login_data)
        
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
    
    def test_login_user_invalid_password(self, db: Session, test_user: User):
        """Test login with invalid password."""
        from app.core.exceptions import AuthenticationError
        
        auth_service = AuthService(db)
        
        login_data = UserLogin(
            email=test_user.email,
            password="WrongPassword123!",
            remember_me=False
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login_user(login_data)
        
        assert exc_info.value.error_code == "INVALID_CREDENTIALS"
    
    def test_login_user_inactive(self, db: Session, test_user: User):
        """Test login with inactive user."""
        from app.core.exceptions import AuthenticationError
        
        auth_service = AuthService(db)
        
        # Deactivate user
        test_user.is_active = False
        db.commit()
        
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=False
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.login_user(login_data)
        
        assert exc_info.value.error_code == "INACTIVE_USER"
    
    def test_login_user_remember_me(self, db: Session, test_user: User):
        """Test login with remember_me option."""
        auth_service = AuthService(db)
        
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=True
        )
        
        user, access_token, refresh_token = auth_service.login_user(login_data)
        
        # Verify tokens returned
        assert access_token is not None
        assert refresh_token is not None
        
        # Verify refresh token has extended expiry
        # (This would require checking the token expiry in the database)


class TestAuthServiceRefreshToken:
    """Tests for token refresh."""
    
    def test_refresh_access_token_success(self, db: Session, test_user: User):
        """Test successful token refresh."""
        auth_service = AuthService(db)
        
        # Login to get refresh token
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=False
        )
        user, access_token, refresh_token = auth_service.login_user(login_data)
        
        # Refresh access token
        new_access_token = auth_service.refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        assert new_access_token != access_token  # Should be different
    
    def test_refresh_access_token_invalid(self, db: Session):
        """Test token refresh with invalid token."""
        from app.core.exceptions import AuthenticationError
        
        auth_service = AuthService(db)
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.refresh_access_token("invalid_token")
        
        assert exc_info.value.error_code == "INVALID_REFRESH_TOKEN"
    
    def test_refresh_access_token_revoked(self, db: Session, test_user: User):
        """Test token refresh with revoked token."""
        from app.core.exceptions import AuthenticationError
        
        auth_service = AuthService(db)
        
        # Login to get refresh token
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=False
        )
        user, access_token, refresh_token = auth_service.login_user(login_data)
        
        # Revoke the token
        token_hash = get_token_hash(refresh_token)
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        db_token.is_revoked = True
        db.commit()
        
        # Try to refresh
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.refresh_access_token(refresh_token)
        
        assert exc_info.value.error_code == "INVALID_REFRESH_TOKEN"


class TestAuthServiceLogout:
    """Tests for user logout."""
    
    def test_logout_user_success(self, db: Session, test_user: User):
        """Test successful logout."""
        auth_service = AuthService(db)
        
        # Login to get refresh token
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=False
        )
        user, access_token, refresh_token = auth_service.login_user(login_data)
        
        # Logout
        result = auth_service.logout_user(
            user_id=str(test_user.id),
            refresh_token=refresh_token,
            logout_all=False
        )
        
        assert result is True
        
        # Verify token revoked
        token_hash = get_token_hash(refresh_token)
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        assert db_token.is_revoked is True
        assert db_token.revoked_at is not None
    
    def test_logout_all_devices(self, db: Session, test_user: User):
        """Test logout from all devices."""
        auth_service = AuthService(db)
        
        # Login multiple times (simulate multiple devices)
        for _ in range(3):
            login_data = UserLogin(
                email=test_user.email,
                password="TestPass123!",
                remember_me=False
            )
            auth_service.login_user(login_data)
        
        # Verify 3 tokens created
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id
        ).all()
        assert len(tokens) == 3
        
        # Logout from all devices
        result = auth_service.logout_user(
            user_id=str(test_user.id),
            logout_all=True
        )
        
        assert result is True
        
        # Verify all tokens revoked
        db.refresh(test_user)
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_revoked == False
        ).all()
        assert len(tokens) == 0


class TestAuthServiceChangePassword:
    """Tests for password change."""
    
    def test_change_password_success(self, db: Session, test_user: User):
        """Test successful password change."""
        auth_service = AuthService(db)
        
        # Login to create refresh token
        login_data = UserLogin(
            email=test_user.email,
            password="TestPass123!",
            remember_me=False
        )
        auth_service.login_user(login_data)
        
        # Change password
        password_data = ChangePassword(
            current_password="TestPass123!",
            new_password="NewPass456!"
        )
        
        result = auth_service.change_password(
            user_id=str(test_user.id),
            password_data=password_data
        )
        
        assert result is True
        
        # Verify password changed
        db.refresh(test_user)
        assert verify_password("NewPass456!", test_user.password_hash)
        assert not verify_password("TestPass123!", test_user.password_hash)
        
        # Verify all refresh tokens revoked
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == test_user.id,
            RefreshToken.is_revoked == False
        ).all()
        assert len(tokens) == 0
    
    def test_change_password_invalid_current(self, db: Session, test_user: User):
        """Test password change with invalid current password."""
        from app.core.exceptions import AuthenticationError
        
        auth_service = AuthService(db)
        
        password_data = ChangePassword(
            current_password="WrongPassword123!",
            new_password="NewPass456!"
        )
        
        with pytest.raises(AuthenticationError) as exc_info:
            auth_service.change_password(
                user_id=str(test_user.id),
                password_data=password_data
            )
        
        assert exc_info.value.error_code == "INVALID_CURRENT_PASSWORD"


class TestAuthServiceUpdateProfile:
    """Tests for profile update."""
    
    def test_update_profile_success(self, db: Session, test_user: User):
        """Test successful profile update."""
        auth_service = AuthService(db)
        
        profile_data = UserUpdate(
            first_name="Updated",
            last_name="Name",
            phone="+9876543210",
            preferred_language="ta"
        )
        
        updated_user = auth_service.update_profile(
            user_id=str(test_user.id),
            profile_data=profile_data
        )
        
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.phone == "+9876543210"
        assert updated_user.preferred_language == "ta"
    
    def test_update_profile_partial(self, db: Session, test_user: User):
        """Test partial profile update."""
        auth_service = AuthService(db)
        
        original_last_name = test_user.last_name
        
        profile_data = UserUpdate(
            first_name="PartialUpdate"
        )
        
        updated_user = auth_service.update_profile(
            user_id=str(test_user.id),
            profile_data=profile_data
        )
        
        assert updated_user.first_name == "PartialUpdate"
        assert updated_user.last_name == original_last_name  # Unchanged


class TestAuthServiceHelpers:
    """Tests for helper methods."""
    
    def test_get_user_by_email(self, db: Session, test_user: User):
        """Test get user by email."""
        auth_service = AuthService(db)
        
        user = auth_service.get_user_by_email(test_user.email)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_email_not_found(self, db: Session):
        """Test get user by email when not found."""
        auth_service = AuthService(db)
        
        user = auth_service.get_user_by_email("nonexistent@example.com")
        
        assert user is None
    
    def test_get_user_by_id(self, db: Session, test_user: User):
        """Test get user by ID."""
        auth_service = AuthService(db)
        
        user = auth_service.get_user_by_id(str(test_user.id))
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    def test_get_user_by_id_not_found(self, db: Session):
        """Test get user by ID when not found."""
        auth_service = AuthService(db)
        
        user = auth_service.get_user_by_id("00000000-0000-0000-0000-000000000000")
        
        assert user is None
