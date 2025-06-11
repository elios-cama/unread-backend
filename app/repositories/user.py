"""
User repository for database operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import OAuthUserCreate, UserUpdate


class UserRepository(BaseRepository[User, OAuthUserCreate, UserUpdate]):
    """Repository for User model operations."""

    async def get_by_username(
        self,
        db: AsyncSession,
        username: str,
    ) -> Optional[User]:
        """Get user by username."""
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_google_id(
        self,
        db: AsyncSession,
        google_id: str,
    ) -> Optional[User]:
        """Get user by Google ID."""
        query = select(User).where(User.google_id == google_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_apple_id(
        self,
        db: AsyncSession,
        apple_id: str,
    ) -> Optional[User]:
        """Get user by Apple ID."""
        query = select(User).where(User.apple_id == apple_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def search_users(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True,
    ) -> tuple[List[User], int]:
        """Search users with pagination."""
        query = select(User)

        # Add active filter
        if active_only:
            query = query.where(User.is_active == True)

        # Add search filter if provided
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%") if hasattr(User, 'email') else False
            )
            query = query.where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return users, total

    async def username_exists(
        self,
        db: AsyncSession,
        username: str,
        exclude_user_id: Optional[UUID] = None,
    ) -> bool:
        """Check if username exists (optionally excluding a specific user)."""
        query = select(User.id).where(User.username == username)
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    async def email_exists(
        self,
        db: AsyncSession,
        email: str,
        exclude_user_id: Optional[UUID] = None,
    ) -> bool:
        """Check if email exists (optionally excluding a specific user)."""
        query = select(User.id).where(User.email == email)
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_active_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """Get active users with pagination."""
        query = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def count_active_users(self, db: AsyncSession) -> int:
        """Count active users."""
        query = select(func.count(User.id)).where(User.is_active == True)
        result = await db.execute(query)
        return result.scalar()

    async def get_recent_users(
        self,
        db: AsyncSession,
        days: int = 7,
        limit: int = 10,
    ) -> List[User]:
        """Get recently registered users."""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = (
            select(User)
            .where(User.created_at >= cutoff_date)
            .where(User.is_active == True)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


# Create repository instance
user_repository = UserRepository(User) 