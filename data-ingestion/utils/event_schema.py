"""
Event Schema Definition
Standardized event structure for all data sources
"""
from datetime import datetime
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
import uuid


EventType = Literal["traffic", "civic", "cultural", "emergency", "weather", "other", "social"]
EventSource = Literal["google_maps", "twitter", "reddit", "instagram", "civic_portal", "user_report", "news"]
SeverityLevel = Literal["low", "medium", "high", "critical"]


class Coordinates(BaseModel):
    """Geographic coordinates"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class Event(BaseModel):
    """Standardized event schema for SmartCitySense"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    type: EventType = Field(..., description="Event category")
    source: EventSource = Field(..., description="Data source")
    description: str = Field(..., description="Event description")
    location: str = Field(..., description="Human-readable location")
    coordinates: Optional[Coordinates] = Field(None, description="Lat/lon coordinates")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    severity: SeverityLevel = Field(default="low", description="Event severity")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Original API response")
    tags: list[str] = Field(default_factory=list, description="Additional tags")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Kafka/Firebase"""
        data = self.model_dump()
        data['timestamp'] = self.timestamp.isoformat()
        if self.coordinates:
            data['coordinates'] = {
                'lat': self.coordinates.lat,
                'lon': self.coordinates.lon
            }
        return data


# Example usage and validation
if __name__ == "__main__":
    # Sample event
    event = Event(
        type="traffic",
        source="twitter",
        description="Heavy traffic on MG Road due to accident",
        location="MG Road, Bangalore",
        coordinates=Coordinates(lat=12.9716, lon=77.5946),
        severity="high",
        tags=["accident", "mgroad", "traffic"]
    )
    
    print("Sample Event:")
    print(event.model_dump_json(indent=2))
