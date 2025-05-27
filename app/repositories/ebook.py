"""
Ebook repository with privacy controls.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ebook import Ebook, PrivacyStatus
from app.models.user import User
from app.schemas.ebook import EbookCreate, EbookUpdate
from app.repositories.base import BaseRepository


class EbookRepository(BaseRepository[Ebook, EbookCreate, EbookUpdate]):
    def __init__(self):
        super().__init__(Ebook)

    async def get_with_author(self, db: AsyncSession, id: UUID) -> Optional[Ebook]:
        """Get ebook with author information."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_author(
        self, 
        db: AsyncSession, 
        author_id: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Ebook]:
        """Get ebooks by author (all statuses for the author)."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.author_id == author_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_public_ebooks(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Ebook]:
        """Get public ebooks with optional search."""
        query = (
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.status == PrivacyStatus.PUBLIC)
        )
        
        if search:
            search_filter = or_(
                self.model.title.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
            query = query.join(User).where(search_filter)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def count_public_ebooks(
        self, 
        db: AsyncSession,
        search: Optional[str] = None
    ) -> int:
        """Count public ebooks with optional search."""
        query = select(func.count(self.model.id)).where(self.model.status == PrivacyStatus.PUBLIC)
        
        if search:
            search_filter = or_(
                self.model.title.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%")
            )
            query = query.join(User).where(search_filter)
        
        result = await db.execute(query)
        return result.scalar()

    async def increment_download_count(self, db: AsyncSession, ebook_id: UUID) -> None:
        """Increment download count for an ebook."""
        ebook = await self.get(db, ebook_id)
        if ebook:
            ebook.download_count += 1
            await db.commit()

    async def can_access_ebook(
        self, 
        db: AsyncSession, 
        ebook_id: UUID, 
        user_id: Optional[UUID] = None
    ) -> bool:
        """Check if a user can access an ebook based on privacy status."""
        ebook = await self.get(db, ebook_id)
        if not ebook:
            return False
        
        # Public ebooks are accessible to everyone
        if ebook.status == PrivacyStatus.PUBLIC:
            return True
        
        # Private and invite-only ebooks are only accessible to the author
        # (invite-only access via share links is handled separately)
        if user_id and ebook.author_id == user_id:
            return True
        
        return False

    async def get_popular_ebooks(
        self, 
        db: AsyncSession, 
        limit: int = 10
    ) -> List[Ebook]:
        """Get most popular ebooks by download count."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.status == PrivacyStatus.PUBLIC)
            .order_by(self.model.download_count.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_ebooks(
        self, 
        db: AsyncSession, 
        limit: int = 10
    ) -> List[Ebook]:
        """Get most recently published ebooks."""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.author))
            .where(self.model.status == PrivacyStatus.PUBLIC)
            .order_by(self.model.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


# Create repository instance
ebook_repository = EbookRepository() 