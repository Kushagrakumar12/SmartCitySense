"""
Report Models
Pydantic models for user-submitted reports
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

from app.models.event import EventCategory, EventSeverity, LocationData


class ReportBase(BaseModel):
    """Base report model"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    category: EventCategory
    location: LocationData


class ReportCreate(ReportBase):
    """Create new report"""
    media_urls: Optional[List[str]] = Field(default_factory=list, description="URLs of uploaded images/videos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Waterlogged Street",
                "description": "Heavy waterlogging on main road after rain",
                "category": "Civic Issue",
                "location": {
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "address": "MG Road",
                    "area": "Central Bengaluru"
                },
                "media_urls": ["https://storage.googleapis.com/bucket/image1.jpg"]
            }
        }


class Report(ReportBase):
    """Complete report model"""
    id: Optional[str] = None
    reported_by: str = Field(..., description="User ID who submitted the report")
    severity: EventSeverity = EventSeverity.MEDIUM
    media_urls: List[str] = Field(default_factory=list)
    ai_analysis: Optional[dict] = Field(None, description="AI analysis results from vision/text models")
    status: str = Field(default="pending", description="Report processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    event_id: Optional[str] = Field(None, description="Associated event ID if converted")
    
    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    """API response for report submission"""
    success: bool = True
    report: Report
    message: str = "Report submitted successfully"


class ReportListResponse(BaseModel):
    """API response for report list"""
    success: bool = True
    reports: List[Report]
    total: int
    page: int
    page_size: int
