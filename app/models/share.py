"""
Share link model for trackable sharing of ebooks.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class ShareLink(Base):
    """Share link model for tracking ebook shares."""
    
    __tablename__ = "share_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Link information
    short_code = Column(String(20), unique=True, nullable=False, index=True)
    original_url = Column(String(500), nullable=False)
    
    # Associated ebook
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id"), nullable=False)
    
    # Creator (optional - can be anonymous)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Settings
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Analytics
    click_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    ebook = relationship("Ebook", back_populates="share_links")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self) -> str:
        return f"<ShareLink(id={self.id}, short_code={self.short_code}, ebook_id={self.ebook_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the share link has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at 