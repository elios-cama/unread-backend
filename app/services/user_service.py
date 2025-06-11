"""
User service for Supabase-integrated business logic operations.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import OAuthUserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID (same as Supabase auth.users.id)."""
    return await user_repository.get(db, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    return await user_repository.get_by_username(db, username)


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
) -> List[User]:
    """Get users with pagination and search."""
    users, total = await user_repository.search_users(
        db, search=search, skip=skip, limit=limit, active_only=True
    )
    return users


async def create_user_from_supabase(db: AsyncSession, supabase_user_data: Dict[str, Any]) -> User:
    """
    Create a new user from Supabase user data.
    Uses the same UUID as Supabase auth.users.id.
    
    Args:
        db: Database session
        supabase_user_data: User data from Supabase token (from supabase_service.get_supabase_user_info)
    
    Returns:
        Created User object
    """
    user_id = supabase_user_data["id"]  # UUID from Supabase
    email = supabase_user_data["email"]
    provider = supabase_user_data["provider"]
    avatar_url = supabase_user_data["avatar_url"]
    
    # Generate username based on provider and available data
    if email:
        base_username = email.split("@")[0]
    else:
        # For Apple users with hidden email
        base_username = f"{provider}_user_{str(user_id)[:8]}"
    
    # Ensure username is unique
    username = await _generate_unique_username(db, base_username)
    
    # Create user using repository
    user_data = OAuthUserCreate(
        username=username,
        google_id=user_id if provider == "google" else None,
        apple_id=user_id if provider == "apple" else None,
        avatar_url=avatar_url,
    )
    
    # Create user with Supabase UUID as primary key
    user_dict = user_data.model_dump()
    user_dict["id"] = user_id  # Use Supabase UUID directly!
    user_dict["email"] = email
    user_dict["provider"] = provider
    user_dict["is_active"] = True
    
    return await user_repository.create(db, obj_in=user_dict)


async def update_user(
    db: AsyncSession, user: User, user_update: UserUpdate
) -> User:
    """Update user information."""
    update_data = user_update.model_dump(exclude_unset=True)
    
    # If updating username, ensure it's unique
    if "username" in update_data:
        if await user_repository.username_exists(db, update_data["username"], exclude_user_id=user.id):
            raise ValueError("Username already exists")
    
    return await user_repository.update(db, db_obj=user, obj_in=update_data)


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
    if not await user_repository.username_exists(db, base_username):
        return base_username
    
    # If not available, add numbers
    counter = 1
    while True:
        test_username = f"{base_username}_{counter}"
        if not await user_repository.username_exists(db, test_username):
            return test_username
        counter += 1
        
        # Safety limit to prevent infinite loops
        if counter > 1000:
            test_username = f"{base_username}_{uuid.uuid4().hex[:6]}"
            break
    
    return test_username


# Legacy functions - kept for compatibility but will be removed
async def get_user_by_google_id(db: AsyncSession, google_id: str) -> Optional[User]:
    """DEPRECATED: Use Supabase UUID instead."""
    return None


async def get_user_by_apple_id(db: AsyncSession, apple_id: str) -> Optional[User]:
    """DEPRECATED: Use Supabase UUID instead."""
    return None


async def create_google_user(db: AsyncSession, google_user_info: Dict[str, Any]) -> User:
    """DEPRECATED: Use create_user_from_supabase instead."""
    raise NotImplementedError("Use Supabase auth instead")


async def create_apple_user(db: AsyncSession, apple_user_info: Dict[str, Any]) -> User:
    """DEPRECATED: Use create_user_from_supabase instead."""
    raise NotImplementedError("Use Supabase auth instead")


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