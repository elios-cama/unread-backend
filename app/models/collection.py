"""
Simplified Collection model with privacy controls.
"""

import uuid
import enum
import random
from datetime import datetime

from sqlalchemy import Column, DateTime, String, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.ebook import PrivacyStatus


class CollectionColor(str, enum.Enum):
    """Predefined colors for collections."""
    BLUE = "blue"
    GREEN = "green"
    PURPLE = "purple"
    ORANGE = "orange"
    RED = "red"
    PINK = "pink"
    TEAL = "teal"
    INDIGO = "indigo"
    YELLOW = "yellow"
    EMERALD = "emerald"
    ROSE = "rose"
    CYAN = "cyan"
    
    @classmethod
    def random_color(cls) -> "CollectionColor":
        """Get a random color from the available options."""
        return random.choice(list(cls))

# Association table for many-to-many relationship between collections and ebooks
collection_ebooks = Table(
    'collection_ebooks',
    Base.metadata,
    Column('collection_id', UUID(as_uuid=True), ForeignKey('collections.id'), primary_key=True),
    Column('ebook_id', UUID(as_uuid=True), ForeignKey('ebooks.id'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Collection(Base):
    """Simplified Collection model with privacy controls."""
    
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    
    # Privacy control
    status = Column(Enum(PrivacyStatus), default=PrivacyStatus.PRIVATE, nullable=False)
    
    # Color for frontend display
    color = Column(Enum(CollectionColor), default=CollectionColor.random_color, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="collections")
    ebooks = relationship("Ebook", secondary=collection_ebooks, back_populates="collections")
    share_links = relationship("ShareLink", back_populates="collection", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name={self.name}, status={self.status})>" 