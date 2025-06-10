"""
Supabase-integrated authentication endpoints for Apple and Google OAuth.
"""

import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserProfile, AuthResponse
from app.services import user_service
from app.services.supabase_service import get_supabase_user_info

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/supabase", response_model=AuthResponse)
async def supabase_auth(
    *,
    db: AsyncSession = Depends(deps.get_db),
    authorization: str = Header(..., description="Bearer token from Supabase"),
) -> Any:
    """
    Authenticate with Supabase JWT token (works for both Apple and Google).
    
    This endpoint receives a Supabase JWT token from your Flutter app
    after the user has successfully signed in with Apple or Google through Supabase.
    """
    logger.info("🔐 Starting Supabase authentication flow")
    
    try:
        # Log the authorization header (masked for security)
        auth_preview = authorization[:20] + "..." if len(authorization) > 20 else authorization
        logger.info(f"📥 Received authorization header: {auth_preview}")
        
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            logger.error("❌ Invalid authorization header format - missing 'Bearer ' prefix")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer <token>'"
            )
        
        supabase_token = authorization.split(" ")[1]
        token_preview = f"{supabase_token[:20]}...{supabase_token[-10:]}" if len(supabase_token) > 30 else supabase_token
        logger.info(f"🎫 Extracted Supabase token: {token_preview}")
        
        # Get user info from Supabase token
        logger.info("🔍 Verifying Supabase token and extracting user data...")
        supabase_user_data = await get_supabase_user_info(supabase_token)
        user_id = supabase_user_data["id"]
        provider = supabase_user_data.get("provider", "unknown")
        email = supabase_user_data.get("email", "no-email")
        logger.info(f"✅ Token verified! User ID: {user_id}, Provider: {provider}, Email: {email}")
        
        # Check if user exists in our database (using Supabase UUID)
        logger.info(f"🔍 Checking if user {user_id} exists in database...")
        user = await user_service.get_user_by_id(db, user_id=user_id)
        
        if not user:
            logger.info(f"👤 User {user_id} not found in database, creating new user...")
            # Create new user with same UUID as Supabase
            user = await user_service.create_user_from_supabase(db, supabase_user_data)
            logger.info(f"✅ Created new user: {user.username} (ID: {user.id})")
        else:
            logger.info(f"✅ Found existing user: {user.username} (ID: {user.id})")
        
        # Update last login
        logger.info("🕒 Updating last login timestamp...")
        await user_service.update_last_login(db, user=user)
        
        # Create our own JWT token for API access
        logger.info("🔑 Generating backend access token...")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        logger.info(f"🎉 Authentication successful! User: {user.username}, Token expires in: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        
        # Create user profile for response
        user_profile = UserProfile(
            id=user.id,
            username=user.username,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            has_google=(user.provider == "google"),
            has_apple=(user.provider == "apple"),
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=user_profile,
        )
        
    except HTTPException as http_exc:
        logger.error(f"🚨 HTTP Exception during authentication: {http_exc.status_code} - {http_exc.detail}")
        # Re-raise HTTP exceptions from services
        raise
    except Exception as e:
        logger.error(f"💥 Unexpected error during authentication: {type(e).__name__}: {str(e)}")
        logger.exception("Full exception traceback:")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/test-token", response_model=UserProfile)
async def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """Test access token and get current user info."""
    return current_user


@router.get("/debug-config")
async def debug_config() -> Any:
    """Debug endpoint to check current configuration."""
    logger.info("🔧 Debug config endpoint called")
    return {
        "supabase_url": settings.SUPABASE_URL,
        "environment": settings.ENVIRONMENT,
        "database_url_preview": settings.DATABASE_URL[:50] + "..." if len(settings.DATABASE_URL) > 50 else settings.DATABASE_URL,
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
        "api_v1_str": settings.API_V1_STR,
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Refresh access token."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        current_user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
