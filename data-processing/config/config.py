"""
Configuration Management for Data Processing
Person 2's configuration settings
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration for data processing pipeline"""
    
    # ============ Person 1's Output (Your Input) ============
    
    # Kafka Configuration (if Person 1 uses Kafka)
    KAFKA_BROKER: str = os.getenv("KAFKA_BROKER", "localhost:9092")
    KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "smartcitysense_events")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "data_processing_group")
    
    # Firebase Input (if Person 1 uses Firebase)
    FIREBASE_INPUT_COLLECTION: str = os.getenv("FIREBASE_INPUT_COLLECTION", "events")
    
    # ============ Your Output (Processed Data) ============
    
    # Firebase Output Configuration
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    FIREBASE_PRIVATE_KEY_PATH: str = os.getenv("FIREBASE_PRIVATE_KEY_PATH", "")
    FIREBASE_OUTPUT_COLLECTION: str = os.getenv("FIREBASE_OUTPUT_COLLECTION", "processed_events")
    
    # ============ External APIs ============
    
    # Google Maps for geocoding
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # ============ City Configuration ============
    
    CITY_CENTER_LAT: float = float(os.getenv("CITY_CENTER_LAT", "12.9716"))
    CITY_CENTER_LON: float = float(os.getenv("CITY_CENTER_LON", "77.5946"))
    CITY_RADIUS_KM: float = float(os.getenv("CITY_RADIUS_KM", "50"))
    
    # Bangalore Zones/Neighborhoods
    BANGALORE_ZONES = {
        "North Bangalore": {
            "neighborhoods": ["Hebbal", "Yelahanka", "Malleshwaram", "Sadashivanagar"],
            "center": (13.0358, 77.5970)
        },
        "South Bangalore": {
            "neighborhoods": ["Jayanagar", "JP Nagar", "Banashankari", "BTM Layout", "Silk Board"],
            "center": (12.9173, 77.6221)
        },
        "East Bangalore": {
            "neighborhoods": ["Whitefield", "Marathahalli", "Bellandur", "Sarjapur"],
            "center": (12.9698, 77.7500)
        },
        "West Bangalore": {
            "neighborhoods": ["Rajajinagar", "Vijayanagar", "Peenya"],
            "center": (12.9894, 77.5408)
        },
        "Central Bangalore": {
            "neighborhoods": ["MG Road", "Indiranagar", "Koramangala", "HSR Layout", "Electronic City"],
            "center": (12.9716, 77.5946)
        }
    }
    
    # ============ Deduplication Settings ============
    
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    TIME_WINDOW_MINUTES: int = int(os.getenv("TIME_WINDOW_MINUTES", "60"))
    DISTANCE_THRESHOLD_KM: float = float(os.getenv("DISTANCE_THRESHOLD_KM", "2"))
    
    # ============ Processing Settings ============
    
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "50"))
    PROCESSING_INTERVAL_SECONDS: int = int(os.getenv("PROCESSING_INTERVAL_SECONDS", "30"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    
    # ============ Logging ============
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ============ Performance ============
    
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    PARALLEL_PROCESSING: bool = os.getenv("PARALLEL_PROCESSING", "true").lower() == "true"
    NUM_WORKERS: int = int(os.getenv("NUM_WORKERS", "4"))
    
    # ============ Event Type Refinement ============
    
    EVENT_TYPE_MAPPING = {
        "traffic": {
            "accident": ["accident", "crash", "collision", "hit"],
            "congestion": ["jam", "traffic", "congestion", "slow", "heavy"],
            "road_closure": ["closed", "blocked", "closure", "blocked road"],
            "construction": ["construction", "repair", "work in progress"],
        },
        "civic": {
            "power_outage": ["power", "electricity", "outage", "blackout", "bescom"],
            "water_shortage": ["water", "shortage", "supply", "tanker"],
            "garbage": ["garbage", "waste", "trash", "collection"],
            "pothole": ["pothole", "road", "damage"],
            "drainage": ["drainage", "overflow", "sewage", "flood"],
        },
        "emergency": {
            "fire": ["fire", "burning", "smoke"],
            "medical": ["ambulance", "medical", "hospital", "emergency"],
            "crime": ["theft", "robbery", "crime", "police"],
        }
    }
    
    # ============ Tag Keywords ============
    
    TAG_KEYWORDS = {
        "rush_hour": ["morning", "evening", "rush", "peak"],
        "weather_related": ["rain", "flood", "storm", "weather"],
        "government": ["bbmp", "bescom", "bwssb", "bmtc"],
        "urgent": ["urgent", "critical", "emergency", "immediate"],
        "resolved": ["resolved", "cleared", "fixed", "completed"],
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        # At minimum, need either Kafka or Firebase input
        has_kafka = bool(cls.KAFKA_BROKER and cls.KAFKA_TOPIC)
        has_firebase_input = bool(cls.FIREBASE_PROJECT_ID)
        
        if not (has_kafka or has_firebase_input):
            print("⚠️  Warning: No input source configured (Kafka or Firebase)")
            return False
        
        # Need Firebase for output
        if not cls.FIREBASE_PROJECT_ID:
            print("⚠️  Warning: Firebase not configured for storage")
            return False
        
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Print configuration status"""
        print("=" * 60)
        print("📋 Person 2 - Data Processing Configuration")
        print("=" * 60)
        
        print("\n🔌 INPUT SOURCES:")
        print(f"  Kafka: {'✓ Configured' if cls.KAFKA_BROKER else '✗ Not configured'}")
        if cls.KAFKA_BROKER:
            print(f"    Broker: {cls.KAFKA_BROKER}")
            print(f"    Topic: {cls.KAFKA_TOPIC}")
        print(f"  Firebase Input: {'✓ Configured' if cls.FIREBASE_PROJECT_ID else '✗ Not configured'}")
        
        print("\n💾 OUTPUT STORAGE:")
        print(f"  Firebase: {'✓ Configured' if cls.FIREBASE_PROJECT_ID else '✗ Not configured'}")
        if cls.FIREBASE_PROJECT_ID:
            print(f"    Collection: {cls.FIREBASE_OUTPUT_COLLECTION}")
        
        print("\n🗺️  GEOCODING:")
        print(f"  Google Maps: {'✓ Configured' if cls.GOOGLE_MAPS_API_KEY else '✗ Not configured'}")
        
        print("\n⚙️  PROCESSING:")
        print(f"  Batch Size: {cls.BATCH_SIZE}")
        print(f"  Interval: {cls.PROCESSING_INTERVAL_SECONDS}s")
        print(f"  Similarity Threshold: {cls.SIMILARITY_THRESHOLD}")
        print(f"  Time Window: {cls.TIME_WINDOW_MINUTES} min")
        print(f"  Distance Threshold: {cls.DISTANCE_THRESHOLD_KM} km")
        
        print("\n🚀 PERFORMANCE:")
        print(f"  Caching: {'Enabled' if cls.ENABLE_CACHING else 'Disabled'}")
        print(f"  Parallel Processing: {'Enabled' if cls.PARALLEL_PROCESSING else 'Disabled'}")
        if cls.PARALLEL_PROCESSING:
            print(f"  Workers: {cls.NUM_WORKERS}")
        
        print("=" * 60)


if __name__ == "__main__":
    Config.validate()
    Config.print_config()
