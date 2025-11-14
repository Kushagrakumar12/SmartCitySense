"""
Alert Models
Pydantic models for predictive alerts and notifications
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.models.event import EventCategory, EventSeverity, LocationData


class AlertType(str, Enum):
    """Alert type enumeration"""
    PREDICTIVE = "predictive"
    ANOMALY = "anomaly"
    EMERGENCY = "emergency"
    TREND = "trend"


class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AlertBase(BaseModel):
    """Base alert model"""
    title: str = Field(..., min_length=5, max_length=200)
    message: str = Field(..., min_length=10, max_length=1000)
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.MEDIUM
    category: EventCategory
    location: Optional[LocationData] = None


class Alert(AlertBase):
    """Complete alert model"""
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    affected_areas: List[str] = Field(default_factory=list)
    related_events: List[str] = Field(default_factory=list, description="Related event IDs")
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    notification_sent: bool = False
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "Potential Grid Issue in HSR Layout",
                "message": "Multiple power outage reports detected. A grid issue is likely.",
                "alert_type": "predictive",
                "priority": "high",
                "category": "Power Outage",
                "affected_areas": ["HSR Layout", "BTM Layout"],
                "confidence_score": 0.85,
                "recommendations": [
                    "Check your UPS/inverter",
                    "Report to electricity board"
                ]
            }
        }


class AlertCreate(AlertBase):
    """Create new alert"""
    affected_areas: Optional[List[str]] = None
    related_events: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    """API response for single alert"""
    success: bool = True
    alert: Alert
    message: Optional[str] = None


class AlertListResponse(BaseModel):
    """API response for alert list"""
    success: bool = True
    alerts: List[Alert]
    total: int
    has_more: bool


class AlertFilter(BaseModel):
    """Alert filtering parameters"""
    alert_type: Optional[AlertType] = None
    priority: Optional[AlertPriority] = None
    category: Optional[EventCategory] = None
    area: Optional[str] = None
    is_active: Optional[bool] = True
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
