"""
API dependencies for database sessions and OAuth authentication.
"""

from typing import Generator, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import TokenData
from app.services import user_service

# Updated token URL to reflect OAuth endpoints
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/google"
)

# Optional OAuth2 for endpoints that can work with or without auth
optional_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/google",
    auto_error=False
)


async def get_db() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """Get current authenticated user."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        
        # Convert to UUID
        token_data = TokenData(user_id=user_id)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await user_service.get_user_by_id(db, user_id=UUID(token_data.user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db), token: Optional[str] = Depends(optional_oauth2)
) -> Optional[User]:
    """Get current authenticated user (optional)."""
    if token is None:
        return None
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        token_data = TokenData(user_id=user_id)
    except (jwt.JWTError, ValidationError):
        return None
    
    user = await user_service.get_user_by_id(db, user_id=UUID(token_data.user_id))
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active superuser."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.role != "admin":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user 