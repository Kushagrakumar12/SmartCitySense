"""
User Models
Pydantic models for user-related data
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserSubscriptions(BaseModel):
    """User subscription preferences"""
    categories: List[str] = Field(default_factory=list, description="Subscribed event categories")
    areas: List[str] = Field(default_factory=list, description="Subscribed geographic areas")


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model"""
    password: Optional[str] = None  # For email/password auth


class UserProfile(UserBase):
    """Complete user profile"""
    uid: str
    subscriptions: UserSubscriptions = Field(default_factory=UserSubscriptions)
    fcm_token: Optional[str] = Field(None, description="Firebase Cloud Messaging token")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User profile update"""
    name: Optional[str] = None
    fcm_token: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """Update user subscriptions"""
    categories: Optional[List[str]] = None
    areas: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": ["Traffic", "Emergency", "Events"],
                "areas": ["Indiranagar", "Koramangala", "Whitefield"]
            }
        }


class FCMTokenUpdate(BaseModel):
    """Update FCM token"""
    fcm_token: str = Field(..., description="Firebase Cloud Messaging device token")


class UserResponse(BaseModel):
    """API response for user data"""
    success: bool = True
    user: UserProfile
    message: Optional[str] = None
