"""
User Service
Business logic for user management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from app.utils.firebase_client import firebase_client
from app.models.user import UserProfile, UserSubscriptions

logger = structlog.get_logger()


class UserService:
    """Service for user-related operations"""
    
    def __init__(self):
        self.collection = "users"
        self.db = firebase_client.get_db()
    
    async def get_user_profile(self, uid: str) -> Optional[UserProfile]:
        """
        Get user profile by UID
        
        Args:
            uid: User ID
            
        Returns:
            User profile or None if not found
        """
        try:
            user_data = firebase_client.get_user_document(uid)
            if user_data:
                user_data['uid'] = uid
                return UserProfile(**user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise
    
    async def create_or_update_profile(self, uid: str, data: Dict[str, Any]) -> UserProfile:
        """
        Create or update user profile
        
        Args:
            uid: User ID
            data: Profile data
            
        Returns:
            Updated user profile
        """
        try:
            # Get existing user data
            existing_user = firebase_client.get_user_document(uid)
            
            if existing_user:
                # Update existing profile
                update_data = {}
                if 'name' in data:
                    update_data['name'] = data['name']
                if 'fcm_token' in data:
                    update_data['fcm_token'] = data['fcm_token']
                
                update_data['updated_at'] = datetime.utcnow()
                firebase_client.update_document(self.collection, uid, update_data)
                logger.info(f"Updated user profile for {uid}")
            else:
                # Create new profile
                profile_data = {
                    'email': data.get('email'),
                    'name': data.get('name'),
                    'subscriptions': {
                        'categories': [],
                        'areas': []
                    },
                    'fcm_token': data.get('fcm_token'),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                firebase_client.create_user_document(uid, profile_data)
                logger.info(f"Created user profile for {uid}")
            
            # Get updated profile
            user_data = firebase_client.get_user_document(uid)
            user_data['uid'] = uid
            
            return UserProfile(**user_data)
            
        except Exception as e:
            logger.error(f"Failed to create/update user profile: {str(e)}")
            raise
    
    async def update_subscriptions(
        self,
        uid: str,
        categories: Optional[List[str]] = None,
        areas: Optional[List[str]] = None
    ) -> UserProfile:
        """
        Update user subscriptions
        
        Args:
            uid: User ID
            categories: List of event categories to subscribe to
            areas: List of areas to subscribe to
            
        Returns:
            Updated user profile
        """
        try:
            user_data = firebase_client.get_user_document(uid)
            if not user_data:
                raise ValueError(f"User {uid} not found")
            
            # Get existing subscriptions
            subscriptions = user_data.get('subscriptions', {'categories': [], 'areas': []})
            
            # Update subscriptions
            if categories is not None:
                subscriptions['categories'] = categories
            
            if areas is not None:
                subscriptions['areas'] = areas
            
            # Update in Firestore
            firebase_client.update_document(
                self.collection,
                uid,
                {'subscriptions': subscriptions, 'updated_at': datetime.utcnow()}
            )
            
            logger.info(f"Updated subscriptions for user {uid}")
            
            # Get updated profile
            user_data = firebase_client.get_user_document(uid)
            user_data['uid'] = uid
            
            return UserProfile(**user_data)
            
        except Exception as e:
            logger.error(f"Failed to update subscriptions: {str(e)}")
            raise
    
    async def update_fcm_token(self, uid: str, fcm_token: str) -> UserProfile:
        """
        Update user's FCM token for push notifications
        
        Args:
            uid: User ID
            fcm_token: Firebase Cloud Messaging token
            
        Returns:
            Updated user profile
        """
        try:
            firebase_client.update_document(
                self.collection,
                uid,
                {'fcm_token': fcm_token, 'updated_at': datetime.utcnow()}
            )
            
            logger.info(f"Updated FCM token for user {uid}")
            
            # Get updated profile
            user_data = firebase_client.get_user_document(uid)
            user_data['uid'] = uid
            
            return UserProfile(**user_data)
            
        except Exception as e:
            logger.error(f"Failed to update FCM token: {str(e)}")
            raise
    
    async def get_users_by_subscription(
        self,
        category: Optional[str] = None,
        area: Optional[str] = None
    ) -> List[UserProfile]:
        """
        Get users subscribed to a specific category or area
        
        Args:
            category: Event category
            area: Geographic area
            
        Returns:
            List of user profiles
        """
        try:
            filters = []
            
            if category:
                filters.append(('subscriptions.categories', 'array_contains', category))
            
            if area:
                filters.append(('subscriptions.areas', 'array_contains', area))
            
            users = firebase_client.query_documents(
                collection=self.collection,
                filters=filters if filters else None
            )
            
            user_profiles = []
            for user_data in users:
                if 'uid' not in user_data:
                    user_data['uid'] = user_data.get('id')
                user_profiles.append(UserProfile(**user_data))
            
            return user_profiles
            
        except Exception as e:
            logger.error(f"Failed to get users by subscription: {str(e)}")
            raise
    
    async def delete_user(self, uid: str) -> None:
        """Delete user profile"""
        try:
            firebase_client.delete_document(self.collection, uid)
            logger.info(f"Deleted user {uid}")
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise


# Singleton instance
user_service = UserService()


def get_user_service() -> UserService:
    """Get user service instance"""
    return user_service
