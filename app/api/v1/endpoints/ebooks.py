"""
Minimalist Ebook endpoints.
"""

from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.ebook import (
    Ebook, EbookCreate, EbookUpdate, EbookList, EbookWithAuthor,
    EbookUpload
)
from app.services.ebook_service import ebook_service

router = APIRouter()


@router.post("/", response_model=Ebook)
async def create_ebook(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_in: EbookCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new ebook."""
    ebook = await ebook_service.create_ebook(db, ebook_in, current_user.id)
    return ebook


@router.get("/", response_model=EbookList)
async def get_ebooks(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    author_id: Optional[UUID] = Query(None),
) -> Any:
    """Get ebooks with pagination and search."""
    ebooks = await ebook_service.get_ebooks(
        db, skip=skip, limit=limit, search=search, author_id=author_id
    )
    return ebooks


@router.get("/{ebook_id}", response_model=EbookWithAuthor)
async def get_ebook(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
) -> Any:
    """Get ebook by ID."""
    ebook = await ebook_service.get_ebook(db, ebook_id)
    if not ebook:
        raise HTTPException(status_code=404, detail="Ebook not found")
    return ebook


@router.put("/{ebook_id}", response_model=Ebook)
async def update_ebook(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
    ebook_in: EbookUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update an ebook."""
    ebook = await ebook_service.update_ebook(db, ebook_id, ebook_in, current_user)
    return ebook


@router.delete("/{ebook_id}")
async def delete_ebook(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete an ebook."""
    success = await ebook_service.delete_ebook(db, ebook_id, current_user)
    return {"message": "Ebook deleted successfully"}


@router.post("/{ebook_id}/upload", response_model=EbookUpload)
async def upload_ebook_file(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Upload an ebook file."""
    result = await ebook_service.upload_ebook_file(db, ebook_id, file, current_user)
    return result


@router.post("/{ebook_id}/cover")
async def upload_cover_image(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Upload a cover image for an ebook."""
    result = await ebook_service.upload_cover_image(db, ebook_id, file, current_user)
    return result


@router.get("/{ebook_id}/download")
async def download_ebook(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
) -> Any:
    """Get download URL for an ebook."""
    download_url = await ebook_service.get_download_url(db, ebook_id, current_user)
    return {"download_url": download_url} 