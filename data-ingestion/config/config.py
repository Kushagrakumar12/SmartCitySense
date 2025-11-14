"""
Configuration Management for Data Ingestion
Loads environment variables and provides configuration access
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration management"""
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Twitter/X
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # Reddit
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "CityPulseAI/1.0")
    
    # Instagram
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    
    # Civic Portal
    CIVIC_PORTAL_API_KEY: str = os.getenv("CIVIC_PORTAL_API_KEY", "")
    CIVIC_PORTAL_BASE_URL: str = os.getenv(
        "CIVIC_PORTAL_BASE_URL", 
        "https://api.civicportal.gov/v1"
    )
    
    # Kafka
    KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "localhost:9092")
    KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "citypulse_events")
    
    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY_PATH: str = os.getenv("FIREBASE_PRIVATE_KEY_PATH", "")
    FIREBASE_COLLECTION: str = os.getenv("FIREBASE_COLLECTION", "citypulse_events")
    
    # General
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    POLLING_INTERVAL_SECONDS: int = int(os.getenv("POLLING_INTERVAL_SECONDS", "300"))
    
    # Location (Bangalore/Bengaluru default)
    BANGALORE_LAT: float = float(os.getenv("BANGALORE_LAT", "12.9716"))
    BANGALORE_LON: float = float(os.getenv("BANGALORE_LON", "77.5946"))
    CITY_RADIUS_KM: float = float(os.getenv("CITY_RADIUS_KM", "50"))
    
    # Search Keywords for Social Media
    CITY_KEYWORDS = [
        "bangalore", "bengaluru", "blr", 
        "#bangalore", "#bengaluru", "#nammabengaluru"
    ]
    
    TRAFFIC_KEYWORDS = [
        "traffic", "jam", "congestion", "accident", "road block",
        "heavy traffic", "signal", "flyover"
    ]
    
    CIVIC_KEYWORDS = [
        "power cut", "water shortage", "pothole", "garbage",
        "street light", "drainage", "BBMP", "BESCOM"
    ]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required_keys = [
            cls.KAFKA_BROKER,
        ]
        
        missing = [key for key in required_keys if not key]
        
        if missing:
            print(f"⚠️  Warning: Missing configuration for {len(missing)} items")
            return False
        
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Print configuration status (without exposing secrets)"""
        print("=" * 50)
        print("📋 Configuration Status")
        print("=" * 50)
        print(f"Google Maps API: {'✓ Configured' if cls.GOOGLE_MAPS_API_KEY else '✗ Missing'}")
        print(f"Twitter API: {'✓ Configured' if cls.TWITTER_BEARER_TOKEN else '✗ Missing'}")
        print(f"Reddit API: {'✓ Configured' if cls.REDDIT_CLIENT_ID else '✗ Missing'}")
        print(f"Civic Portal: {'✓ Configured' if cls.CIVIC_PORTAL_API_KEY else '✗ Missing'}")
        print(f"Kafka Broker: {cls.KAFKA_BROKER}")
        print(f"Kafka Topic: {cls.KAFKA_TOPIC}")
        print(f"Polling Interval: {cls.POLLING_INTERVAL_SECONDS}s")
        print(f"City Center: {cls.BANGALORE_LAT}, {cls.BANGALORE_LON}")
        print("=" * 50)


if __name__ == "__main__":
    Config.validate()
    Config.print_config()
