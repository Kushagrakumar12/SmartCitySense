"""
Configuration Management
Loads environment variables and provides app configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings"""
    
    # App Config
    APP_NAME: str = "SmartCitySense Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "../data-ingestion/firebase-credentials.json"
    FIREBASE_DATABASE_URL: Optional[str] = None
    FIREBASE_STORAGE_BUCKET: Optional[str] = None
    
    # FCM (Firebase Cloud Messaging)
    FCM_SERVER_KEY: Optional[str] = None
    
    # AI/ML Service URLs
    AI_ML_SERVICE_URL: str = "http://localhost:8001"
    SUMMARIZATION_ENDPOINT: str = "/api/summarize"
    VISION_ANALYSIS_ENDPOINT: str = "/api/analyze/image"
    SENTIMENT_ENDPOINT: str = "/api/sentiment"
    ANOMALY_DETECTION_ENDPOINT: str = "/api/anomaly/detect"
    
    # Data Processing Service
    DATA_PROCESSING_URL: str = "http://localhost:8002"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",  # Frontend dev server
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Geospatial
    DEFAULT_RADIUS_KM: float = 5.0
    MAX_RADIUS_KM: float = 50.0
    
    # Notification Settings
    NOTIFICATION_BATCH_SIZE: int = 500
    NOTIFICATION_RETRY_ATTEMPTS: int = 3
    
    # Cache Settings
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Redis (for background jobs and caching)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
