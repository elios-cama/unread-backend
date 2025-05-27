"""
User management endpoints.
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
    # Check if username is being changed and if it's already taken
    if user_in.username and user_in.username != current_user.username:
        existing_user = await user_service.get_user_by_username(db, user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
    
    # Check if email is being changed and if it's already taken
    if user_in.email and user_in.email != current_user.email:
        existing_user = await user_service.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    user = await user_service.update_user(db, current_user, user_in)
    return user


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