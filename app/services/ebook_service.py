"""
Ebook service with privacy controls.
"""

import math
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ebook import Ebook, PrivacyStatus
from app.models.user import User
from app.schemas.ebook import (
    EbookCreate, EbookUpdate, EbookList, EbookWithAuthor, 
    EbookUpload
)
from app.repositories.ebook import ebook_repository
from app.services.storage_service import storage_service


class EbookService:
    def __init__(self):
        self.repository = ebook_repository
        self.storage = storage_service

    async def create_ebook(
        self, 
        db: AsyncSession, 
        ebook_data: EbookCreate, 
        author_id: UUID
    ) -> Ebook:
        """Create a new ebook (private by default)."""
        # Create ebook with author_id
        ebook_dict = ebook_data.dict()
        ebook_dict['author_id'] = author_id
        
        ebook = await self.repository.create(db, obj_in=ebook_dict)
        return ebook

    async def upload_ebook_file(
        self, 
        db: AsyncSession, 
        ebook_id: UUID, 
        file: UploadFile,
        current_user: User
    ) -> EbookUpload:
        """Upload an ebook file."""
        # Get ebook and verify ownership
        ebook = await self.repository.get(db, ebook_id)
        if not ebook:
            raise HTTPException(status_code=404, detail="Ebook not found")
        
        if ebook.author_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to upload file for this ebook"
            )
        
        # Validate file size
        self.storage.validate_file_size(file, max_size_mb=50)
        
        # Upload file
        file_path, file_size, _ = await self.storage.upload_ebook(
            file, str(current_user.id)
        )
        
        # Update ebook with file information
        update_data = {
            'file_path': file_path,
            'file_size': file_size
        }
        
        await self.repository.update(db, db_obj=ebook, obj_in=update_data)
        
        return EbookUpload(
            ebook_id=ebook_id,
            file_path=file_path,
            file_size=file_size,
            message="Ebook file uploaded successfully"
        )

    async def upload_cover_image(
        self, 
        db: AsyncSession, 
        ebook_id: UUID, 
        file: UploadFile,
        current_user: User
    ) -> dict:
        """Upload a cover image for an ebook."""
        # Get ebook and verify ownership
        ebook = await self.repository.get(db, ebook_id)
        if not ebook:
            raise HTTPException(status_code=404, detail="Ebook not found")
        
        if ebook.author_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to upload cover for this ebook"
            )
        
        # Validate file size (smaller limit for images)
        self.storage.validate_file_size(file, max_size_mb=5)
        
        # Upload cover image
        cover_path = await self.storage.upload_cover_image(file, str(ebook_id))
        
        # Update ebook with cover path
        await self.repository.update(
            db, 
            db_obj=ebook, 
            obj_in={'cover_image_path': cover_path}
        )
        
        return {
            'ebook_id': ebook_id,
            'cover_path': cover_path,
            'cover_url': self.storage.get_cover_url(cover_path),
            'message': 'Cover image uploaded successfully'
        }

    async def get_ebook(
        self, 
        db: AsyncSession, 
        ebook_id: UUID,
        current_user: Optional[User] = None
    ) -> Optional[EbookWithAuthor]:
        """Get an ebook with access control."""
        ebook = await self.repository.get_with_author(db, ebook_id)
        if not ebook:
            return None
        
        # Check access permissions
        user_id = current_user.id if current_user else None
        can_access = await self.repository.can_access_ebook(db, ebook_id, user_id)
        
        if not can_access:
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to access this ebook"
            )
        
        # Add cover URL if cover exists
        if ebook.cover_image_path:
            ebook.cover_url = self.storage.get_cover_url(ebook.cover_image_path)
        
        return ebook

    async def get_ebooks(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20,
        search: Optional[str] = None,
        author_id: Optional[UUID] = None,
        current_user: Optional[User] = None
    ) -> EbookList:
        """Get ebooks with pagination and search."""
        if author_id:
            # Get ebooks by specific author
            # Only show all ebooks if requesting user is the author
            if current_user and current_user.id == author_id:
                ebooks = await self.repository.get_by_author(db, author_id, skip, limit)
                total = await self.repository.count(db, author_id=author_id)
            else:
                # For other users, only show public ebooks by this author
                ebooks = await self.repository.get_public_ebooks(db, skip, limit, search)
                ebooks = [e for e in ebooks if e.author_id == author_id]
                total = len(ebooks)
        else:
            # Get public ebooks
            ebooks = await self.repository.get_public_ebooks(
                db, skip, limit, search=search
            )
            total = await self.repository.count_public_ebooks(db, search=search)
        
        # Add cover URLs
        for ebook in ebooks:
            if ebook.cover_image_path:
                ebook.cover_url = self.storage.get_cover_url(ebook.cover_image_path)
        
        pages = math.ceil(total / limit) if limit > 0 else 1
        
        return EbookList(
            items=ebooks,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=limit,
            pages=pages
        )

    async def update_ebook(
        self, 
        db: AsyncSession, 
        ebook_id: UUID, 
        ebook_update: EbookUpdate,
        current_user: User
    ) -> Ebook:
        """Update an ebook."""
        ebook = await self.repository.get(db, ebook_id)
        if not ebook:
            raise HTTPException(status_code=404, detail="Ebook not found")
        
        if ebook.author_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to update this ebook"
            )
        
        updated_ebook = await self.repository.update(db, db_obj=ebook, obj_in=ebook_update)
        return updated_ebook

    async def delete_ebook(
        self, 
        db: AsyncSession, 
        ebook_id: UUID,
        current_user: User
    ) -> bool:
        """Delete an ebook."""
        ebook = await self.repository.get(db, ebook_id)
        if not ebook:
            raise HTTPException(status_code=404, detail="Ebook not found")
        
        if ebook.author_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to delete this ebook"
            )
        
        # Delete files from storage
        if ebook.file_path:
            await self.storage.delete_file(ebook.file_path)
        if ebook.cover_image_path:
            await self.storage.delete_file(ebook.cover_image_path, self.storage.cover_bucket)
        
        # Delete from database
        await self.repository.remove(db, id=ebook_id)
        return True

    async def get_download_url(
        self, 
        db: AsyncSession, 
        ebook_id: UUID,
        current_user: Optional[User] = None
    ) -> str:
        """Get download URL for an ebook with access control."""
        ebook = await self.repository.get(db, ebook_id)
        if not ebook:
            raise HTTPException(status_code=404, detail="Ebook not found")
        
        if not ebook.file_path:
            raise HTTPException(status_code=404, detail="Ebook file not found")
        
        # Check access permissions
        user_id = current_user.id if current_user else None
        can_access = await self.repository.can_access_ebook(db, ebook_id, user_id)
        
        if not can_access:
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to download this ebook"
            )
        
        # Increment download count
        await self.repository.increment_download_count(db, ebook_id)
        
        # Generate download URL
        download_url = self.storage.get_download_url(ebook.file_path)
        return download_url

    async def get_popular_ebooks(self, db: AsyncSession, limit: int = 10) -> List[Ebook]:
        """Get popular ebooks."""
        ebooks = await self.repository.get_popular_ebooks(db, limit)
        
        # Add cover URLs
        for ebook in ebooks:
            if ebook.cover_image_path:
                ebook.cover_url = self.storage.get_cover_url(ebook.cover_image_path)
        
        return ebooks

    async def get_recent_ebooks(self, db: AsyncSession, limit: int = 10) -> List[Ebook]:
        """Get recent ebooks."""
        ebooks = await self.repository.get_recent_ebooks(db, limit)
        
        # Add cover URLs
        for ebook in ebooks:
            if ebook.cover_image_path:
                ebook.cover_url = self.storage.get_cover_url(ebook.cover_image_path)
        
        return ebooks


# Create service instance
ebook_service = EbookService() 