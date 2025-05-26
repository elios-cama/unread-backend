"""
Ebook model for the Unread application.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class EbookStatus(str, enum.Enum):
    """Ebook status enum."""
    DRAFT = "draft"
    PUBLISHED = "published"
    PRIVATE = "private"
    ARCHIVED = "archived"


class EbookFormat(str, enum.Enum):
    """Ebook format enum."""
    EPUB = "epub"
    MOBI = "mobi"
    PDF = "pdf"


class Ebook(Base):
    """Ebook model."""
    
    __tablename__ = "ebooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    title = Column(String(255), nullable=False, index=True)
    subtitle = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Author information
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    author_name = Column(String(255), nullable=False)  # Denormalized for performance
    
    # Publication details
    isbn = Column(String(20), nullable=True, unique=True)
    language = Column(String(10), default="en", nullable=False)
    publication_date = Column(DateTime, nullable=True)
    
    # File information
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    format = Column(Enum(EbookFormat), nullable=False)
    original_filename = Column(String(255), nullable=False)
    
    # Cover image
    cover_image_url = Column(String(500), nullable=True)
    
    # Metadata
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    reading_time_minutes = Column(Integer, nullable=True)
    
    # Categorization
    genre = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string array
    
    # Status and visibility
    status = Column(Enum(EbookStatus), default=EbookStatus.DRAFT, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Analytics
    view_count = Column(Integer, default=0, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="ebooks")
    collection_items = relationship("CollectionItem", back_populates="ebook", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="ebook", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="ebook", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="ebook", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Ebook(id={self.id}, title={self.title}, author={self.author_name})>" 