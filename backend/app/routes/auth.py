"""
Authentication Routes
Endpoints for user authentication and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.models.user import (
    UserProfile, UserUpdate, SubscriptionUpdate,
    FCMTokenUpdate, UserResponse
)
from app.models.common import SuccessResponse
from app.utils.auth_middleware import get_current_user, verify_firebase_token
from app.services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/verify", response_model=UserResponse)
async def verify_token(user_info: Dict[str, Any] = Depends(verify_firebase_token)):
    """
    Verify Firebase ID token and return user information
    
    This endpoint verifies the Firebase authentication token and returns
    basic user information. It's used after a user signs in with Firebase Auth.
    """
    try:
        uid = user_info['uid']
        
        # Get or create user profile
        user_profile = await user_service.get_user_profile(uid)
        
        if not user_profile:
            # Create new profile
            user_profile = await user_service.create_or_update_profile(
                uid,
                {
                    'email': user_info.get('email'),
                    'name': user_info.get('name')
                }
            )
        
        return UserResponse(
            user=user_profile,
            message="Token verified successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify token: {str(e)}"
        )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user's profile
    
    Returns the complete profile of the authenticated user including
    subscription preferences and FCM token.
    """
    try:
        uid = current_user['uid']
        user_profile = await user_service.get_user_profile(uid)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserResponse(user=user_profile)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update current user's profile
    
    Allows updating user's name and FCM token.
    """
    try:
        uid = current_user['uid']
        
        # Update profile
        user_profile = await user_service.create_or_update_profile(
            uid,
            update_data.model_dump(exclude_unset=True)
        )
        
        return UserResponse(
            user=user_profile,
            message="Profile updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.put("/subscriptions", response_model=UserResponse)
async def update_subscriptions(
    subscriptions: SubscriptionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user's notification subscriptions
    
    Allows users to subscribe to specific event categories and geographic areas.
    They will receive push notifications for events matching their subscriptions.
    """
    try:
        uid = current_user['uid']
        
        # Update subscriptions
        user_profile = await user_service.update_subscriptions(
            uid,
            categories=subscriptions.categories,
            areas=subscriptions.areas
        )
        
        return UserResponse(
            user=user_profile,
            message="Subscriptions updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update subscriptions: {str(e)}"
        )


@router.post("/fcm-token", response_model=SuccessResponse)
async def update_fcm_token(
    token_data: FCMTokenUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user's Firebase Cloud Messaging token
    
    This endpoint should be called when the user's device receives a new FCM token.
    The token is used to send push notifications to the user's device.
    """
    try:
        uid = current_user['uid']
        
        await user_service.update_fcm_token(uid, token_data.fcm_token)
        
        return SuccessResponse(
            message="FCM token updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update FCM token: {str(e)}"
        )


@router.delete("/profile", response_model=SuccessResponse)
async def delete_account(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Delete user account and all associated data
    
    This permanently deletes the user's profile and subscription data.
    """
    try:
        uid = current_user['uid']
        
        await user_service.delete_user(uid)
        
        return SuccessResponse(
            message="Account deleted successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )
