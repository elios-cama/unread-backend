# Repository layer for database operations
from app.repositories.user import user_repository
from app.repositories.ebook import ebook_repository  
from app.repositories.collection import collection_repository

__all__ = ["user_repository", "ebook_repository", "collection_repository"]