"""
Reading progress model for tracking user reading state.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ReadingProgress(Base):
    """Reading progress model for tracking user's reading state."""
    
    __tablename__ = "reading_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and ebook
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id"), nullable=False)
    
    # Progress tracking
    current_page = Column(Integer, default=0, nullable=False)
    total_pages = Column(Integer, nullable=True)
    progress_percentage = Column(Float, default=0.0, nullable=False)
    
    # Reading position (for different formats)
    chapter_id = Column(String(100), nullable=True)  # For EPUB chapters
    position_cfi = Column(String(500), nullable=True)  # Canonical Fragment Identifier for EPUB
    position_offset = Column(Integer, nullable=True)  # Character offset for text position
    
    # Reading session info
    reading_time_minutes = Column(Integer, default=0, nullable=False)
    last_read_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_finished = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    
    # Bookmarks and notes (JSON strings)
    bookmarks = Column(Text, nullable=True)  # JSON array of bookmark positions
    notes = Column(Text, nullable=True)  # JSON array of user notes
    highlights = Column(Text, nullable=True)  # JSON array of highlighted text
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reading_progress")
    ebook = relationship("Ebook", back_populates="reading_progress")
    
    def __repr__(self) -> str:
        return f"<ReadingProgress(user_id={self.user_id}, ebook_id={self.ebook_id}, progress={self.progress_percentage}%)>" 