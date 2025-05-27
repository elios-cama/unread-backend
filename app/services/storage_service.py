"""
Storage service for handling file uploads and downloads with Supabase Storage.
"""

import os
import uuid
from typing import Optional, Tuple
from pathlib import Path

from fastapi import UploadFile, HTTPException
from supabase import create_client, Client

from app.core.config import settings


class StorageService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        self.ebook_bucket = "ebooks"
        self.cover_bucket = "covers"

    async def upload_ebook(self, file: UploadFile, author_id: str) -> Tuple[str, int, str]:
        """
        Upload an ebook file to Supabase Storage.
        
        Returns:
            Tuple of (file_path, file_size, file_format)
        """
        # Validate file type
        allowed_formats = ['.epub', '.pdf', '.mobi', '.txt']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_formats)}"
            )
        
        # Generate unique filename
        unique_filename = f"{author_id}/{uuid.uuid4()}{file_extension}"
        
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(self.ebook_bucket).upload(
                unique_filename, 
                file_content,
                file_options={"content-type": file.content_type}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload ebook file"
                )
            
            return unique_filename, file_size, file_extension[1:]  # Remove dot from extension
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading ebook: {str(e)}"
            )

    async def upload_cover_image(self, file: UploadFile, ebook_id: str) -> str:
        """
        Upload a cover image to Supabase Storage.
        
        Returns:
            file_path
        """
        # Validate file type
        allowed_formats = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Allowed formats: {', '.join(allowed_formats)}"
            )
        
        # Generate unique filename
        unique_filename = f"{ebook_id}/cover{file_extension}"
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(self.cover_bucket).upload(
                unique_filename, 
                file_content,
                file_options={"content-type": file.content_type}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload cover image"
                )
            
            return unique_filename
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading cover image: {str(e)}"
            )

    def get_download_url(self, file_path: str, bucket: str = None) -> str:
        """
        Get a signed URL for downloading a file.
        """
        if bucket is None:
            bucket = self.ebook_bucket
            
        try:
            response = self.supabase.storage.from_(bucket).create_signed_url(
                file_path, 
                expires_in=3600  # 1 hour
            )
            
            if 'signedURL' in response:
                return response['signedURL']
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate download URL"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating download URL: {str(e)}"
            )

    def get_cover_url(self, file_path: str) -> str:
        """
        Get a public URL for a cover image.
        """
        try:
            response = self.supabase.storage.from_(self.cover_bucket).get_public_url(file_path)
            return response['publicURL']
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting cover URL: {str(e)}"
            )

    async def delete_file(self, file_path: str, bucket: str = None) -> bool:
        """
        Delete a file from Supabase Storage.
        """
        if bucket is None:
            bucket = self.ebook_bucket
            
        try:
            response = self.supabase.storage.from_(bucket).remove([file_path])
            return response.status_code == 200
        except Exception as e:
            # Log error but don't raise exception for cleanup operations
            print(f"Error deleting file {file_path}: {str(e)}")
            return False

    def validate_file_size(self, file: UploadFile, max_size_mb: int = 50) -> None:
        """
        Validate file size.
        """
        if hasattr(file, 'size') and file.size:
            max_size_bytes = max_size_mb * 1024 * 1024
            if file.size > max_size_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {max_size_mb}MB"
                )


# Create service instance
storage_service = StorageService() 