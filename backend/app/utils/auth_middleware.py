"""
Authentication Middleware
Handles token verification and user authentication
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import structlog

from app.utils.firebase_client import firebase_client

logger = structlog.get_logger()
security = HTTPBearer()


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Verify Firebase ID token from Authorization header
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Decoded token with user information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    
    token = credentials.credentials
    
    try:
        # Verify token with Firebase
        decoded_token = firebase_client.verify_token(token)
        
        # Extract user information
        user_info = {
            'uid': decoded_token.get('uid'),
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name'),
            'email_verified': decoded_token.get('email_verified', False)
        }
        
        return user_info
        
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


async def get_current_user(
    user_info: Dict[str, Any] = Security(verify_firebase_token)
) -> Dict[str, Any]:
    """
    Get current authenticated user with profile data
    
    Args:
        user_info: User information from token
        
    Returns:
        Complete user profile
    """
    try:
        uid = user_info['uid']
        
        # Get user document from Firestore
        user_doc = firebase_client.get_user_document(uid)
        
        if not user_doc:
            # Create basic user document if doesn't exist
            user_data = {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'subscriptions': {
                    'categories': [],
                    'areas': []
                },
                'fcm_token': None
            }
            firebase_client.create_user_document(uid, user_data)
            user_doc = user_data
        
        # Add uid to user document
        user_doc['uid'] = uid
        
        return user_doc
        
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None
    Useful for endpoints that work with or without authentication
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        User information if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        decoded_token = firebase_client.verify_token(token)
        
        return {
            'uid': decoded_token.get('uid'),
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name')
        }
    except:
        return None
