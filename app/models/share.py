"""
Share link model for invite-only access to ebooks and collections.
"""

import uuid
from datetime import datetime
import enum

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ShareableType(str, enum.Enum):
    """Type of content being shared."""
    EBOOK = "ebook"
    COLLECTION = "collection"


class ShareLink(Base):
    """Share link model for invite-only access."""
    
    __tablename__ = "share_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # What's being shared
    shareable_type = Column(Enum(ShareableType), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id"), nullable=True)
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id"), nullable=True)
    
    # Who created the share
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Share token for the URL
    share_token = Column(String(50), unique=True, nullable=False, index=True)
    
    # Access control
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)  # e.g., 24h from creation
    max_uses = Column(Integer, nullable=True)     # e.g., 3 uses
    
    # Usage tracking
    use_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ebook = relationship("Ebook", back_populates="share_links")
    collection = relationship("Collection", back_populates="share_links")
    author = relationship("User", back_populates="share_links")
    
    def __repr__(self) -> str:
        return f"<ShareLink(id={self.id}, type={self.shareable_type}, token={self.share_token})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the share link has expired."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    @property
    def is_exhausted(self) -> bool:
        """Check if the share link has reached max uses."""
        if self.max_uses and self.use_count >= self.max_uses:
            return True
        return False
    
    @property
    def is_valid(self) -> bool:
        """Check if the share link is still valid."""
        return self.is_active and not self.is_expired and not self.is_exhausted 