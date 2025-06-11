"""
Collection management endpoints.
"""

from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.collection import (
    Collection,
    CollectionCreate,
    CollectionUpdate,
    CollectionList,
    CollectionWithAuthor,
    CollectionWithEbooks,
    CollectionGridList,
)
from app.services.collection_service import collection_service

router = APIRouter()


@router.get("/", response_model=CollectionList)
async def get_collections(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    author_id: Optional[UUID] = Query(None),
) -> Any:
    """Get public collections with pagination and search."""
    collections = await collection_service.get_collections(
        db, skip=skip, limit=limit, search=search, author_id=author_id
    )
    return collections


@router.get("/me", response_model=List[CollectionWithAuthor])
async def get_my_collections(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """Get current user's collections (both public and private)."""
    collections = await collection_service.get_my_collections(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return collections


@router.get("/me/grid", response_model=CollectionGridList)
async def get_my_collections_grid(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
) -> Any:
    """Get current user's collections optimized for grid display with cover previews."""
    collections = await collection_service.get_my_collections_grid(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return collections


@router.get("/{collection_id}", response_model=CollectionWithEbooks)
async def get_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    collection_id: UUID,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """Get collection by ID with ebooks."""
    collection = await collection_service.get_collection(
        db, collection_id, current_user
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.post("/", response_model=CollectionWithAuthor)
async def create_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    collection_in: CollectionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new collection."""
    collection = await collection_service.create_collection(
        db, collection_in, current_user.id
    )
    return collection


@router.put("/{collection_id}", response_model=CollectionWithAuthor)
async def update_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    collection_id: UUID,
    collection_in: CollectionUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a collection."""
    collection = await collection_service.update_collection(
        db, collection_id, collection_in, current_user
    )
    return collection


@router.delete("/{collection_id}")
async def delete_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    collection_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a collection."""
    success = await collection_service.delete_collection(
        db, collection_id, current_user
    )
    return {"message": "Collection deleted successfully"}


@router.post("/{collection_id}/ebooks/{ebook_id}", response_model=CollectionWithEbooks)
async def add_ebook_to_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    collection_id: UUID,
    ebook_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Add an ebook to a collection."""
    collection = await collection_service.add_ebook_to_collection(
        db, collection_id, ebook_id, current_user
    )
    return collection


@router.delete("/{collection_id}/ebooks/{ebook_id}", response_model=CollectionWithEbooks)
async def remove_ebook_from_collection(
    *,
    db: AsyncSession = Depends(deps.get_db),
    collection_id: UUID,
    ebook_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Remove an ebook from a collection."""
    collection = await collection_service.remove_ebook_from_collection(
        db, collection_id, ebook_id, current_user
    )
    return collection 