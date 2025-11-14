"""
Event and Response Schema Definitions
Pydantic models for data validation and API responses
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


# ========================================
# ENUMS FOR STANDARDIZATION
# ========================================

class EventType(str, Enum):
    """Event type categories"""
    TRAFFIC = "traffic"
    OBSTRUCTION = "obstruction"
    ACCIDENT = "accident"
    FLOODING = "flooding"
    POWER_OUTAGE = "power_outage"
    PROTEST = "protest"
    CIVIC_ISSUE = "civic_issue"
    CONSTRUCTION = "construction"
    FIRE = "fire"
    EMERGENCY = "emergency"
    CULTURAL = "cultural"
    OTHER = "other"


class SeverityLevel(str, Enum):
    """Severity levels for events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types for predictions"""
    TRAFFIC_SURGE = "traffic_surge"
    POWER_GRID_ISSUE = "power_grid_issue"
    FLOODING_RISK = "flooding_risk"
    ACCIDENT_CLUSTER = "accident_cluster"
    ANOMALY = "anomaly"
    FORECAST = "forecast"


# ========================================
# VISION ANALYSIS MODELS
# ========================================

class Coordinates(BaseModel):
    """Geographic coordinates"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class DetectedObject(BaseModel):
    """Individual object detected in image/video"""
    class_name: str = Field(..., description="Detected object class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bbox: List[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")


class VisionAnalysisRequest(BaseModel):
    """Request model for vision analysis"""
    image_url: Optional[str] = Field(None, description="URL to image")
    video_url: Optional[str] = Field(None, description="URL to video")
    location: Optional[str] = Field(None, description="Location description")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(None, description="User who submitted report")
    
    @field_validator('timestamp', mode='before')
    @classmethod
    @classmethod
    def set_timestamp(cls, v):
        return v or datetime.now(timezone.utc)


class VisionAnalysisResponse(BaseModel):
    """Response model for vision analysis"""
    event_type: EventType = Field(..., description="Classified event type")
    description: str = Field(..., description="AI-generated event description")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    severity: SeverityLevel = Field(..., description="Estimated severity")
    detected_objects: List[DetectedObject] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list, description="Relevant tags")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_version: str = Field(default="yolov8n", description="Model version used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "obstruction",
                "description": "Fallen tree blocking road near Indiranagar",
                "confidence": 0.89,
                "severity": "high",
                "detected_objects": [
                    {
                        "class_name": "tree",
                        "confidence": 0.92,
                        "bbox": [120, 340, 580, 720]
                    }
                ],
                "tags": ["obstruction", "tree", "road_block"],
                "timestamp": "2025-10-11T14:20:00Z",
                "processing_time_ms": 245.3,
                "model_version": "yolov8n"
            }
        }


# ========================================
# PREDICTIVE MODELING MODELS
# ========================================

class PredictionRequest(BaseModel):
    """Request model for predictive analysis"""
    location: Optional[str] = Field(None, description="Location to analyze")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    event_types: Optional[List[EventType]] = Field(None, description="Event types to analyze")
    time_window_minutes: int = Field(default=15, ge=5, le=120, description="Time window for analysis")
    forecast_hours: int = Field(default=24, ge=1, le=168, description="Hours to forecast ahead")


class AnomalyResult(BaseModel):
    """Anomaly detection result"""
    is_anomaly: bool = Field(..., description="Whether anomaly detected")
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score")
    event_count: int = Field(..., description="Number of events in window")
    baseline_count: float = Field(..., description="Expected baseline count")
    severity: SeverityLevel = Field(..., description="Anomaly severity")


class ForecastResult(BaseModel):
    """Forecast result"""
    forecast_timestamp: datetime = Field(..., description="Forecasted time point")
    predicted_value: float = Field(..., description="Predicted event count/metric")
    lower_bound: float = Field(..., description="Lower confidence bound")
    upper_bound: float = Field(..., description="Upper confidence bound")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Forecast confidence")


class PredictionResponse(BaseModel):
    """Response model for predictive analysis"""
    alert: Optional[str] = Field(None, description="Alert message if anomaly detected")
    alert_type: Optional[AlertType] = Field(None, description="Type of alert")
    severity: SeverityLevel = Field(..., description="Overall severity")
    anomaly_result: Optional[AnomalyResult] = Field(None, description="Anomaly detection results")
    forecast_results: Optional[List[ForecastResult]] = Field(None, description="Forecast results")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    affected_areas: List[str] = Field(default_factory=list, description="Areas affected")
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert": "Potential grid outage cluster in Whitefield",
                "alert_type": "power_grid_issue",
                "severity": "high",
                "anomaly_result": {
                    "is_anomaly": True,
                    "anomaly_score": 0.94,
                    "event_count": 12,
                    "baseline_count": 2.3,
                    "severity": "high"
                },
                "recommendations": [
                    "Multiple outage reports detected in 15 minutes",
                    "Likely grid issue - check transformer status",
                    "Estimated restoration: 2-4 hours"
                ],
                "affected_areas": ["Whitefield", "ITPL", "Brookefield"],
                "timestamp": "2025-10-11T14:25:00Z",
                "processing_time_ms": 156.8
            }
        }


# ========================================
# COMMON MODELS
# ========================================

class HealthResponse(BaseModel):
    """API health check response"""
    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    models_loaded: Dict[str, bool] = Field(default_factory=dict)
    gpu_available: bool = Field(default=False)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


# ========================================
# TEXT PROCESSING MODELS (Member B1)
# ========================================

