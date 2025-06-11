"""
Collection schemas with privacy controls.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ebook import PrivacyStatus

if TYPE_CHECKING:
    from app.schemas.user import UserPublic
    from app.schemas.ebook import EbookWithAuthor


class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: PrivacyStatus = Field(default=PrivacyStatus.PRIVATE)


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection."""
    pass


class CollectionUpdate(BaseModel):
    """Schema for updating a collection."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[PrivacyStatus] = None


class CollectionInDB(CollectionBase):
    """Schema for collection as stored in database."""
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Collection(CollectionInDB):
    """Schema for collection response."""
    pass


class CollectionWithAuthor(Collection):
    """Schema for collection response with author information."""
    author: "UserPublic"


class CollectionWithEbooks(CollectionWithAuthor):
    """Schema for collection response with ebooks."""
    ebooks: List["EbookWithAuthor"]


class CollectionList(BaseModel):
    """Schema for paginated collection list response."""
    items: List[CollectionWithAuthor]
    total: int
    page: int
    size: int
    pages: int


class CollectionEbookAdd(BaseModel):
    """Schema for adding ebook to collection."""
    ebook_id: UUID


class CollectionEbookRemove(BaseModel):
    """Schema for removing ebook from collection."""
    ebook_id: UUID


# ============================================================================
# FRONTEND-FRIENDLY COLLECTION MODELS
# ============================================================================

class EbookCoverPreview(BaseModel):
    """Minimal ebook data for collection previews."""
    id: UUID
    title: str
    cover_image_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class CollectionGridItem(BaseModel):
    """Collection data optimized for frontend grid display."""
    id: UUID
    name: str
    description: Optional[str] = None
    status: PrivacyStatus
    author_id: UUID
    ebook_count: int = 0
    cover_previews: List[EbookCoverPreview] = []  # Up to 4 ebooks for preview
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CollectionGridList(BaseModel):
    """Schema for collection grid list response."""
    items: List[CollectionGridItem]
    total: int
    page: int
    size: int
    pages: int