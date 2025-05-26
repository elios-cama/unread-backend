"""
Review model for user feedback on ebooks.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Review(Base):
    """Review model for user feedback on ebooks."""
    
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User and ebook
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id"), nullable=False)
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    
    # Status
    is_public = Column(Boolean, default=True, nullable=False)
    is_verified_purchase = Column(Boolean, default=False, nullable=False)  # For future use
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    ebook = relationship("Ebook", back_populates="reviews")
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, user_id={self.user_id}, ebook_id={self.ebook_id}, rating={self.rating})>" 