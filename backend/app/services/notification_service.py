"""
Notification Service
Handles push notifications via Firebase Cloud Messaging
"""

import requests
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime

from app.config import settings
from app.utils.firebase_client import firebase_client
from app.services.user_service import user_service

logger = structlog.get_logger()


class NotificationService:
    """Service for sending push notifications"""
    
    def __init__(self):
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.fcm_key = settings.FCM_SERVER_KEY
        self.collection = "notifications"
    
    async def send_notification(
        self,
        fcm_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send push notification to a single device
        
        Args:
            fcm_token: Firebase Cloud Messaging device token
            title: Notification title
            body: Notification body
            data: Optional data payload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.fcm_key:
                logger.warning("FCM server key not configured")
                return False
            
            payload = {
                "to": fcm_token,
                "notification": {
                    "title": title,
                    "body": body,
                    "sound": "default"
                },
                "priority": "high"
            }
            
            if data:
                payload["data"] = data
            
            headers = {
                "Authorization": f"key={self.fcm_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.fcm_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Notification sent successfully to {fcm_token[:20]}...")
                return True
            else:
                logger.error(f"Failed to send notification: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    async def send_to_multiple(
        self,
        fcm_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Send notification to multiple devices
        
        Args:
            fcm_tokens: List of FCM tokens
            title: Notification title
            body: Notification body
            data: Optional data payload
            
        Returns:
            Dictionary with success and failure counts
        """
        success_count = 0
        failure_count = 0
        
        # Process in batches
        batch_size = settings.NOTIFICATION_BATCH_SIZE
        
        for i in range(0, len(fcm_tokens), batch_size):
            batch = fcm_tokens[i:i + batch_size]
            
            for token in batch:
                success = await self.send_notification(token, title, body, data)
                if success:
                    success_count += 1
                else:
                    failure_count += 1
        
        logger.info(f"Sent notifications: {success_count} successful, {failure_count} failed")
        
        return {
            "success": success_count,
            "failure": failure_count
        }
    
    async def send_to_users(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        Send notification to specific users
        
        Args:
            user_ids: List of user IDs
            title: Notification title
            body: Notification body
            data: Optional data payload
            
        Returns:
            Dictionary with success and failure counts
        """
        try:
            # Get FCM tokens for users
            fcm_tokens = []
            
            for uid in user_ids:
                user_data = firebase_client.get_user_document(uid)
                if user_data and user_data.get('fcm_token'):
                    fcm_tokens.append(user_data['fcm_token'])
            
            if not fcm_tokens:
                logger.warning("No valid FCM tokens found for users")
                return {"success": 0, "failure": 0}
            
            # Send notifications
            result = await self.send_to_multiple(fcm_tokens, title, body, data)
            
            # Log notification
            await self._log_notification(user_ids, title, body, data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send notifications to users: {str(e)}")
            return {"success": 0, "failure": len(user_ids)}
    
    async def notify_event_subscribers(
        self,
        event: Dict[str, Any],
        alert_type: str = "new_event"
    ) -> Dict[str, int]:
        """
        Notify users subscribed to an event's category or area
        
        Args:
            event: Event data
            alert_type: Type of alert (new_event, update, alert)
            
        Returns:
            Dictionary with success and failure counts
        """
        try:
            category = event.get('category')
            area = event.get('location', {}).get('area')
            
            # Get subscribed users
            users = []
            
            if category:
                category_users = await user_service.get_users_by_subscription(category=category)
                users.extend(category_users)
            
            if area:
                area_users = await user_service.get_users_by_subscription(area=area)
                users.extend(area_users)
            
            # Remove duplicates
            unique_user_ids = list(set([user.uid for user in users]))
            
            if not unique_user_ids:
                logger.info("No subscribed users found for event")
                return {"success": 0, "failure": 0}
            
            # Prepare notification
            title = f"{category} Alert" if category else "New Event"
            body = event.get('title', 'Check out this new event')
            
            data = {
                "event_id": event.get('id'),
                "category": category,
                "area": area,
                "type": alert_type
            }
            
            # Send notifications
            result = await self.send_to_users(unique_user_ids, title, body, data)
            
            logger.info(f"Notified {len(unique_user_ids)} users about event")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to notify event subscribers: {str(e)}")
            return {"success": 0, "failure": 0}
    
    async def send_alert_notification(
        self,
        alert: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Send notification for predictive alert
        
        Args:
            alert: Alert data
            
        Returns:
            Dictionary with success and failure counts
        """
        try:
            category = alert.get('category')
            affected_areas = alert.get('affected_areas', [])
            
            # Get subscribed users
            users = []
            
            if category:
                category_users = await user_service.get_users_by_subscription(category=category)
                users.extend(category_users)
            
            for area in affected_areas:
                area_users = await user_service.get_users_by_subscription(area=area)
                users.extend(area_users)
            
            # Remove duplicates
            unique_user_ids = list(set([user.uid for user in users]))
            
            if not unique_user_ids:
                logger.info("No subscribed users found for alert")
                return {"success": 0, "failure": 0}
            
            # Prepare notification
            title = alert.get('title', 'Predictive Alert')
            body = alert.get('message', 'Check out this alert')
            
            data = {
                "alert_id": alert.get('id'),
                "alert_type": alert.get('alert_type'),
                "priority": alert.get('priority'),
                "category": category,
                "type": "alert"
            }
            
            # Send notifications
            result = await self.send_to_users(unique_user_ids, title, body, data)
            
            logger.info(f"Sent alert notification to {len(unique_user_ids)} users")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send alert notification: {str(e)}")
            return {"success": 0, "failure": 0}
    
    async def _log_notification(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]],
        result: Dict[str, int]
    ) -> None:
        """Log notification to Firestore"""
        try:
            log_data = {
                "user_ids": user_ids,
                "title": title,
                "body": body,
                "data": data,
                "result": result,
                "sent_at": datetime.utcnow()
            }
            
            firebase_client.add_document(self.collection, log_data)
            
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")


# Singleton instance
notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get notification service instance"""
    return notification_service