class SummarizationRequest(BaseModel):
    """Request model for text summarization"""
    reports: List[str] = Field(..., min_length=1, description="List of text reports to summarize")
    event_type: str = Field(default="default", description="Event type (traffic, power, civic, etc.)")
    location: str = Field(default="Bengaluru", description="Location of incident")
    timestamp: Optional[datetime] = Field(None, description="Timestamp of reports")
    use_llm: bool = Field(default=True, description="Use LLM for summarization (if False, uses template)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reports": [
                    "Heavy traffic jam on Old Airport Road near KR Puram",
                    "Massive traffic on OAR, avoid until evening",
                    "Road blocked due to vehicle breakdown on Old Airport Road"
                ],
                "event_type": "traffic",
                "location": "Old Airport Road",
                "timestamp": "2025-10-11T14:30:00Z",
                "use_llm": True
            }
        }


class SummarizationResponse(BaseModel):
    """Response model for text summarization"""
    event_type: str = Field(..., description="Type of event")
    summary: str = Field(..., description="Generated summary")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    location: str = Field(..., description="Normalized location")
    timestamp: datetime = Field(..., description="Timestamp")
    source_count: int = Field(..., description="Number of original reports")
    processed_count: int = Field(..., description="Number after deduplication")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    method: str = Field(..., description="Summarization method used (llm or template)")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "traffic",
                "summary": "Heavy traffic on Old Airport Road near KR Puram due to vehicle breakdown. Avoid until evening.",
                "confidence": 0.92,
                "location": "Old Airport Road",
                "timestamp": "2025-10-11T14:30:00Z",
                "source_count": 15,
                "processed_count": 8,
                "keywords": ["traffic", "breakdown", "airport", "road", "jam"],
                "method": "llm",
                "processing_time_ms": 1245.6
            }
        }


class SentimentAnalysisRequest(BaseModel):
    """Request model for sentiment analysis"""
    texts: List[str] = Field(..., min_length=1, description="List of texts to analyze")
    locations: Optional[List[str]] = Field(None, description="Optional locations for each text")
    aggregate_by_location: bool = Field(default=True, description="Aggregate results by location")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Traffic is horrible in Koramangala today!",
                    "Love the new metro station in Whitefield",
                    "Power cuts again in Electronic City, very frustrating"
                ],
                "locations": ["Koramangala", "Whitefield", "Electronic City"],
                "aggregate_by_location": True
            }
        }


class SentimentResult(BaseModel):
    """Individual sentiment analysis result"""
    sentiment: str = Field(..., description="Sentiment label (positive, negative, neutral)")
    score: float = Field(..., ge=-1.0, le=1.0, description="Signed sentiment score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence")
    location: str = Field(..., description="Location (extracted or provided)")
    original_text: str = Field(..., description="Original text (first 100 chars)")


class LocationSentiment(BaseModel):
    """Aggregated sentiment for a location"""
    location: str = Field(..., description="Location name")
    sentiment: str = Field(..., description="Overall sentiment")
    score: float = Field(..., ge=-1.0, le=1.0, description="Average sentiment score")
    sample_size: int = Field(..., description="Number of samples")
    distribution: Dict[str, float] = Field(..., description="Sentiment distribution")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class SentimentAnalysisResponse(BaseModel):
    """Response model for sentiment analysis"""
    individual_results: Optional[List[SentimentResult]] = Field(None, description="Individual analysis results")
    location_aggregates: Optional[Dict[str, LocationSentiment]] = Field(None, description="Aggregated by location")
    city_wide: Optional[Dict[str, Any]] = Field(None, description="City-wide sentiment")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_analyzed: int = Field(..., description="Total texts analyzed")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "individual_results": [
                    {
                        "sentiment": "negative",
                        "score": -0.85,
                        "confidence": 0.92,
                        "location": "Koramangala",
                        "original_text": "Traffic is horrible in Koramangala today!"
                    }
                ],
                "location_aggregates": {
                    "Koramangala": {
                        "location": "Koramangala",
                        "sentiment": "negative",
                        "score": -0.67,
                        "sample_size": 25,
                        "distribution": {
                            "positive": 0.12,
                            "negative": 0.72,
                            "neutral": 0.16
                        },
                        "confidence": 0.85
                    }
                },
                "city_wide": {
                    "sentiment": "neutral",
                    "score": -0.15,
                    "distribution": {
                        "positive": 0.35,
                        "negative": 0.42,
                        "neutral": 0.23
                    }
                },
                "timestamp": "2025-10-11T15:00:00Z",
                "total_analyzed": 150,
                "processing_time_ms": 3452.1
            }
        }


class MoodMapRequest(BaseModel):
    """Request model for creating mood map"""
    texts: List[str] = Field(..., min_length=1, description="List of text posts")
    locations: Optional[List[str]] = Field(None, description="Optional locations for each text")
    timestamp: Optional[datetime] = Field(None, description="Timestamp for mood map")
    
    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "Great day at Cubbon Park!",
                    "Traffic nightmare on ORR",
                    "New cafe opened in Indiranagar, amazing!"
                ],
                "locations": ["Cubbon Park", "ORR", "Indiranagar"],
                "timestamp": "2025-10-11T15:00:00Z"
            }
        }


# ========================================
# UTILS INITIALIZATION
# ========================================

__all__ = [
    "EventType",
    "SeverityLevel",
    "AlertType",
    "Coordinates",
    "DetectedObject",
    "VisionAnalysisRequest",
    "VisionAnalysisResponse",
    "PredictionRequest",
    "AnomalyResult",
    "ForecastResult",
    "PredictionResponse",
    "HealthResponse",
    "ErrorResponse",
    "SummarizationRequest",
    "SummarizationResponse",
    "SentimentAnalysisRequest",
    "SentimentResult",
    "LocationSentiment",
    "SentimentAnalysisResponse",
    "MoodMapRequest",
]
