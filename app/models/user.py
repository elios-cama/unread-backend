"""
Supabase-integrated User model for OAuth authentication.
Uses the same UUID as Supabase auth.users table.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    # Use Supabase auth.users UUID as primary key (no auto-generation!)
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # OAuth provider info (from Supabase metadata)
    provider = Column(String(20), nullable=False)  # 'apple' or 'google'
    
    # User profile (from OAuth providers)
    email = Column(String(255), nullable=True)  # May be None for Apple privacy
    avatar_url = Column(String(500), nullable=True)
    
    # User flags
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
        return f"<User(id={self.id}, username={self.username}, provider={self.provider})>" 