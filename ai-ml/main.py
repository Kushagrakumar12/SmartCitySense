"""
Main FastAPI Application for AI/ML Services
REST API endpoints for vision analysis and predictive modeling
"""

import time
import uuid
from datetime import datetime
from typing import Optional
from pathlib import Path
import tempfile
import aiofiles
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.config import config
from utils.logger import get_logger
from utils.schemas import (
    VisionAnalysisRequest, VisionAnalysisResponse,
    PredictionRequest, PredictionResponse,
    HealthResponse, ErrorResponse,
    EventType, SeverityLevel, AlertType,
    AnomalyResult, ForecastResult,
    # Text processing schemas (Member B1)
    SummarizationRequest, SummarizationResponse,
    SentimentAnalysisRequest, SentimentAnalysisResponse,
    MoodMapRequest
)
from utils.firebase_client import firebase_client
from vision.image_classifier import ImageClassifier
from vision.video_analyzer import VideoAnalyzer
from predictive.anomaly_detector import AnomalyDetector
from predictive.timeseries_model import TimeSeriesForecaster
# Text processing modules (Member B1)
from text.text_summarizer import TextSummarizer
from text.sentiment_analyzer import SentimentAnalyzer

logger = get_logger("api")

# ========================================
# LIFESPAN EVENT HANDLER
# ========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info("="*60)
    logger.info("🚀 Starting SmartCitySense - AI/ML API Server")
    logger.info("="*60)
    config.print_config()
    
    # Optionally pre-load models
    # get_vision_classifier()
    # get_anomaly_detector()
    
    logger.success("✅ API Server ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API server...")


