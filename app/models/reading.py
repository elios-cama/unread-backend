"""
Simplified Reading progress model.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ReadingProgress(Base):
    """Simplified reading progress model."""
    
    __tablename__ = "reading_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and ebook
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id"), nullable=False)
    
    # Simple progress tracking
    current_page = Column(Integer, default=0)
    total_pages = Column(Integer, nullable=True)
    progress_percentage = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    last_read_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="reading_progress")
    ebook = relationship("Ebook", back_populates="reading_progress")
    
    def __repr__(self) -> str:
        return f"<ReadingProgress(user_id={self.user_id}, ebook_id={self.ebook_id}, progress={self.progress_percentage}%)>" 