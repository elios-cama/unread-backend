"""
OAuth service for Google and Apple authentication.
"""

import httpx
import jwt
from typing import Dict, Any
from fastapi import HTTPException, status

from app.core.config import settings


async def verify_google_token(id_token: str) -> Dict[str, Any]:
    """
    Verify Google ID token and return user information.
    """
    try:
        # First, get Google's public keys
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.googleapis.com/oauth2/v3/certs")
            google_keys = response.json()
        
        # Decode and verify the token
        # For now, we'll do basic verification without signature check
        # In production, you should verify the signature with Google's public keys
        decoded_token = jwt.decode(
            id_token, 
            options={"verify_signature": False},  # We'll verify against Google's endpoint
            audience=settings.GOOGLE_CLIENT_ID
        )
        
        # Verify with Google's tokeninfo endpoint for additional security
        async with httpx.AsyncClient() as client:
            verify_response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            
            if verify_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token"
                )
            
            token_info = verify_response.json()
            
            # Verify audience (your app's client ID)
            if token_info.get("aud") != settings.GOOGLE_CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token audience"
                )
            
            return {
                "sub": token_info["sub"],  # Google user ID
                "email": token_info.get("email", ""),
                "name": token_info.get("name", ""),
                "picture": token_info.get("picture", ""),
                "email_verified": token_info.get("email_verified", False)
            }
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Google token verification failed: {str(e)}"
        )


async def verify_apple_token(id_token: str, authorization_code: str) -> Dict[str, Any]:
    """
    Verify Apple ID token and return user information.
    """
    try:
        # For Apple, we need to verify the JWT token
        # This is a simplified version - in production you should:
        # 1. Get Apple's public keys from https://appleid.apple.com/auth/keys
        # 2. Verify the signature properly
        # 3. Handle the authorization_code for server-to-server verification
        
        decoded_token = jwt.decode(
            id_token, 
            options={"verify_signature": False},  # Simplified for now
            audience=settings.APPLE_CLIENT_ID
        )
        
        # Basic validation
        if decoded_token.get("iss") != "https://appleid.apple.com":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Apple token issuer"
            )
        
        if decoded_token.get("aud") != settings.APPLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Apple token audience"
            )
        
        return {
            "sub": decoded_token["sub"],  # Apple user ID
            "email": decoded_token.get("email", ""),  # May be empty due to privacy
            "email_verified": decoded_token.get("email_verified", False),
            "is_private_email": decoded_token.get("is_private_email", False)
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Apple token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Apple token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Apple token verification failed: {str(e)}"
        ) 