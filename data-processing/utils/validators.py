"""
Data Validators
Validation utilities for event data
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from utils.logger import setup_logger

logger = setup_logger(__name__)


class Coordinates(BaseModel):
    """Geographic coordinates"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")


class ProcessedEvent(BaseModel):
    """
    Schema for processed events (output from Person 2)
    This is the enhanced version of what Person 1 provides
    """
    # Original fields from Person 1
    id: str
    type: str
    source: str
    description: str
    location: str
    timestamp: datetime
    severity: str
    tags: List[str] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Person 2's enhancements
    subtype: Optional[str] = None
    full_address: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    zone: Optional[str] = None
    neighborhood: Optional[str] = None
    urgency: Optional[str] = None
    duplicate_of: Optional[str] = None
    similar_events: List[str] = Field(default_factory=list)
    verified: bool = False
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    processed_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('type')
    def validate_type(cls, v):
        """Validate event type"""
        valid_types = ['traffic', 'civic', 'cultural', 'emergency', 'weather', 'other']
        if v not in valid_types:
            logger.warning(f"Unknown event type: {v}")
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate severity level"""
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v not in valid_severities:
            logger.warning(f"Unknown severity: {v}, defaulting to 'medium'")
            return 'medium'
        return v
    
    @validator('urgency')
    def validate_urgency(cls, v):
        """Validate urgency level"""
        if v is not None:
            valid_urgencies = ['can_wait', 'needs_attention', 'critical', 'resolved']
            if v not in valid_urgencies:
                logger.warning(f"Unknown urgency: {v}")
        return v


class DataValidator:
    """
    Validates and cleans event data
    """
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Validate coordinates are within Bangalore bounds
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            True if valid, False otherwise
        """
        # Bangalore approximate bounds
        LAT_MIN, LAT_MAX = 12.7, 13.2
        LON_MIN, LON_MAX = 77.3, 77.9
        
        if not (LAT_MIN <= lat <= LAT_MAX):
            return False
        if not (LON_MIN <= lon <= LON_MAX):
            return False
        
        return True
    
    @staticmethod
    def validate_timestamp(timestamp: datetime) -> bool:
        """
        Validate timestamp is reasonable
        
        Args:
            timestamp: Event timestamp
        
        Returns:
            True if valid, False otherwise
        """
        now = datetime.utcnow()
        
        # Not too far in the past (> 1 week)
        if (now - timestamp).days > 7:
            logger.warning(f"Timestamp too old: {timestamp}")
            return False
        
        # Not in the future
        if timestamp > now:
            logger.warning(f"Timestamp in future: {timestamp}")
            return False
        
        return True
    
    @staticmethod
    def calculate_quality_score(event: Dict[str, Any]) -> float:
        """
        Calculate quality score for an event (0-1)
        
        Higher score = better quality
        
        Factors:
        - Has coordinates: +0.3
        - Has detailed description: +0.2
        - Has zone/neighborhood: +0.2
        - Has multiple tags: +0.1
        - Recent timestamp: +0.1
        - Has verification: +0.1
        
        Args:
            event: Event dictionary
        
        Returns:
            Quality score (0-1)
        """
        score = 0.0
        
        # Has coordinates
        if event.get('coordinates'):
            score += 0.3
        
        # Has detailed description (> 20 chars)
        desc = event.get('description', '')
        if len(desc) > 20:
            score += 0.2
        
        # Has zone and neighborhood
        if event.get('zone') and event.get('neighborhood'):
            score += 0.2
        
        # Has multiple tags
        tags = event.get('tags', [])
        if len(tags) >= 3:
            score += 0.1
        
        # Recent timestamp (< 1 hour old)
        if event.get('timestamp'):
            try:
                ts = event['timestamp']
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                age_hours = (datetime.utcnow() - ts).total_seconds() / 3600
                if age_hours < 1:
                    score += 0.1
            except:
                pass
        
        # Has verification
        if event.get('verified'):
            score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def clean_description(description: str) -> str:
        """
        Clean and normalize description text
        
        Args:
            description: Raw description
        
        Returns:
            Cleaned description
        """
        # Remove extra whitespace
        description = ' '.join(description.split())
        
        # Capitalize first letter
        if description:
            description = description[0].upper() + description[1:]
        
        # Ensure ends with period
        if description and not description[-1] in ['.', '!', '?']:
            description += '.'
        
        return description
    
    @staticmethod
    def validate_event(event: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate event has required fields
        
        Args:
            event: Event dictionary
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required = ['id', 'type', 'source', 'description', 'timestamp']
        for field in required:
            if field not in event:
                errors.append(f"Missing required field: {field}")
        
        # Validate coordinates if present
        if event.get('coordinates'):
            coords = event['coordinates']
            if not DataValidator.validate_coordinates(
                coords.get('lat', 0), 
                coords.get('lon', 0)
            ):
                errors.append("Coordinates outside Bangalore bounds")
        
        # Validate timestamp if present
        if event.get('timestamp'):
            try:
                ts = event['timestamp']
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                if not DataValidator.validate_timestamp(ts):
                    errors.append("Invalid timestamp")
            except:
                errors.append("Cannot parse timestamp")
        
        return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Test validation
    print("Testing Data Validator\n" + "="*50)
    
    sample_event = {
        'id': 'test123',
        'type': 'traffic',
        'source': 'twitter',
        'description': 'Heavy traffic on MG Road',
        'timestamp': datetime.utcnow(),
        'coordinates': {'lat': 12.9760, 'lon': 77.6061},
        'zone': 'Central Bangalore',
        'neighborhood': 'MG Road',
        'tags': ['traffic', 'congestion', 'mgroad'],
        'verified': True
    }
    
    validator = DataValidator()
    
    # Validate
    is_valid, errors = validator.validate_event(sample_event)
    print(f"\nValidation: {'✓ PASS' if is_valid else '✗ FAIL'}")
    if errors:
        print(f"Errors: {errors}")
    
    # Quality score
    score = validator.calculate_quality_score(sample_event)
    print(f"\nQuality Score: {score:.2f}")
    
    # Validate coordinates
    valid = validator.validate_coordinates(12.9760, 77.6061)
    print(f"Coordinates Valid: {'✓ Yes' if valid else '✗ No'}")
