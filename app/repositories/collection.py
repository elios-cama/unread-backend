"""
Collection repository for database operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.collection import Collection
from app.models.ebook import PrivacyStatus
from app.repositories.base import BaseRepository
from app.schemas.collection import CollectionCreate, CollectionUpdate


class CollectionRepository(BaseRepository[Collection, CollectionCreate, CollectionUpdate]):
    """Repository for Collection model operations."""

    async def get_by_author_id(
        self,
        db: AsyncSession,
        author_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Collection]:
        """Get collections by author ID."""
        query = (
            select(Collection)
            .options(selectinload(Collection.author))
            .where(Collection.author_id == author_id)
            .order_by(Collection.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_public_collections(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        author_id: Optional[UUID] = None,
    ) -> tuple[List[Collection], int]:
        """Get public collections with optional search and author filter."""
        query = (
            select(Collection)
            .options(selectinload(Collection.author))
            .where(Collection.status == PrivacyStatus.PUBLIC)
        )

        # Add author filter if provided
        if author_id:
            query = query.where(Collection.author_id == author_id)

        # Add search filter if provided
        if search:
            search_filter = or_(
                Collection.name.ilike(f"%{search}%"),
                Collection.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Collection.updated_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        collections = result.scalars().all()
        
        return collections, total

    async def get_with_ebooks(
        self,
        db: AsyncSession,
        collection_id: UUID,
    ) -> Optional[Collection]:
        """Get collection with its ebooks loaded."""
        query = (
            select(Collection)
            .options(
                selectinload(Collection.author),
                selectinload(Collection.ebooks).selectinload("author")
            )
            .where(Collection.id == collection_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def count_by_author(
        self,
        db: AsyncSession,
        author_id: UUID,
    ) -> int:
        """Count collections by author."""
        query = select(func.count(Collection.id)).where(Collection.author_id == author_id)
        result = await db.execute(query)
        return result.scalar()

    async def is_author(
        self,
        db: AsyncSession,
        collection_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Check if user is the author of the collection."""
        query = select(Collection.id).where(
            and_(Collection.id == collection_id, Collection.author_id == user_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_with_relationships(
        self,
        db: AsyncSession,
        collection_id: UUID,
        relationships: List[str],
    ) -> Optional[Collection]:
        """Get collection with specific relationships loaded."""
        query = select(Collection).where(Collection.id == collection_id)
        
        for relationship in relationships:
            if relationship == "author":
                query = query.options(selectinload(Collection.author))
            elif relationship == "ebooks":
                query = query.options(selectinload(Collection.ebooks))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_collections_with_previews(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Collection], int]:
        """Get user's collections with ebook previews for grid display."""
        from app.models.ebook import Ebook
        from sqlalchemy.orm import selectinload
        
        # Query collections with their ebooks (limited to first 4 for preview)
        query = (
            select(Collection)
            .options(
                selectinload(Collection.ebooks.and_(
                    # Limit to first 4 ebooks, ordered by creation date
                    # Note: SQLAlchemy doesn't support LIMIT in subquery relationships,
                    # so we'll handle the limitation in the service layer
                )).selectinload(Ebook.author)
            )
            .where(Collection.author_id == user_id)
            .order_by(Collection.updated_at.desc())
        )

        # Get total count
        count_query = select(func.count(Collection.id)).where(Collection.author_id == user_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        collections = result.scalars().all()
        
        return collections, total

    async def get_public_collections_with_previews(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[Collection], int]:
        """Get public collections with ebook previews for discovery."""
        from app.models.ebook import Ebook, PrivacyStatus as EbookPrivacyStatus
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Collection)
            .options(
                selectinload(Collection.author),
                selectinload(Collection.ebooks.and_(
                    # Only include public ebooks in preview
                    Ebook.status == EbookPrivacyStatus.PUBLIC
                )).selectinload(Ebook.author)
            )
            .where(Collection.status == PrivacyStatus.PUBLIC)
        )

        # Add search filter if provided
        if search:
            search_filter = or_(
                Collection.name.ilike(f"%{search}%"),
                Collection.description.ilike(f"%{search}%")
            )
            query = query.where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(Collection.updated_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        collections = result.scalars().all()
        
        return collections, total


# Create repository instance
collection_repository = CollectionRepository(Collection) 