"""
Main API router for version 1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, ebooks, collections, shares, reading, reviews

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ebooks.router, prefix="/ebooks", tags=["ebooks"])
api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
api_router.include_router(shares.router, prefix="/shares", tags=["shares"])
api_router.include_router(reading.router, prefix="/reading", tags=["reading"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"]) 