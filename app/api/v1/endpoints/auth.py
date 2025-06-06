"""
OAuth-only authentication endpoints for Google and Apple.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.user import User, Token, GoogleAuthData, AppleAuthData
from app.services import user_service, oauth_service

router = APIRouter()


@router.post("/google", response_model=Token)
async def google_auth(
    *,
    db: AsyncSession = Depends(deps.get_db),
    auth_data: GoogleAuthData,
) -> Any:
    """Authenticate with Google OAuth."""
    try:
        # Verify Google ID token and get user info
        google_user_info = await oauth_service.verify_google_token(auth_data.id_token)
        
        # Check if user already exists
        user = await user_service.get_user_by_google_id(db, google_id=google_user_info["sub"])
        
        if not user:
            # Check if user exists with same email
            user = await user_service.get_user_by_email(db, email=google_user_info["email"])
            if user:
                # Link Google account to existing user
                user = await user_service.link_google_account(db, user=user, google_id=google_user_info["sub"])
            else:
                # Create new user
                user = await user_service.create_google_user(db, google_user_info=google_user_info)
        
        # Update last login
        await user_service.update_last_login(db, user=user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/apple", response_model=Token)
async def apple_auth(
    *,
    db: AsyncSession = Depends(deps.get_db),
    auth_data: AppleAuthData,
) -> Any:
    """Authenticate with Apple OAuth."""
    try:
        # Verify Apple ID token and get user info
        apple_user_info = await oauth_service.verify_apple_token(
            auth_data.id_token, 
            auth_data.authorization_code
        )
        
        # Check if user already exists
        user = await user_service.get_user_by_apple_id(db, apple_id=apple_user_info["sub"])
        
        if not user:
            # Check if user exists with same email (if provided by Apple)
            if apple_user_info.get("email"):
                user = await user_service.get_user_by_email(db, email=apple_user_info["email"])
                if user:
                    # Link Apple account to existing user
                    user = await user_service.link_apple_account(db, user=user, apple_id=apple_user_info["sub"])
                else:
                    # Create new user
                    user = await user_service.create_apple_user(db, apple_user_info=apple_user_info)
            else:
                # Create new user without email (Apple privacy)
                user = await user_service.create_apple_user(db, apple_user_info=apple_user_info)
        
        # Update last login
        await user_service.update_last_login(db, user=user)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Apple authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/test-token", response_model=User)
async def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """Test access token."""
    return current_user


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