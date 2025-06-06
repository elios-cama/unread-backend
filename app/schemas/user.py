"""
OAuth-only User schemas for Google and Apple authentication.
Frontend-friendly data models for mobile app development.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, field_validator


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class GoogleAuthData(BaseModel):
    """Schema for Google OAuth authentication."""
    id_token: str


class AppleAuthData(BaseModel):
    """Schema for Apple OAuth authentication."""
    id_token: str
    authorization_code: str


class AuthResponse(BaseModel):
    """Schema for authentication response to frontend."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 11520  # minutes
    user: "UserProfile"


class Token(BaseModel):
    """Schema for JWT token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[str] = None


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user schema (OAuth-only)."""
    username: str
    
    @field_validator('username')
    @classmethod
    def username_validation(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be at most 50 characters')
        return v


class OAuthUserCreate(BaseModel):
    """Schema for creating a user via OAuth."""
    username: str
    google_id: Optional[str] = None
    apple_id: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def username_validation(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Username must be at most 50 characters')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def username_validation(cls, v):
        if v is not None:
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
            if len(v) < 3:
                raise ValueError('Username must be at least 3 characters')
            if len(v) > 50:
                raise ValueError('Username must be at most 50 characters')
        return v


# ============================================================================
# FRONTEND-FRIENDLY USER MODELS
# ============================================================================

class UserProfile(BaseModel):
    """Complete user profile for frontend."""
    id: UUID
    username: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    # OAuth provider info (for account linking UI)
    has_google: bool = False
    has_apple: bool = False
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user information (for author profiles, etc.)."""
    id: UUID
    username: str
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListItem(BaseModel):
    """Minimal user data for lists (search results, etc.)."""
    id: UUID
    username: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class UsernameCheck(BaseModel):
    """Response for username availability check."""
    username: str
    available: bool
    suggestions: Optional[List[str]] = None


# ============================================================================
# USER STATISTICS (useful for frontend dashboards)
# ============================================================================

class UserStats(BaseModel):
    """User statistics for frontend dashboard."""
    total_ebooks: int = 0
    total_collections: int = 0
    total_shares: int = 0
    total_reading_progress: int = 0
    recent_activity_count: int = 0


class UserDashboard(BaseModel):
    """Complete user dashboard data for frontend."""
    profile: UserProfile
    stats: UserStats
    recent_ebooks: List["EbookListItem"] = []
    recent_collections: List["CollectionListItem"] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# INTERNAL DATABASE SCHEMAS
# ============================================================================

class UserInDB(BaseModel):
    """Schema for user in database with OAuth fields."""
    id: UUID
    username: str
    google_id: Optional[str] = None
    apple_id: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Forward references for imports
from app.schemas.ebook import EbookListItem
from app.schemas.collection import CollectionListItem

UserDashboard.model_rebuild()
AuthResponse.model_rebuild() 