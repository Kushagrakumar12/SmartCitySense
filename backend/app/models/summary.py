"""
Summary Models
Pydantic models for AI-generated summaries
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.event import EventCategory, LocationData


class SummaryBase(BaseModel):
    """Base summary model"""
    title: str = Field(..., description="Concise summary title")
    summary_text: str = Field(..., description="AI-generated summary text")
    category: EventCategory
    location: Optional[LocationData] = None


class Summary(SummaryBase):
    """Complete summary model"""
    id: Optional[str] = None
    source_event_ids: List[str] = Field(..., description="IDs of events that were summarized")
    event_count: int = Field(..., ge=1, description="Number of events summarized")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    area: Optional[str] = None
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    key_points: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timeframe: Optional[str] = Field(None, description="Time period covered (e.g., 'last 2 hours')")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "Traffic Congestion on Old Airport Road",
                "summary_text": "15 reports of heavy traffic on Old Airport Road due to a multi-vehicle accident near HAL. Average delay of 30 minutes reported. Alternative routes via Marathahalli recommended.",
                "category": "Traffic",
                "source_event_ids": ["evt123", "evt124", "evt125"],
                "event_count": 15,
                "area": "HAL",
                "sentiment_score": -0.6,
                "key_points": [
                    "Multi-vehicle accident near HAL",
                    "30-minute average delay",
                    "15 confirmed reports"
                ],
                "recommendations": [
                    "Avoid Old Airport Road until 7 PM",
                    "Use Marathahalli route as alternative"
                ],
                "timeframe": "last 2 hours"
            }
        }


class SummaryCreate(BaseModel):
    """Create new summary request"""
    event_ids: List[str] = Field(..., min_items=2, description="Event IDs to summarize")
    category: Optional[EventCategory] = None
    area: Optional[str] = None


class SummaryResponse(BaseModel):
    """API response for single summary"""
    success: bool = True
    summary: Summary
    message: Optional[str] = None


class SummaryListResponse(BaseModel):
    """API response for summary list"""
    success: bool = True
    summaries: List[Summary]
    total: int
    page: int
    page_size: int


class SummaryFilter(BaseModel):
    """Summary filtering parameters"""
    category: Optional[EventCategory] = None
    area: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
