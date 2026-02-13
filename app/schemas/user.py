"""
User schemas for Uzhathunai v2.0.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    preferred_language: Optional[str] = Field("en", max_length=10)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        # Remove spaces and dashes
        phone = v.replace(" ", "").replace("-", "")
        # Check if it's a valid phone number (basic validation)
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('preferred_language')
    def validate_language(cls, v):
        """Validate language code."""
        valid_languages = ['en', 'ta', 'ml', 'hi']  # Add more as needed
        if v and v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=72)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity."""
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


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    preferred_language: Optional[str] = Field(None, max_length=10)
    specialization: Optional[str] = Field(None, max_length=200)
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        phone = v.replace(" ", "").replace("-", "")
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise ValueError('Invalid phone number format')
        return v
    
    @validator('preferred_language')
    def validate_language(cls, v):
        """Validate language code."""
        if v is None:
            return v
        valid_languages = ['en', 'ta', 'ml', 'hi']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {", ".join(valid_languages)}')
        return v


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    preferred_language: str
    specialization: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FreelancerResponse(BaseModel):
    """Schema for individual freelancer in search results."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialization: Optional[str] = None
    profile_picture: Optional[str] = None
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True


class UserBasicInfo(BaseModel):
    """Schema for basic user info (for assignment details)."""
    id: str
    first_name: str
    last_name: str
    profile_picture_url: Optional[str] = None
    role: Optional[str] = None  # Populated dynamically
    
    @validator('id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID to string."""
        if v is not None:
            return str(v)
        return v
    
    class Config:
        from_attributes = True
