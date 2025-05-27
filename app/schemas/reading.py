"""
Reading progress schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, validator

if TYPE_CHECKING:
    from app.schemas.ebook import Ebook


class ReadingProgressBase(BaseModel):
    current_page: int = Field(..., ge=0)
    total_pages: Optional[int] = Field(None, ge=1)
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    last_read_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('progress_percentage', pre=True, always=True)
    def calculate_progress(cls, v, values):
        if v is not None:
            return v
        current_page = values.get('current_page', 0)
        total_pages = values.get('total_pages')
        if total_pages and total_pages > 0:
            return min(100.0, (current_page / total_pages) * 100)
        return 0.0


class ReadingProgressCreate(ReadingProgressBase):
    """Schema for creating reading progress."""
    ebook_id: UUID


class ReadingProgressUpdate(BaseModel):
    """Schema for updating reading progress."""
    current_page: Optional[int] = Field(None, ge=0)
    total_pages: Optional[int] = Field(None, ge=1)
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    last_read_at: Optional[datetime] = None


class ReadingProgressInDB(ReadingProgressBase):
    """Schema for reading progress as stored in database."""
    id: UUID
    user_id: UUID
    ebook_id: UUID
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingProgress(ReadingProgressInDB):
    """Schema for reading progress response."""
    pass


class ReadingProgressWithEbook(ReadingProgress):
    """Schema for reading progress response with ebook information."""
    ebook: "Ebook"


class ReadingProgressList(BaseModel):
    """Schema for paginated reading progress list response."""
    items: List[ReadingProgressWithEbook]
    total: int
    page: int
    size: int
    pages: int


class ReadingStats(BaseModel):
    """Schema for user reading statistics."""
    user_id: UUID
    total_books_read: int
    total_books_in_progress: int
    total_pages_read: int
    average_reading_speed: Optional[float]  # pages per day
    reading_streak: int  # consecutive days
    favorite_genres: List[str]


class EbookReadingStats(BaseModel):
    """Schema for ebook reading statistics."""
    ebook_id: UUID
    total_readers: int
    completed_readers: int
    average_completion_rate: float
    average_reading_time: Optional[float]  # days to complete 