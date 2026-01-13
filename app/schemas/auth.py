"""
Authentication schemas for Uzhathunai v2.0.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

from app.schemas.user import UserCreate, UserUpdate as BaseUserUpdate, UserResponse


class UserRegister(UserCreate):
    """Schema for user registration."""
    pass


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenRefresh(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class UserLogout(BaseModel):
    """Schema for user logout."""
    logout_all_devices: bool = False


class UserUpdate(BaseUserUpdate):
    """Schema for updating user profile (reuse from user schemas)."""
    pass


class ChangePassword(BaseModel):
    """Schema for changing password."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=72)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password complexity."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Schema for authentication response (user + tokens)."""
    user: UserResponse
    tokens: TokenResponse
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schema for simple message response."""
    message: str
