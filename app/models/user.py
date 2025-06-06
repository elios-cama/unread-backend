"""
OAuth-only User model for Google and Apple authentication.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # OAuth-only fields (at least one must be present)
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    apple_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # User profile
    avatar_url = Column(String(500), nullable=True)  # Profile picture from OAuth
    
    # Simple flags
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    ebooks = relationship("Ebook", back_populates="author", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="author", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="author", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>" 