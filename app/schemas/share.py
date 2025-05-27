"""
Share link schemas for invite-only access.
"""

from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.share import ShareableType

if TYPE_CHECKING:
    from app.schemas.user import UserPublic
    from app.schemas.ebook import EbookWithAuthor
    from app.schemas.collection import CollectionWithAuthor


class ShareLinkBase(BaseModel):
    shareable_type: ShareableType
    expires_at: Optional[datetime] = None
    max_uses: Optional[int] = Field(None, ge=1, le=100)


class ShareLinkCreate(ShareLinkBase):
    """Schema for creating a share link."""
    ebook_id: Optional[UUID] = None
    collection_id: Optional[UUID] = None
    
    # Convenience fields for common expiration times
    expires_in_hours: Optional[int] = Field(None, ge=1, le=168)  # Max 1 week
    
    @validator('expires_in_hours')
    def set_expires_at(cls, v, values):
        if v:
            values['expires_at'] = datetime.utcnow() + timedelta(hours=v)
        return v
    
    @validator('collection_id')
    def validate_shareable_content(cls, v, values):
        shareable_type = values.get('shareable_type')
        ebook_id = values.get('ebook_id')
        
        if shareable_type == ShareableType.EBOOK and not ebook_id:
            raise ValueError('ebook_id is required when sharing an ebook')
        if shareable_type == ShareableType.COLLECTION and not v:
            raise ValueError('collection_id is required when sharing a collection')
        if shareable_type == ShareableType.EBOOK and v:
            raise ValueError('collection_id should not be set when sharing an ebook')
        if shareable_type == ShareableType.COLLECTION and ebook_id:
            raise ValueError('ebook_id should not be set when sharing a collection')
        
        return v


class ShareLinkInDB(ShareLinkBase):
    """Schema for share link as stored in database."""
    id: UUID
    ebook_id: Optional[UUID]
    collection_id: Optional[UUID]
    author_id: UUID
    share_token: str
    is_active: bool
    use_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShareLink(ShareLinkInDB):
    """Schema for share link response."""
    is_expired: bool
    is_exhausted: bool
    is_valid: bool


class ShareLinkWithContent(ShareLink):
    """Schema for share link with the shared content."""
    author: "UserPublic"
    ebook: Optional["EbookWithAuthor"] = None
    collection: Optional["CollectionWithAuthor"] = None


class ShareLinkAccess(BaseModel):
    """Schema for accessing content via share link."""
    share_token: str
    
    
class ShareLinkResponse(BaseModel):
    """Schema for share link creation response."""
    share_link: ShareLink
    share_url: str
    message: str 