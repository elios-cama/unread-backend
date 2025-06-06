"""
Simplified Ebook schemas with privacy controls.
Frontend-friendly data models for mobile app development.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ebook import PrivacyStatus

if TYPE_CHECKING:
    from app.schemas.user import UserPublic, UserListItem


class EbookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    page_count: Optional[int] = Field(None, ge=1)
    status: PrivacyStatus = Field(default=PrivacyStatus.PRIVATE)


class EbookCreate(EbookBase):
    """Schema for creating a new ebook."""
    pass


class EbookUpdate(BaseModel):
    """Schema for updating an ebook."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    page_count: Optional[int] = Field(None, ge=1)
    status: Optional[PrivacyStatus] = None


class EbookInDB(EbookBase):
    """Schema for ebook as stored in database."""
    id: UUID
    author_id: UUID
    file_path: Optional[str]
    cover_image_path: Optional[str]
    file_size: Optional[int]
    download_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Ebook(EbookInDB):
    """Schema for ebook response."""
    pass


class EbookWithAuthor(Ebook):
    """Schema for ebook response with author information."""
    author: "UserPublic"


# ============================================================================
# FRONTEND-FRIENDLY EBOOK MODELS
# ============================================================================

class EbookListItem(BaseModel):
    """Lightweight ebook data for lists, feeds, and search results."""
    id: UUID
    title: str
    cover_image_url: Optional[str] = None  # Full URL for cover image
    author: "UserListItem"
    page_count: Optional[int] = None
    status: PrivacyStatus
    download_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class EbookCard(BaseModel):
    """Enhanced ebook data for cards and featured content."""
    id: UUID
    title: str
    cover_image_url: Optional[str] = None
    author: "UserListItem"
    page_count: Optional[int] = None
    status: PrivacyStatus
    download_count: int = 0
    file_size_mb: Optional[float] = None  # File size in MB for display
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EbookDetail(EbookWithAuthor):
    """Complete ebook details for individual ebook pages."""
    file_size_mb: Optional[float] = None
    download_url: Optional[str] = None  # Generated download URL
    share_count: int = 0
    
    class Config:
        from_attributes = True


class EbookUpload(BaseModel):
    """Schema for ebook file upload response."""
    ebook_id: UUID
    file_path: str
    file_size: int
    message: str


class EbookList(BaseModel):
    """Schema for paginated ebook list response."""
    items: List[EbookListItem]
    total: int
    page: int
    size: int
    pages: int


class EbookFeed(BaseModel):
    """Schema for ebook feed/discovery response."""
    featured: List[EbookCard] = []
    recent: List[EbookListItem] = []
    popular: List[EbookListItem] = []
    total_count: int = 0


# ============================================================================
# MOBILE APP SPECIFIC MODELS
# ============================================================================

class EbookDownload(BaseModel):
    """Schema for ebook download information."""
    ebook_id: UUID
    download_url: str
    expires_at: datetime
    file_size: int
    file_format: str  # "epub", "pdf", "mobi"


class EbookSearchResult(BaseModel):
    """Schema for ebook search results."""
    items: List[EbookListItem]
    query: str
    total: int
    page: int
    size: int
    filters_applied: dict = {}
    suggestions: List[str] = [] 