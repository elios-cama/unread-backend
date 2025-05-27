"""
Simplified Ebook model with privacy controls.
"""

import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class PrivacyStatus(str, enum.Enum):
    """Privacy status for ebooks and collections."""
    PRIVATE = "private"
    PUBLIC = "public"
    INVITE_ONLY = "invite_only"


class Ebook(Base):
    __tablename__ = "ebooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    page_count = Column(Integer, nullable=True)
    
    # File information
    file_path = Column(String(500), nullable=True)
    cover_image_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    
    # Privacy control
    status = Column(Enum(PrivacyStatus), default=PrivacyStatus.PRIVATE, nullable=False)
    
    # Stats
    download_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="ebooks")
    collections = relationship("Collection", secondary="collection_ebooks", back_populates="ebooks")
    share_links = relationship("ShareLink", back_populates="ebook", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="ebook", cascade="all, delete-orphan") 