"""
User service for OAuth-only business logic operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import OAuthUserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_google_id(db: AsyncSession, google_id: str) -> Optional[User]:
    """Get user by Google ID."""
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def get_user_by_apple_id(db: AsyncSession, apple_id: str) -> Optional[User]:
    """Get user by Apple ID."""
    result = await db.execute(select(User).where(User.apple_id == apple_id))
    return result.scalar_one_or_none()


async def create_google_user(db: AsyncSession, google_user_info: Dict[str, Any]) -> User:
    """Create a new user from Google OAuth."""
    # Generate a unique username from email or name
    email = google_user_info.get("email", "")
    name = google_user_info.get("name", "")
    
    # Try to create username from email first part
    base_username = email.split("@")[0] if email else name.replace(" ", "_").lower()
    username = await _generate_unique_username(db, base_username)
    
    db_user = User(
        email=email,
        username=username,
        google_id=google_user_info["sub"],
        avatar_url=google_user_info.get("picture", ""),
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_apple_user(db: AsyncSession, apple_user_info: Dict[str, Any]) -> User:
    """Create a new user from Apple OAuth."""
    email = apple_user_info.get("email", "")
    
    # Generate username (Apple doesn't provide names usually)
    if email:
        base_username = email.split("@")[0]
    else:
        # If no email (private), generate random username
        base_username = f"user_{apple_user_info['sub'][:8]}"
    
    username = await _generate_unique_username(db, base_username)
    
    db_user = User(
        email=email,
        username=username,
        apple_id=apple_user_info["sub"],
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def link_google_account(db: AsyncSession, user: User, google_id: str) -> User:
    """Link Google account to existing user."""
    user.google_id = google_id
    await db.commit()
    await db.refresh(user)
    return user


async def link_apple_account(db: AsyncSession, user: User, apple_id: str) -> User:
    """Link Apple account to existing user."""
    user.apple_id = apple_id
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user: User, user_update: UserUpdate
) -> User:
    """Update user information."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # If updating username, ensure it's unique
    if "username" in update_data:
        existing_user = await get_user_by_username(db, update_data["username"])
        if existing_user and existing_user.id != user.id:
            raise ValueError("Username already exists")
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def update_last_login(db: AsyncSession, user: User) -> User:
    """Update user's last login timestamp."""
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user


async def is_active(user: User) -> bool:
    """Check if user is active."""
    return user.is_active


async def _generate_unique_username(db: AsyncSession, base_username: str) -> str:
    """Generate a unique username by adding numbers if needed."""
    # Clean the base username
    base_username = base_username.lower().replace(" ", "_")
    # Remove any non-alphanumeric characters except underscores and hyphens
    base_username = "".join(c for c in base_username if c.isalnum() or c in ["_", "-"])
    
    # Ensure it's not empty
    if not base_username:
        base_username = "user"
    
    # Check if base username is available
    existing_user = await get_user_by_username(db, base_username)
    if not existing_user:
        return base_username
    
    # If not available, add numbers
    counter = 1
    while True:
        test_username = f"{base_username}_{counter}"
        existing_user = await get_user_by_username(db, test_username)
        if not existing_user:
            return test_username
        counter += 1 