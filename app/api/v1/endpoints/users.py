"""
User management endpoints for OAuth-only users.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate, UserPublic
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserSchema)
async def update_current_user_profile(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update current user profile."""
    try:
        user = await user_service.update_user(db, current_user, user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_profile(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: UUID,
) -> Any:
    """Get user profile by ID (public information only)."""
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/username/{username}", response_model=UserPublic)
async def get_user_by_username(
    *,
    db: AsyncSession = Depends(deps.get_db),
    username: str,
) -> Any:
    """Get user profile by username (public information only)."""
    user = await user_service.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/check-username/{username}")
async def check_username_availability(
    *,
    db: AsyncSession = Depends(deps.get_db),
    username: str,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Check if username is available."""
    existing_user = await user_service.get_user_by_username(db, username)
    
    # Username is available if no user exists or it belongs to current user
    is_available = not existing_user or existing_user.id == current_user.id
    
    return {
        "username": username,
        "available": is_available
    }


@router.get("/", response_model=List[UserPublic])
async def get_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
) -> Any:
    """Get users with pagination and search."""
    users = await user_service.get_users(db, skip=skip, limit=limit, search=search)
    return users 