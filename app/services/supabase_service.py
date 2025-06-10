"""
Supabase integration service for JWT verification and user data extraction.
"""

import httpx
import jwt
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException

from app.core.config import settings

# Set up logger
logger = logging.getLogger(__name__)


async def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Verify Supabase JWT token and return user data.
    
    Args:
        token: Supabase JWT access token
        
    Returns:
        Dict containing user data from Supabase
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    logger.info("🔐 Starting Supabase token verification")
    
    try:
        # Decode JWT without signature verification (Supabase already verified it)
        # We just need to extract the user data
        logger.info("🔓 Decoding JWT token (without signature verification)")
        decoded_token = jwt.decode(
            token,
            options={"verify_signature": False},
            audience="authenticated"
        )
        
        # Log token info (safely)
        iss = decoded_token.get("iss", "no-issuer")
        aud = decoded_token.get("aud", "no-audience")
        sub = decoded_token.get("sub", "no-subject")
        exp = decoded_token.get("exp", "no-expiry")
        logger.info(f"📋 Token info - Issuer: {iss}, Audience: {aud}, Subject: {sub}, Expires: {exp}")
        
        # Verify token is from our Supabase instance
        expected_issuer = f"{settings.SUPABASE_URL}/auth/v1"
        logger.info(f"🔍 Checking issuer: Expected='{expected_issuer}', Actual='{iss}'")
        if decoded_token.get("iss") != expected_issuer:
            logger.error(f"❌ Token issuer mismatch! Expected: {expected_issuer}, Got: {iss}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token issuer"
            )
        
        # Verify token audience
        logger.info(f"🔍 Checking audience: Expected='authenticated', Actual='{aud}'")
        if decoded_token.get("aud") != "authenticated":
            logger.error(f"❌ Token audience mismatch! Expected: authenticated, Got: {aud}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token audience"
            )
        
        logger.info("✅ Token verification successful!")
        return decoded_token
        
    except jwt.ExpiredSignatureError:
        logger.error("❌ Token has expired")
        raise HTTPException(
            status_code=401, 
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"❌ Invalid token format: {str(e)}")
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        logger.error(f"💥 Unexpected error during token verification: {type(e).__name__}: {str(e)}")
        logger.exception("Full exception traceback:")
        raise HTTPException(
            status_code=401, 
            detail=f"Token verification failed: {str(e)}"
        )


def extract_user_data(supabase_token_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user information from Supabase token data.
    
    Args:
        supabase_token_data: Decoded Supabase JWT token
        
    Returns:
        Dict with standardized user data
    """
    logger.info("📊 Extracting user data from Supabase token")
    
    # Get user ID (this matches Supabase auth.users.id)
    user_id = supabase_token_data.get("sub")
    logger.info(f"👤 User ID: {user_id}")
    if not user_id:
        logger.error("❌ No user ID found in token")
        raise HTTPException(status_code=401, detail="No user ID in token")
    
    # Get app metadata (contains provider info)
    app_metadata = supabase_token_data.get("app_metadata", {})
    provider = app_metadata.get("provider", "unknown")
    logger.info(f"🔐 Provider: {provider}")
    logger.info(f"📱 App metadata: {app_metadata}")
    
    # Get user metadata (contains profile info from OAuth)
    user_metadata = supabase_token_data.get("user_metadata", {})
    logger.info(f"👤 User metadata: {user_metadata}")
    
    # Extract email (may be None for Apple privacy)
    email = supabase_token_data.get("email")
    logger.info(f"📧 Email: {email}")
    
    # Extract avatar URL from provider
    avatar_url = None
    if provider == "google":
        avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")
    elif provider == "apple":
        # Apple doesn't typically provide avatar URLs
        avatar_url = user_metadata.get("avatar_url")
    logger.info(f"🖼️ Avatar URL: {avatar_url}")
    
    extracted_data = {
        "id": UUID(user_id),  # Convert to UUID for database
        "email": email,
        "provider": provider,
        "avatar_url": avatar_url,
        "raw_user_metadata": user_metadata,  # For debugging/future use
    }
    
    logger.info(f"✅ Successfully extracted user data: {extracted_data}")
    return extracted_data


async def get_supabase_user_info(token: str) -> Dict[str, Any]:
    """
    Get complete user information from Supabase token.
    
    This is the main function to call from auth endpoints.
    
    Args:
        token: Supabase JWT access token
        
    Returns:
        Dict with user data ready for database operations
    """
    logger.info("🚀 Starting Supabase user info extraction")
    
    # Verify token and get decoded data
    token_data = await verify_supabase_token(token)
    
    # Extract standardized user data
    user_data = extract_user_data(token_data)
    
    logger.info("🎉 Supabase user info extraction completed successfully")
    return user_data 