# Initialize FastAPI app
app = FastAPI(
    title="SmartCitySense - AI/ML API",
    description="Vision analysis and predictive modeling for city events",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models (lazy loading)
vision_classifier: Optional[ImageClassifier] = None
video_analyzer: Optional[VideoAnalyzer] = None
anomaly_detector: Optional[AnomalyDetector] = None
time_series_forecaster: Optional[TimeSeriesForecaster] = None
# Text processing models (Member B1)
text_summarizer: Optional[TextSummarizer] = None
sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_vision_classifier() -> ImageClassifier:
    """Get or initialize image classifier"""
    global vision_classifier
    if vision_classifier is None:
        logger.info("Initializing Image Classifier...")
        vision_classifier = ImageClassifier()
    return vision_classifier


def get_video_analyzer() -> VideoAnalyzer:
    """Get or initialize video analyzer"""
    global video_analyzer
    if video_analyzer is None:
        logger.info("Initializing Video Analyzer...")
        video_analyzer = VideoAnalyzer(get_vision_classifier())
    return video_analyzer


def get_anomaly_detector() -> AnomalyDetector:
    """Get or initialize anomaly detector"""
    global anomaly_detector
    if anomaly_detector is None:
        logger.info("Initializing Anomaly Detector...")
        anomaly_detector = AnomalyDetector()
    return anomaly_detector


def get_time_series_forecaster() -> TimeSeriesForecaster:
    """Get or initialize time series forecaster"""
    global time_series_forecaster
    if time_series_forecaster is None:
        logger.info("Initializing Time Series Forecaster...")
        time_series_forecaster = TimeSeriesForecaster()
    return time_series_forecaster


def get_text_summarizer() -> TextSummarizer:
    """Get or initialize text summarizer (Member B1)"""
    global text_summarizer
    if text_summarizer is None:
        logger.info("Initializing Text Summarizer...")
        text_summarizer = TextSummarizer()
    return text_summarizer


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or initialize sentiment analyzer (Member B1)"""
    global sentiment_analyzer
    if sentiment_analyzer is None:
        logger.info("Initializing Sentiment Analyzer...")
        sentiment_analyzer = SentimentAnalyzer()
    return sentiment_analyzer


# ========================================
# HEALTH & STATUS ENDPOINTS
# ========================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded={
            "vision": vision_classifier is not None,
            "video": video_analyzer is not None,
            "anomaly": anomaly_detector is not None,
            "forecast": time_series_forecaster is not None,
            "summarization": text_summarizer is not None,
            "sentiment": sentiment_analyzer is not None,
        },
        gpu_available=config.use_gpu
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        models_loaded={
            "vision": vision_classifier is not None,
            "video": video_analyzer is not None,
            "anomaly": anomaly_detector is not None,
            "forecast": time_series_forecaster is not None,
            "summarization": text_summarizer is not None,
            "sentiment": sentiment_analyzer is not None,
        },
        gpu_available=config.use_gpu
    )


# ========================================
# VISION ANALYSIS ENDPOINTS
# ========================================

@app.post("/ai/vision/image", response_model=VisionAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Analyze uploaded image for event detection
    
    - **file**: Image file (JPG, PNG)
    - **location**: Optional location description
    - **latitude**: Optional latitude coordinate
    - **longitude**: Optional longitude coordinate
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Received image analysis request")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size
        max_size = config.api.max_upload_size_mb * 1024 * 1024
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
        
        async with aiofiles.open(temp_file.name, 'wb') as f:
            content = await file.read()
            
            if len(content) > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {config.api.max_upload_size_mb}MB"
                )
            
            await f.write(content)
        
        # Analyze image
        classifier = get_vision_classifier()
        result = classifier.classify_image(temp_file.name, save_debug=config.save_debug_images)
        
        # Clean up temp file
        Path(temp_file.name).unlink(missing_ok=True)
        
        # Save to Firebase in background
        if background_tasks:
            background_tasks.add_task(
                save_vision_result_to_firebase,
                result.model_dump(),
                location,
                latitude,
                longitude
            )
        
        logger.success(f"[{request_id}] Image analyzed: {result.event_type.value}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/vision/video", response_model=VisionAnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    sample_rate: Optional[int] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Analyze uploaded video for event detection
    
    - **file**: Video file (MP4, AVI, MOV)
    - **location**: Optional location description
    - **latitude**: Optional latitude coordinate
    - **longitude**: Optional longitude coordinate
    - **sample_rate**: Frame sampling rate (extract every Nth frame)
    """
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"[{request_id}] Received video analysis request")
        
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
        
        async with aiofiles.open(temp_file.name, 'wb') as f:
            content = await file.read()
            
            max_size = config.api.max_upload_size_mb * 1024 * 1024
            if len(content) > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {config.api.max_upload_size_mb}MB"
                )
            
            await f.write(content)
        
        # Analyze video
        analyzer = get_video_analyzer()
        result = analyzer.analyze_video(temp_file.name, sample_rate=sample_rate)
        
        # Clean up temp file
        Path(temp_file.name).unlink(missing_ok=True)
        
        # Save to Firebase in background
        if background_tasks:
            background_tasks.add_task(
                save_vision_result_to_firebase,
                result.model_dump(),
                location,
                latitude,
                longitude
            )
        
        logger.success(f"[{request_id}] Video analyzed: {result.event_type.value}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Video analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# PREDICTIVE ANALYSIS ENDPOINTS
# ========================================

@app.post("/ai/predict/anomaly", response_model=PredictionResponse)
async def detect_anomaly(request: PredictionRequest, background_tasks: BackgroundTasks = None):
    """
    Detect anomalies in recent event patterns
    
    - **location**: Optional location filter
    - **event_types**: Optional list of event types to analyze
    - **time_window_minutes**: Time window for analysis (default: 15)
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Anomaly detection request")
        
        detector = get_anomaly_detector()
        
        # Analyze each event type or all if not specified
        event_types = request.event_types or [EventType.TRAFFIC, EventType.POWER_OUTAGE]
        
        all_results = []
        recommendations = []
        affected_areas = set()
        
        for event_type in event_types:
            anomaly_result = detector.detect_anomaly(
                event_type=event_type.value,
                location=request.location,
                time_window_minutes=request.time_window_minutes
            )
            
            if anomaly_result.is_anomaly:
                all_results.append(anomaly_result)
                
                # Generate alert message
                alert_msg, alert_type = detector.generate_alert_message(
                    anomaly_result,
                    event_type.value,
                    request.location
                )
                
                recommendations.append(alert_msg)
                
                if request.location:
                    affected_areas.add(request.location)
        
        # Determine overall severity
        if all_results:
            severity = max([r.severity for r in all_results],
                          key=lambda s: [SeverityLevel.LOW, SeverityLevel.MEDIUM,
                                        SeverityLevel.HIGH, SeverityLevel.CRITICAL].index(s))
            most_anomalous = max(all_results, key=lambda r: r.anomaly_score)
        else:
            severity = SeverityLevel.LOW
            most_anomalous = None
        
        processing_time = (time.time() - start_time) * 1000
        
        response = PredictionResponse(
            alert=recommendations[0] if recommendations else None,
            alert_type=AlertType.ANOMALY if all_results else None,
            severity=severity,
            anomaly_result=most_anomalous,
            recommendations=recommendations,
            affected_areas=list(affected_areas),
            processing_time_ms=processing_time
        )
        
        # Save alert to Firebase if anomaly detected
        if all_results and background_tasks:
            background_tasks.add_task(save_alert_to_firebase, response.model_dump())
        
        logger.success(f"[{request_id}] Anomaly detection complete: {len(all_results)} anomalies found")
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/predict/forecast", response_model=PredictionResponse)
async def forecast_events(request: PredictionRequest):
    """
    Forecast future event patterns
    
    - **event_types**: List of event types to forecast
    - **forecast_hours**: Hours to forecast ahead (default: 24)
    - **location**: Optional location filter
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Forecast request for {request.forecast_hours} hours")
        
        forecaster = get_time_series_forecaster()
        
        # Forecast each event type
        event_types = request.event_types or [EventType.TRAFFIC]
        all_forecasts = []
        recommendations = []
        
        for event_type in event_types:
            forecast_results = forecaster.forecast(
                event_type=event_type.value,
                periods=request.forecast_hours
            )
            
            if forecast_results:
                all_forecasts.extend(forecast_results)
                
                # Check for peaks in forecast
                max_forecast = max(forecast_results, key=lambda f: f.predicted_value)
                if max_forecast.predicted_value > 10:  # Threshold
                    recommendations.append(
                        f"High {event_type.value} activity predicted around {max_forecast.forecast_timestamp.strftime('%H:%M')}"
                    )
        
        processing_time = (time.time() - start_time) * 1000
        
        response = PredictionResponse(
            alert=None,
            alert_type=AlertType.FORECAST if all_forecasts else None,
            severity=SeverityLevel.LOW,
            forecast_results=all_forecasts[:24],  # Limit to 24 hours
            recommendations=recommendations,
            affected_areas=[request.location] if request.location else [],
            processing_time_ms=processing_time
        )
        
        logger.success(f"[{request_id}] Forecast generated: {len(all_forecasts)} data points")
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Forecasting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# TRAINING ENDPOINTS (ADMIN)
# ========================================

@app.post("/ai/train/anomaly")
async def train_anomaly_model():
    """Train anomaly detection model on historical data"""
    try:
        detector = get_anomaly_detector()
        detector.train()
        return {"status": "success", "message": "Anomaly model trained successfully"}
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/train/forecast/{event_type}")
async def train_forecast_model(event_type: str):
    """Train forecast model for specific event type"""
    try:
        forecaster = get_time_series_forecaster()
        forecaster.train(event_type)
        return {"status": "success", "message": f"Forecast model trained for {event_type}"}
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# TEXT PROCESSING ENDPOINTS (Member B1)
# ========================================

@app.post("/ai/summarize", response_model=SummarizationResponse)
async def summarize_reports(
    request: SummarizationRequest,
    background_tasks: BackgroundTasks
):
    """
    Summarize multiple text reports into one coherent summary
    
    - Combines related reports about the same incident
    - Uses LLM (Gemini/GPT) for intelligent summarization
    - Falls back to template-based summarization if needed
    - Stores results in Firebase 'summarized_events' collection
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Summarization request: {len(request.reports)} reports, type={request.event_type}")
        
        # Get summarizer
        summarizer = get_text_summarizer()
        
        # Perform summarization
        result = summarizer.summarize(
            reports=request.reports,
            event_type=request.event_type,
            location=request.location,
            timestamp=request.timestamp,
            use_llm=request.use_llm
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        result['processing_time_ms'] = processing_time
        
        # Save to Firebase in background
        background_tasks.add_task(
            firebase_client.save_summarized_event,
            result
        )
        
        logger.success(f"[{request_id}] Summarization complete: {result['summary'][:50]}...")
        
        return SummarizationResponse(**result)
        
    except Exception as e:
        logger.error(f"[{request_id}] Summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/sentiment", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze sentiment of text posts
    
    - Classifies sentiment as positive, negative, or neutral
    - Aggregates results by location for mood mapping
    - Provides city-wide sentiment overview
    - Supports batch processing of multiple texts
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Sentiment analysis request: {len(request.texts)} texts")
        
        # Get analyzer
        analyzer = get_sentiment_analyzer()
        
        # Batch analyze
        individual_results = analyzer.batch_analyze(
            texts=request.texts,
            locations=request.locations
        )
        
        # Prepare response
        response_data = {
            "timestamp": datetime.utcnow(),
            "total_analyzed": len(request.texts),
            "processing_time_ms": (time.time() - start_time) * 1000
        }
        
        # Add individual results
        if not request.aggregate_by_location:
            from utils.schemas import SentimentResult
            response_data["individual_results"] = [
                SentimentResult(**result) for result in individual_results
            ]
        
        # Aggregate by location if requested
        if request.aggregate_by_location:
            aggregated = analyzer.aggregate_by_location(individual_results)
            
            from utils.schemas import LocationSentiment
            response_data["location_aggregates"] = {
                loc: LocationSentiment(**data)
                for loc, data in aggregated.items()
            }
            
            # Calculate city-wide
            all_scores = [r.get("score", 0.0) for r in individual_results if "error" not in r]
            all_sentiments = [r.get("sentiment") for r in individual_results if "error" not in r]
            
            from collections import Counter
            sentiment_counts = Counter(all_sentiments)
            total = len(all_sentiments)
            
            response_data["city_wide"] = {
                "sentiment": sentiment_counts.most_common(1)[0][0] if sentiment_counts else "neutral",
                "score": round(float(sum(all_scores) / len(all_scores)), 3) if all_scores else 0.0,
                "distribution": {
                    "positive": round(sentiment_counts.get("positive", 0) / total, 3) if total > 0 else 0,
                    "negative": round(sentiment_counts.get("negative", 0) / total, 3) if total > 0 else 0,
                    "neutral": round(sentiment_counts.get("neutral", 0) / total, 3) if total > 0 else 0,
                }
            }
        
        logger.success(f"[{request_id}] Sentiment analysis complete")
        
        return SentimentAnalysisResponse(**response_data)
        
    except Exception as e:
        logger.error(f"[{request_id}] Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/mood-map")
async def create_mood_map(
    request: MoodMapRequest,
    background_tasks: BackgroundTasks
):
    """
    Create mood map for Bengaluru
    
    - Aggregates sentiment by location
    - Provides city-wide sentiment overview
    - Stores result in Firebase 'mood_map' collection
    - Useful for visualizing public sentiment across city zones
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Mood map request: {len(request.texts)} texts")
        
        # Get analyzer
        analyzer = get_sentiment_analyzer()
        
        # Create mood map
        mood_map = analyzer.create_mood_map(
            texts=request.texts,
            locations=request.locations,
            timestamp=request.timestamp
        )
        
        # Add processing time
        mood_map['processing_time_ms'] = (time.time() - start_time) * 1000
        
        # Save to Firebase in background
        background_tasks.add_task(
            firebase_client.save_mood_map,
            mood_map
        )
        
        logger.success(f"[{request_id}] Mood map created with {len(mood_map['locations'])} locations")
        
        return mood_map
        
    except Exception as e:
        logger.error(f"[{request_id}] Mood map creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# BACKGROUND TASKS
# ========================================

def save_vision_result_to_firebase(result_data: dict, location: str, lat: float, lon: float):
    """Save vision analysis result to Firebase"""
    try:
        # Add location data
        if location:
            result_data['location'] = location
        if lat and lon:
            result_data['coordinates'] = {'lat': lat, 'lon': lon}
        
        firebase_client.save_vision_result(result_data)
    except Exception as e:
        logger.error(f"Failed to save vision result to Firebase: {e}")


def save_alert_to_firebase(alert_data: dict):
    """Save alert to Firebase"""
    try:
        firebase_client.save_alert(alert_data)
    except Exception as e:
        logger.error(f"Failed to save alert to Firebase: {e}")


# ========================================
# ERROR HANDLERS
# ========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc),
            request_id=str(uuid.uuid4())
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            request_id=str(uuid.uuid4())
        ).model_dump()
    )


# ========================================
# MAIN ENTRY POINT
# ========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        log_level=config.api.log_level,
        workers=1 if config.api.reload else config.api.workers
    )
