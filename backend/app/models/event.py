"""
Event Models
Pydantic models for event-related data
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class EventCategory(str, Enum):
    """Event category enumeration"""
    TRAFFIC = "Traffic"
    EMERGENCY = "Emergency"
    CIVIC_ISSUE = "Civic Issue"
    CULTURAL = "Cultural"
    WEATHER = "Weather"
    POWER_OUTAGE = "Power Outage"
    WATER_SUPPLY = "Water Supply"
    PROTEST = "Protest"
    CONSTRUCTION = "Construction"
    OTHER = "Other"


class EventSeverity(str, Enum):
    """Event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    """Event status"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    MONITORING = "monitoring"


class LocationData(BaseModel):
    """Geographic location"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    address: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = "Bengaluru"


class EventBase(BaseModel):
    """Base event model"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: EventCategory
    severity: EventSeverity = EventSeverity.MEDIUM
    location: LocationData
    source: str = Field(..., description="Data source (twitter, civic_portal, user_report, etc.)")


class Event(EventBase):
    """Complete event model"""
    id: Optional[str] = None
    status: EventStatus = EventStatus.ACTIVE
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    reported_by: Optional[str] = Field(None, description="User ID if user-submitted")
    media_urls: List[str] = Field(default_factory=list)
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="Sentiment score from -1 to 1")
    upvotes: int = Field(default=0, ge=0)
    report_count: int = Field(default=1, ge=1, description="Number of similar reports")
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "Heavy Traffic on Old Airport Road",
                "description": "Major congestion due to accident, expect delays",
                "category": "Traffic",
                "severity": "high",
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "Old Airport Road",
                    "area": "HAL"
                },
                "source": "twitter",
                "tags": ["accident", "congestion"]
            }
        }


class EventCreate(EventBase):
    """Create new event"""
    media_urls: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class EventUpdate(BaseModel):
    """Update event"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    status: Optional[EventStatus] = None
    severity: Optional[EventSeverity] = None


class EventFilter(BaseModel):
    """Event filtering parameters"""
    category: Optional[EventCategory] = None
    severity: Optional[EventSeverity] = None
    status: Optional[EventStatus] = None
    area: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius_km: Optional[float] = Field(None, ge=0, le=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class EventListResponse(BaseModel):
    """API response for event list"""
    success: bool = True
    events: List[Event]
    total: int
    page: int
    page_size: int
    has_more: bool


class EventResponse(BaseModel):
    """API response for single event"""
    success: bool = True
    event: Event
    message: Optional[str] = None
