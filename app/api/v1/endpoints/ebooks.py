"""
Enhanced Ebook endpoints with mobile app optimizations.
"""

from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.ebook import (
    Ebook, EbookCreate, EbookUpdate, EbookList, EbookWithAuthor,
    EbookUpload, SignedUploadUrl, UploadUrlRequest, ConfirmUploadRequest, UploadConfirmation
)
from app.services.ebook_service import ebook_service
from app.services.storage_service import StorageService

router = APIRouter()

# Initialize storage service
storage_service = StorageService()


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


@router.post("/upload-complete", response_model=EbookUpload)
async def create_ebook_with_file(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
    title: str = Form(...),
    page_count: Optional[int] = Form(None),
    collection_id: Optional[UUID] = Form(None),
) -> Any:
    """
    Create ebook and upload file in a single operation.
    Optimized for mobile apps to reduce API calls.
    """
    ebook_data = EbookCreate(
        title=title,
        page_count=page_count,
        status="PRIVATE"  # Always start as private
    )
    
    result = await ebook_service.create_ebook_with_file(
        db, ebook_data, file, current_user, collection_id
    )
    return result


@router.post("/temp-upload")
async def upload_temp_file(
    *,
    current_user: User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
) -> Any:
    """
    Upload a file to temporary storage for processing.
    Useful for extracting metadata before creating the ebook record.
    """
    result = await ebook_service.upload_temp_file(file, current_user)
    return result


@router.post("/from-temp", response_model=EbookUpload)
async def create_ebook_from_temp(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    temp_path: str = Form(...),
    title: str = Form(...),
    page_count: Optional[int] = Form(None),
    collection_id: Optional[UUID] = Form(None),
) -> Any:
    """
    Create an ebook from a temporary file.
    Moves file from temp storage to permanent organized storage.
    """
    ebook_data = EbookCreate(
        title=title,
        page_count=page_count,
        status="PRIVATE"
    )
    
    result = await ebook_service.create_ebook_from_temp(
        db, temp_path, ebook_data, current_user, collection_id
    )
    return result


@router.get("/file-organization")
async def get_file_organization_info(
    *,
    current_user: User = Depends(deps.get_current_user),
    collection_id: Optional[UUID] = Query(None),
) -> Any:
    """
    Get file organization information for the mobile app.
    Shows where files will be stored for this user/collection.
    """
    info = ebook_service.get_file_organization_info(current_user.id, collection_id)
    return info


@router.delete("/cleanup-temp")
async def cleanup_temp_files(
    *,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Clean up temporary files for the current user."""
    result = await ebook_service.cleanup_user_temp_files(current_user)
    return result


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
    collection_id: Optional[UUID] = Query(None),
) -> Any:
    """Upload an ebook file with optional collection organization."""
    result = await ebook_service.upload_ebook_file(db, ebook_id, file, current_user, collection_id)
    return result


@router.post("/{ebook_id}/cover")
async def upload_cover_image(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ebook_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
    collection_id: Optional[UUID] = Query(None),
) -> Any:
    """Upload a cover image for an ebook with optional collection organization."""
    result = await ebook_service.upload_cover_image(db, ebook_id, file, current_user, collection_id)
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


@router.post("/upload-url", response_model=SignedUploadUrl)
async def get_ebook_upload_url(
    *,
    current_user: User = Depends(deps.get_current_user),
    upload_request: UploadUrlRequest,
) -> Any:
    """
    Get a signed URL for uploading an ebook file.
    The client uploads directly to Supabase Storage using this URL.
    """
    signed_url_data, file_path = storage_service.get_ebook_upload_url(
        author_id=str(current_user.id),
        file_extension=upload_request.file_extension,
        collection_id=str(upload_request.collection_id) if upload_request.collection_id else None
    )
    
    return SignedUploadUrl(**signed_url_data)


@router.post("/cover-upload-url", response_model=SignedUploadUrl)
async def get_cover_upload_url(
    *,
    current_user: User = Depends(deps.get_current_user),
    ebook_id: UUID = Form(...),
    file_extension: str = Form(...),
    collection_id: Optional[UUID] = Form(None),
) -> Any:
    """
    Get a signed URL for uploading a cover image.
    The client uploads directly to Supabase Storage using this URL.
    """
    if not file_extension.startswith('.'):
        file_extension = f'.{file_extension}'
    
    signed_url_data, file_path = storage_service.get_cover_upload_url(
        ebook_id=str(ebook_id),
        author_id=str(current_user.id),
        file_extension=file_extension.lower(),
        collection_id=str(collection_id) if collection_id else None
    )
    
    return SignedUploadUrl(**signed_url_data)


@router.post("/temp-upload-url", response_model=SignedUploadUrl)
async def get_temp_upload_url(
    *,
    current_user: User = Depends(deps.get_current_user),
    upload_request: UploadUrlRequest,
) -> Any:
    """
    Get a signed URL for uploading a temporary file for processing.
    Useful for extracting metadata before creating the ebook record.
    """
    signed_url_data, temp_path = storage_service.get_temp_upload_url(
        user_id=str(current_user.id),
        file_extension=upload_request.file_extension
    )
    
    return SignedUploadUrl(**signed_url_data)


@router.post("/confirm-upload", response_model=UploadConfirmation)
async def confirm_file_upload(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    confirm_request: ConfirmUploadRequest,
) -> Any:
    """
    Confirm that a file was successfully uploaded and update the ebook record.
    Call this after uploading via signed URL.
    """
    # Confirm the upload with storage service
    confirmation = storage_service.confirm_upload(
        file_path=confirm_request.file_path,
        bucket=confirm_request.bucket
    )
    
    # If ebook_id is provided, update the ebook record
    if confirm_request.ebook_id:
        await ebook_service.update_ebook_file_path(
            db,
            ebook_id=confirm_request.ebook_id,
            file_path=confirm_request.file_path,
            file_size=confirmation["file_size"],  # Fixed: was "size" but confirmation returns "file_size"
            current_user=current_user
        )
    
    return UploadConfirmation(**confirmation) 