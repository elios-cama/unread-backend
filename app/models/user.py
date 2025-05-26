"""
User model for the Unread application.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User roles enum."""
    READER = "reader"
    AUTHOR = "author"
    ADMIN = "admin"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    
    # Profile information
    bio = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    social_links = Column(Text, nullable=True)  # JSON string
    
    # User status and roles
    role = Column(Enum(UserRole), default=UserRole.READER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # OAuth information
    google_id = Column(String(100), nullable=True, unique=True)
    apple_id = Column(String(100), nullable=True, unique=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    ebooks = relationship("Ebook", back_populates="author", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="author", cascade="all, delete-orphan")
    reading_progress = relationship("ReadingProgress", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>" 