"""
Pydantic schemas for User model.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str
    display_name: str
    bio: Optional[str] = None
    website_url: Optional[str] = None
    role: UserRole = UserRole.READER


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        assert len(v) >= 3, 'Username must be at least 3 characters'
        assert len(v) <= 50, 'Username must be at most 50 characters'
        return v
    
    @validator('password')
    def password_validation(cls, v):
        assert len(v) >= 8, 'Password must be at least 8 characters'
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    role: Optional[UserRole] = None


class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for user response."""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in database with sensitive fields."""
    hashed_password: Optional[str] = None
    google_id: Optional[str] = None
    apple_id: Optional[str] = None


class UserProfile(BaseModel):
    """Schema for public user profile."""
    id: UUID
    username: str
    display_name: str
    bio: Optional[str] = None
    website_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None 