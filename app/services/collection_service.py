"""
Collection service for business logic.
"""

import math
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.models.ebook import PrivacyStatus
from app.models.user import User
from app.repositories.collection import collection_repository
from app.schemas.collection import (
    CollectionCreate,
    CollectionUpdate,
    CollectionList,
    CollectionWithAuthor,
    CollectionWithEbooks,
    CollectionGridList,
    CollectionGridItem,
    EbookCoverPreview,
)


class CollectionService:
    """Service for collection business logic."""

    async def get_collections(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        author_id: Optional[UUID] = None,
    ) -> CollectionList:
        """Get public collections with pagination and search."""
        collections, total = await collection_repository.get_public_collections(
            db, skip=skip, limit=limit, search=search, author_id=author_id
        )
        
        pages = math.ceil(total / limit) if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1
        
        return CollectionList(
            items=[CollectionWithAuthor.model_validate(collection) for collection in collections],
            total=total,
            page=page,
            size=limit,
            pages=pages,
        )

    async def get_my_collections(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CollectionWithAuthor]:
        """Get current user's collections (both public and private)."""
        collections = await collection_repository.get_by_author_id(
            db, author_id=user_id, skip=skip, limit=limit
        )
        return [CollectionWithAuthor.model_validate(collection) for collection in collections]

    async def get_my_collections_grid(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> CollectionGridList:
        """Get current user's collections optimized for grid display with cover previews."""
        collections, total = await collection_repository.get_user_collections_with_previews(
            db, user_id=user_id, skip=skip, limit=limit
        )
        
        grid_items = []
        for collection in collections:
            # Limit to first 4 ebooks for preview and get their covers
            preview_ebooks = collection.ebooks[:4] if collection.ebooks else []
            cover_previews = [
                EbookCoverPreview(
                    id=ebook.id,
                    title=ebook.title,
                    cover_image_url=ebook.cover_image_path  # This will need URL conversion
                )
                for ebook in preview_ebooks
                if ebook.cover_image_path  # Only include ebooks with covers
            ]
            
            grid_item = CollectionGridItem(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                status=collection.status,
                author_id=collection.author_id,
                ebook_count=len(collection.ebooks) if collection.ebooks else 0,
                cover_previews=cover_previews,
                created_at=collection.created_at,
                updated_at=collection.updated_at,
            )
            grid_items.append(grid_item)
        
        pages = math.ceil(total / limit) if limit > 0 else 1
        page = (skip // limit) + 1 if limit > 0 else 1
        
        return CollectionGridList(
            items=grid_items,
            total=total,
            page=page,
            size=limit,
            pages=pages,
        )

    async def get_collection(
        self,
        db: AsyncSession,
        collection_id: UUID,
        current_user: Optional[User] = None,
    ) -> Optional[CollectionWithEbooks]:
        """Get collection by ID with privacy checks."""
        collection = await collection_repository.get_with_ebooks(db, collection_id)
        
        if not collection:
            return None
        
        # Privacy check: only public collections or own collections are accessible
        if collection.status == PrivacyStatus.PRIVATE:
            if not current_user or collection.author_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Collection is private"
                )
        
        return CollectionWithEbooks.model_validate(collection)

    async def create_collection(
        self,
        db: AsyncSession,
        collection_in: CollectionCreate,
        user_id: UUID,
    ) -> CollectionWithAuthor:
        """Create a new collection."""
        collection_data = collection_in.model_dump()
        collection_data["author_id"] = user_id
        
        collection = await collection_repository.create(db, obj_in=collection_data)
        
        # Reload with author relationship
        collection = await collection_repository.get_with_relationships(
            db, collection.id, relationships=["author"]
        )
        
        return CollectionWithAuthor.model_validate(collection)

    async def update_collection(
        self,
        db: AsyncSession,
        collection_id: UUID,
        collection_in: CollectionUpdate,
        current_user: User,
    ) -> CollectionWithAuthor:
        """Update a collection."""
        collection = await collection_repository.get(db, collection_id)
        
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        # Check if user is the author
        if collection.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this collection"
            )
        
        update_data = collection_in.model_dump(exclude_unset=True)
        collection = await collection_repository.update(db, db_obj=collection, obj_in=update_data)
        
        # Reload with author relationship
        collection = await collection_repository.get_with_relationships(
            db, collection.id, relationships=["author"]
        )
        
        return CollectionWithAuthor.model_validate(collection)

    async def delete_collection(
        self,
        db: AsyncSession,
        collection_id: UUID,
        current_user: User,
    ) -> bool:
        """Delete a collection."""
        collection = await collection_repository.get(db, collection_id)
        
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        # Check if user is the author
        if collection.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this collection"
            )
        
        await collection_repository.remove(db, id=collection_id)
        return True

    async def add_ebook_to_collection(
        self,
        db: AsyncSession,
        collection_id: UUID,
        ebook_id: UUID,
        current_user: User,
    ) -> CollectionWithEbooks:
        """Add an ebook to a collection."""
        collection = await collection_repository.get_with_ebooks(db, collection_id)
        
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        # Check if user is the author
        if collection.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this collection"
            )
        
        # Check if ebook is already in collection
        if any(ebook.id == ebook_id for ebook in collection.ebooks):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ebook is already in this collection"
            )
        
        # Note: This would need to be implemented in the repository
        # For now, we'll leave this as a placeholder
        # await collection_repository.add_ebook(db, collection_id, ebook_id)
        
        # Reload collection with ebooks
        collection = await collection_repository.get_with_ebooks(db, collection_id)
        return CollectionWithEbooks.model_validate(collection)

    async def remove_ebook_from_collection(
        self,
        db: AsyncSession,
        collection_id: UUID,
        ebook_id: UUID,
        current_user: User,
    ) -> CollectionWithEbooks:
        """Remove an ebook from a collection."""
        collection = await collection_repository.get_with_ebooks(db, collection_id)
        
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        # Check if user is the author
        if collection.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this collection"
            )
        
        # Check if ebook is in collection
        if not any(ebook.id == ebook_id for ebook in collection.ebooks):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ebook is not in this collection"
            )
        
        # Note: This would need to be implemented in the repository
        # For now, we'll leave this as a placeholder
        # await collection_repository.remove_ebook(db, collection_id, ebook_id)
        
        # Reload collection with ebooks
        collection = await collection_repository.get_with_ebooks(db, collection_id)
        return CollectionWithEbooks.model_validate(collection)


# Create service instance
collection_service = CollectionService() 