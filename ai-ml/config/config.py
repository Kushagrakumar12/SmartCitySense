"""
Configuration Management for AI/ML Module
Loads environment variables and provides centralized config access
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import torch

# Load environment variables from .env file
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")


class FirebaseConfig(BaseModel):
    """Firebase/Firestore configuration"""
    credentials_path: str = Field(default="./firebase-credentials.json")
    project_id: str = Field(default="smartcitysense")
    events_collection: str = Field(default="events")
    predictions_collection: str = Field(default="predictions")
    alerts_collection: str = Field(default="alerts")


class VisionConfig(BaseModel):
    """Vision model configuration"""
    yolo_model_path: str = Field(default="./models/yolov8n.pt")
    yolo_model_size: str = Field(default="n")  # n, s, m, l, x
    confidence_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    max_image_size: int = Field(default=1280)
    max_video_duration: int = Field(default=30)
    max_video_frames: int = Field(default=60)


class PredictiveConfig(BaseModel):
    """Predictive modeling configuration"""
    anomaly_model_path: str = Field(default="./models/isolation_forest.pkl")
    prophet_model_path: str = Field(default="./models/prophet_model.pkl")
    contamination: float = Field(default=0.1, ge=0.01, le=0.5)
    n_estimators: int = Field(default=100)
    forecast_periods: int = Field(default=24)
    anomaly_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    prediction_window_minutes: int = Field(default=15)
    min_reports_for_anomaly: int = Field(default=5)
    alert_cooldown_minutes: int = Field(default=30)


class TextConfig(BaseModel):
    """Text processing configuration (Member B1)"""
    # Summarization settings
    summarization_llm_provider: str = Field(default="gemini")  # gemini or openai
    summarization_model_name: str = Field(default="gemini-1.5-flash")
    google_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    max_reports_per_summary: int = Field(default=50)
    summary_max_length: int = Field(default=200)
    
    # Sentiment analysis settings
    sentiment_model_name: str = Field(default="distilbert-base-uncased-finetuned-sst-2-english")
    enable_multilingual: bool = Field(default=False)
    batch_size: int = Field(default=32)
    
    # Firestore collections
    summarized_events_collection: str = Field(default="summarized_events")
    mood_map_collection: str = Field(default="mood_map")


class APIConfig(BaseModel):
    """API server configuration"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8001)
    workers: int = Field(default=4)
    reload: bool = Field(default=True)
    log_level: str = Field(default="info")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    max_upload_size_mb: int = Field(default=10)
    backend_api_url: str = Field(default="http://localhost:8000")
    backend_api_key: Optional[str] = Field(default=None)


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO")
    file: str = Field(default="./logs/ai_ml.log")
    rotation: str = Field(default="10 MB")
    retention: str = Field(default="30 days")


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.mock_mode = os.getenv("MOCK_MODE", "False").lower() == "true"
        self.save_debug_images = os.getenv("SAVE_DEBUG_IMAGES", "True").lower() == "true"
        
        # Sub-configurations
        self.firebase = self._load_firebase_config()
        self.vision = self._load_vision_config()
        self.predictive = self._load_predictive_config()
        self.text = self._load_text_config()
        self.api = self._load_api_config()
        self.logging = self._load_logging_config()
        
        # Hardware detection
        self.use_gpu = self._detect_gpu()
        self.device = "cuda" if self.use_gpu else "cpu"
        
    def _load_firebase_config(self) -> FirebaseConfig:
        """Load Firebase configuration"""
        return FirebaseConfig(
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json"),
            project_id=os.getenv("FIREBASE_PROJECT_ID", "smartcitysense"),
            events_collection=os.getenv("FIRESTORE_COLLECTION_EVENTS", "events"),
            predictions_collection=os.getenv("FIRESTORE_COLLECTION_PREDICTIONS", "predictions"),
            alerts_collection=os.getenv("FIRESTORE_COLLECTION_ALERTS", "alerts"),
        )
    
    def _load_vision_config(self) -> VisionConfig:
        """Load vision model configuration"""
        return VisionConfig(
            yolo_model_path=os.getenv("YOLO_MODEL_PATH", "./models/yolov8n.pt"),
            yolo_model_size=os.getenv("YOLO_MODEL_SIZE", "n"),
            confidence_threshold=float(os.getenv("VISION_CONFIDENCE_THRESHOLD", "0.65")),
            iou_threshold=float(os.getenv("VISION_IOU_THRESHOLD", "0.45")),
            max_image_size=int(os.getenv("MAX_IMAGE_SIZE", "1280")),
            max_video_duration=int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "30")),
            max_video_frames=int(os.getenv("MAX_VIDEO_FRAMES", "60")),
        )
    
    def _load_predictive_config(self) -> PredictiveConfig:
        """Load predictive model configuration"""
        return PredictiveConfig(
            anomaly_model_path=os.getenv("ANOMALY_MODEL_PATH", "./models/isolation_forest.pkl"),
            prophet_model_path=os.getenv("PROPHET_MODEL_PATH", "./models/prophet_model.pkl"),
            contamination=float(os.getenv("ANOMALY_CONTAMINATION", "0.1")),
            n_estimators=int(os.getenv("ANOMALY_N_ESTIMATORS", "100")),
            forecast_periods=int(os.getenv("FORECAST_PERIODS", "24")),
            anomaly_threshold=float(os.getenv("ANOMALY_THRESHOLD", "0.85")),
            prediction_window_minutes=int(os.getenv("PREDICTION_WINDOW_MINUTES", "15")),
            min_reports_for_anomaly=int(os.getenv("MIN_REPORTS_FOR_ANOMALY", "5")),
            alert_cooldown_minutes=int(os.getenv("ALERT_COOLDOWN_MINUTES", "30")),
        )
    
    def _load_text_config(self) -> TextConfig:
        """Load text processing configuration"""
        return TextConfig(
            summarization_llm_provider=os.getenv("SUMMARIZATION_LLM_PROVIDER", "gemini"),
            summarization_model_name=os.getenv("SUMMARIZATION_MODEL_NAME", "gemini-1.5-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            max_reports_per_summary=int(os.getenv("MAX_REPORTS_PER_SUMMARY", "50")),
            summary_max_length=int(os.getenv("SUMMARY_MAX_LENGTH", "200")),
            sentiment_model_name=os.getenv("SENTIMENT_MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english"),
            enable_multilingual=os.getenv("ENABLE_MULTILINGUAL", "False").lower() == "true",
            batch_size=int(os.getenv("TEXT_BATCH_SIZE", "32")),
            summarized_events_collection=os.getenv("FIRESTORE_COLLECTION_SUMMARIZED_EVENTS", "summarized_events"),
            mood_map_collection=os.getenv("FIRESTORE_COLLECTION_MOOD_MAP", "mood_map"),
        )
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration"""
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]
        
        return APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8001")),
            workers=int(os.getenv("API_WORKERS", "4")),
            reload=os.getenv("API_RELOAD", "True").lower() == "true",
            log_level=os.getenv("API_LOG_LEVEL", "info"),
            cors_origins=cors_origins,
            max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")),
            backend_api_url=os.getenv("BACKEND_API_URL", "http://localhost:8000"),
            backend_api_key=os.getenv("BACKEND_API_KEY"),
        )
    
    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration"""
        return LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file=os.getenv("LOG_FILE", "./logs/ai_ml.log"),
            rotation=os.getenv("LOG_ROTATION", "10 MB"),
            retention=os.getenv("LOG_RETENTION", "30 days"),
        )
    
    def _detect_gpu(self) -> bool:
        """Detect GPU availability"""
        use_gpu_env = os.getenv("USE_GPU", "True").lower() == "true"
        has_cuda = torch.cuda.is_available()
        return use_gpu_env and has_cuda
    
    def get_model_path(self, model_name: str) -> Path:
        """Get absolute path for a model file"""
        return BASE_DIR / "models" / model_name
    
    def get_log_path(self) -> Path:
        """Get absolute path for log directory"""
        return BASE_DIR / "logs"
    
    def print_config(self):
        """Print current configuration for debugging"""
        print("=" * 60)
        print("🤖 AI/ML Module Configuration")
        print("=" * 60)
        print(f"Environment: {self.environment}")
        print(f"Device: {self.device} (GPU Available: {self.use_gpu})")
        print(f"Mock Mode: {self.mock_mode}")
        print()
        print("Firebase:")
        print(f"  Project ID: {self.firebase.project_id}")
        print(f"  Events Collection: {self.firebase.events_collection}")
        print()
        print("Vision:")
        print(f"  Model: YOLOv{self.vision.yolo_model_size}")
        print(f"  Confidence: {self.vision.confidence_threshold}")
        print(f"  Max Image Size: {self.vision.max_image_size}px")
        print()
        print("Predictive:")
        print(f"  Anomaly Threshold: {self.predictive.anomaly_threshold}")
        print(f"  Forecast Periods: {self.predictive.forecast_periods}h")
        print()
        print("Text Intelligence:")
        print(f"  LLM Provider: {self.text.summarization_llm_provider}")
        print(f"  Model: {self.text.summarization_model_name}")
        print(f"  Sentiment Model: {self.text.sentiment_model_name}")
        print(f"  Multilingual: {self.text.enable_multilingual}")
        print()
        print("API:")
        print(f"  Host: {self.api.host}:{self.api.port}")
        print(f"  Workers: {self.api.workers}")
        print("=" * 60)


# Global configuration instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    config.print_config()
