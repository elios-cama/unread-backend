"""
Simplified Ebook schemas with privacy controls.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.ebook import PrivacyStatus

if TYPE_CHECKING:
    from app.schemas.user import UserPublic


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


class EbookList(BaseModel):
    """Schema for paginated ebook list response."""
    items: List[EbookWithAuthor]
    total: int
    page: int
    size: int
    pages: int


class EbookUpload(BaseModel):
    """Schema for ebook file upload response."""
    ebook_id: UUID
    file_path: str
    file_size: int
    message: str 