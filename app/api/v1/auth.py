"""
Authentication API routes for Uzhathunai v2.0.
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenRefresh,
    UserLogout,
    UserUpdate,
    ChangePassword,
    TokenResponse,
    AuthResponse,
    MessageResponse
)
from app.schemas.response import BaseResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.core.config import settings

router = APIRouter()

@router.post(
    "/register",
    response_model=BaseResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return authentication tokens"
)
def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    auth_service = AuthService(db)
    
    # Get device info from request
    device_info = {
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None
    }
    
    user, access_token, refresh_token = auth_service.register_user(
        user_data=user_data,
        device_info=device_info
    )
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user": user,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
    }


@router.post(
    "/login",
    response_model=BaseResponse[AuthResponse],
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return tokens"
)
def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password.
    """
    auth_service = AuthService(db)
    
    # Get device info and IP from request
    device_info = {
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None
    }
    
    user, access_token, refresh_token = auth_service.login_user(
        login_data=login_data,
        device_info=device_info,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "user": user,
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        }
    }


@router.post(
    "/refresh",
    response_model=BaseResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using refresh token"
)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token.
    """
    auth_service = AuthService(db)
    
    access_token = auth_service.refresh_access_token(token_data.refresh_token)
    
    return {
        "success": True,
        "message": "Token refreshed successfully",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    }


@router.post(
    "/logout",
    response_model=BaseResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Revoke refresh token(s)"
)
def logout(
    logout_data: UserLogout,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh tokens.
    """
    auth_service = AuthService(db)
    
    auth_service.logout_user(
        user_id=str(current_user.id),
        logout_all=logout_data.logout_all_devices
    )
    
    message = "Logged out from all devices" if logout_data.logout_all_devices else "Logged out successfully"
    
    return {
        "success": True,
        "message": message,
        "data": {"message": message}
    }


@router.get(
    "/me",
    response_model=BaseResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get current user profile with roles",
    description="Get authenticated user's profile information including roles and freelancer status"
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile with roles.
    """
    auth_service = AuthService(db)
    
    # Get user roles
    roles = auth_service.get_user_roles(current_user.id)
    
    # Check if freelancer
    is_freelancer = auth_service.is_freelancer(current_user.id)
    
    return {
        "success": True,
        "message": "User profile retrieved",
        "data": {
            "user": current_user.to_dict(),
            "roles": roles,
            "is_freelancer": is_freelancer
        }
    }


@router.put(
    "/me",
    response_model=BaseResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Update authenticated user's profile information"
)
def update_user_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    """
    auth_service = AuthService(db)
    
    updated_user = auth_service.update_profile(
        user_id=str(current_user.id),
        profile_data=profile_data
    )
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "data": updated_user
    }


@router.post(
    "/change-password",
    response_model=BaseResponse[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user password and revoke all refresh tokens"
)
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    """
    auth_service = AuthService(db)
    
    auth_service.change_password(
        user_id=str(current_user.id),
        password_data=password_data
    )
    
    return {
        "success": True,
        "message": "Password changed successfully. Please login again on all devices.",
        "data": {"message": "Password changed successfully. Please login again on all devices."}
    }
