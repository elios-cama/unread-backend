"""
Collection models for organizing ebooks into series.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Collection(Base):
    """Collection model for grouping ebooks."""
    
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Author information
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Display settings
    cover_image_url = Column(String(500), nullable=True)
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="collections")
    items = relationship("CollectionItem", back_populates="collection", cascade="all, delete-orphan", order_by="CollectionItem.order_index")
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name={self.name})>"


class CollectionItem(Base):
    """Association table for ebooks in collections with ordering."""
    
    __tablename__ = "collection_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id"), nullable=False)
    ebook_id = Column(UUID(as_uuid=True), ForeignKey("ebooks.id"), nullable=False)
    
    # Ordering
    order_index = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    collection = relationship("Collection", back_populates="items")
    ebook = relationship("Ebook", back_populates="collection_items")
    
    def __repr__(self) -> str:
        return f"<CollectionItem(collection_id={self.collection_id}, ebook_id={self.ebook_id}, order={self.order_index})>" 