"""
Subscription Routes
Endpoints for user notification subscriptions
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel
import structlog
import uuid
from datetime import datetime

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])
logger = structlog.get_logger()


class SubscriptionCreate(BaseModel):
    user_id: str
    category: Optional[str] = None
    location: Optional[dict] = None
    severity_threshold: Optional[str] = "medium"
    notification_channels: List[str] = ["push"]


class Subscription(BaseModel):
    id: str
    user_id: str
    category: Optional[str] = None
    location: Optional[dict] = None
    severity_threshold: str
    notification_channels: List[str]
    created_at: str
    is_active: bool = True


# In-memory storage for demo (would use Firebase in production)
subscriptions_db: dict = {}


@router.post("", response_model=Subscription, status_code=status.HTTP_201_CREATED)
async def create_subscription(subscription_data: SubscriptionCreate):
    """
    Create a new notification subscription
    
    Users can subscribe to:
    - Specific event categories
    - Geographic areas
    - Severity levels
    """
    try:
        subscription_id = str(uuid.uuid4())
        
        subscription = Subscription(
            id=subscription_id,
            user_id=subscription_data.user_id,
            category=subscription_data.category,
            location=subscription_data.location,
            severity_threshold=subscription_data.severity_threshold,
            notification_channels=subscription_data.notification_channels,
            created_at=datetime.utcnow().isoformat(),
            is_active=True
        )
        
        # Store subscription
        if subscription_data.user_id not in subscriptions_db:
            subscriptions_db[subscription_data.user_id] = []
        
        subscriptions_db[subscription_data.user_id].append(subscription.model_dump())
        
        logger.info("Subscription created", subscription_id=subscription_id, user_id=subscription_data.user_id)
        
        return subscription
        
    except Exception as e:
        logger.error("Error creating subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )


@router.get("/{user_id}", response_model=List[Subscription])
async def get_user_subscriptions(user_id: str):
    """
    Get all subscriptions for a user
    """
    try:
        user_subs = subscriptions_db.get(user_id, [])
        return user_subs
        
    except Exception as e:
        logger.error("Error fetching subscriptions", error=str(e), user_id=user_id)
        return []


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(subscription_id: str):
    """
    Delete a subscription
    """
    try:
        # Find and remove subscription
        for user_id, subs in subscriptions_db.items():
            for i, sub in enumerate(subs):
                if sub['id'] == subscription_id:
                    subscriptions_db[user_id].pop(i)
                    logger.info("Subscription deleted", subscription_id=subscription_id)
                    return
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting subscription", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subscription"
        )
