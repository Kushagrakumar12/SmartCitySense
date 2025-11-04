# 🏗️ Architecture Documentation - AI/ML Module

Comprehensive technical documentation for the Vision & Predictive Modeling system.

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Model Details](#model-details)
5. [API Design](#api-design)
6. [Integration Points](#integration-points)
7. [Scalability](#scalability)
8. [Security](#security)

---

## System Overview

### Purpose
The AI/ML module (Member B2) provides intelligent analysis and prediction capabilities for SmartCitySense:
- **Vision Intelligence**: Automatically detect and classify events from user-uploaded images/videos
- **Predictive Analytics**: Identify anomalies and forecast future event patterns
- **Real-time Alerts**: Generate actionable alerts for emerging city issues

### Technology Stack
- **ML Framework**: PyTorch, scikit-learn
- **Computer Vision**: YOLOv8 (Ultralytics), OpenCV
- **Time Series**: Facebook Prophet
- **API Framework**: FastAPI, Uvicorn
- **Database**: Firebase/Firestore
- **Testing**: pytest
- **Logging**: Loguru

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI/ML Module (B2)                        │
│                                                              │
│  ┌──────────────────┐           ┌──────────────────┐       │
│  │  Vision Module   │           │ Predictive Module│       │
│  │                  │           │                  │       │
│  │ ┌──────────────┐ │           │ ┌──────────────┐│       │
│  │ │Image         │ │           │ │Anomaly       ││       │
│  │ │Classifier    │ │           │ │Detector      ││       │
│  │ │(YOLOv8)      │ │           │ │(I.Forest)    ││       │
│  │ └──────────────┘ │           │ └──────────────┘│       │
│  │                  │           │                  │       │
│  │ ┌──────────────┐ │           │ ┌──────────────┐│       │
│  │ │Video         │ │           │ │Time Series   ││       │
│  │ │Analyzer      │ │           │ │Forecaster    ││       │
│  │ │(Frame Ext.)  │ │           │ │(Prophet)     ││       │
│  │ └──────────────┘ │           │ └──────────────┘│       │
│  └──────────────────┘           └──────────────────┘       │
│           │                              │                  │
│           └──────────────┬───────────────┘                  │
│                          │                                  │
│                   ┌──────▼──────┐                           │
│                   │   FastAPI   │                           │
│                   │  REST API   │                           │
│                   └──────┬──────┘                           │
└──────────────────────────┼───────────────────────────────────┘
                           │
                           │ REST API Calls
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│   Frontend    │  │   Backend    │  │  Firebase    │
│  (Member C)   │  │  (Member D)  │  │  (Database)  │
└───────────────┘  └──────────────┘  └──────────────┘
```

### Module Breakdown

#### 1. Vision Module (`vision/`)

**Image Classifier (`image_classifier.py`)**
- **Purpose**: Detect and classify events from single images
- **Model**: YOLOv8 (nano, small, medium variants)
- **Input**: Image file (JPG, PNG) or URL
- **Output**: Event type, objects detected, confidence, severity
- **Key Features**:
  - Object detection with bounding boxes
  - Event categorization (13+ event types)
  - Automatic description generation
  - Debug image saving

**Video Analyzer (`video_analyzer.py`)**
- **Purpose**: Analyze video clips by extracting key frames
- **Process**:
  1. Extract key frames (configurable sampling rate)
  2. Analyze each frame with ImageClassifier
  3. Aggregate results (voting + confidence averaging)
- **Input**: Video file (MP4, AVI, MOV) or URL
- **Output**: Aggregated event analysis
- **Key Features**:
  - Smart frame sampling
  - Temporal consistency
  - Duration limits (configurable)

#### 2. Predictive Module (`predictive/`)

**Anomaly Detector (`anomaly_detector.py`)**
- **Purpose**: Detect abnormal event patterns in real-time
- **Algorithm**: Isolation Forest (unsupervised)
- **Features**:
  - Event count aggregation by time/location
  - Statistical baseline calculation
  - ML-based anomaly scoring
  - Severity classification
- **Process**:
  1. Query recent events from Firebase (15-min window)
  2. Compare to historical baseline
  3. Run ML model if trained
  4. Generate alert if threshold exceeded

**Time Series Forecaster (`timeseries_model.py`)**
- **Purpose**: Forecast future event patterns
- **Model**: Facebook Prophet
- **Features**:
  - Hourly event count forecasting
  - Daily + weekly seasonality
  - 95% confidence intervals
  - Trend detection
- **Process**:
  1. Fetch historical data (30+ days)
  2. Resample to hourly counts
  3. Train Prophet model
  4. Generate forecasts (1-168 hours ahead)

#### 3. Configuration (`config/`)

**Config Manager (`config.py`)**
- Centralized configuration using Pydantic
- Environment variable loading
- Sub-configs: Firebase, Vision, Predictive, API, Logging
- Hardware detection (GPU/CPU)
- Validation and defaults

#### 4. Utilities (`utils/`)

**Logger (`logger.py`)**
- Structured logging with Loguru
- File rotation (10 MB chunks)
- Console + file output
- Color-coded levels

**Schemas (`schemas.py`)**
- Pydantic models for data validation
- Request/response models
- Event type enums
- Type safety throughout codebase

**Firebase Client (`firebase_client.py`)**
- Firestore integration
- CRUD operations for events, predictions, alerts
- Query helpers (recent events, historical data)
- Graceful degradation if credentials missing

---

## Data Flow

### Vision Analysis Flow

```
User Upload (Image/Video)
        │
        ▼
FastAPI Endpoint (/ai/vision/image or /video)
        │
        ├─ Validate file type & size
        ├─ Save to temporary location
        │
        ▼
Vision Module (ImageClassifier or VideoAnalyzer)
        │
        ├─ Load and preprocess media
        ├─ Run YOLO inference
        ├─ Parse detections
        ├─ Classify event type
        ├─ Generate description
        │
        ▼
VisionAnalysisResponse (JSON)
        │
        ├─ Return to caller
        └─ Save to Firebase (background task)
                │
                ▼
        Firestore 'events' collection
```

### Predictive Analysis Flow

```
API Request (/ai/predict/anomaly or /forecast)
        │
        ▼
Predictive Module
        │
        ├─ Query recent events from Firebase
        │
        ▼
Anomaly Detector
        │
        ├─ Calculate statistical baseline
        ├─ Prepare features
        ├─ Run Isolation Forest
        ├─ Calculate anomaly score
        ├─ Generate alert if threshold exceeded
        │
        ▼
PredictionResponse (JSON)
        │
        ├─ Return to caller
        └─ Save alert to Firebase (if anomaly)
                │
                ▼
        Firestore 'alerts' collection
```

---

## Model Details

### YOLOv8 (Vision)

**Architecture**:
- Backbone: CSPDarknet
- Neck: PANet
- Head: Decoupled detection head

**Variants**:
| Model | Size | Speed (CPU) | Speed (GPU) | mAP |
|-------|------|-------------|-------------|-----|
| YOLOv8n | 6 MB | 5 FPS | 45 FPS | 37.3 |
| YOLOv8s | 22 MB | 3 FPS | 35 FPS | 44.9 |
| YOLOv8m | 52 MB | 1.5 FPS | 25 FPS | 50.2 |

**Default**: YOLOv8n (nano) - best balance for real-time processing

**Event Mapping**:
```python
{
    "car/truck/bus" → "traffic" event
    "tree/debris"   → "obstruction" event
    "water/flood"   → "flooding" event
    "fire/smoke"    → "fire" event
    "person" (20+)  → "protest" event
    "construction"  → "construction" event
}
```

**Inference Pipeline**:
1. Image preprocessing (resize to 640x640)
2. Model forward pass
3. Non-max suppression (NMS)
4. Post-processing (event classification)

### Isolation Forest (Anomaly Detection)

**Algorithm**:
- Unsupervised outlier detection
- Builds ensemble of random trees
- Anomalies = points with short average path length

**Features**:
```
- event_count (per hour-location)
- hour_of_day (0-23)
- day_of_week (0-6)
- location_encoded (top 20 locations)
```

**Hyperparameters**:
- `n_estimators`: 100 trees
- `contamination`: 0.1 (10% expected anomalies)
- `random_state`: 42 (reproducibility)

**Scoring**:
- Anomaly score: 0-1 (higher = more anomalous)
- Threshold: 0.85 for alert generation
- Combined with statistical baseline

### Facebook Prophet (Forecasting)

**Components**:
```
y(t) = g(t) + s(t) + h(t) + ε
```
- `g(t)`: Trend (piecewise linear or logistic)
- `s(t)`: Seasonality (Fourier series)
- `h(t)`: Holidays (not used for city events)
- `ε`: Error term

**Configuration**:
- Daily seasonality: Enabled (24h cycles)
- Weekly seasonality: Enabled (7-day patterns)
- Yearly seasonality: Disabled (insufficient data)
- Changepoint prior: 0.05 (moderate flexibility)

**Training**:
- Minimum: 10 hourly data points
- Recommended: 30+ days of historical data
- Automatic trend detection

---

## API Design

### RESTful Principles

- **Stateless**: Each request contains all necessary info
- **Resource-based**: Endpoints represent resources (vision, predictions)
- **HTTP methods**: POST for analysis (creates results)
- **JSON**: All request/response bodies in JSON
- **Status codes**: Proper use (200, 400, 500, etc.)

### Endpoint Patterns

```
GET  /health               # Health check
GET  /                     # API info

POST /ai/vision/image      # Analyze image
POST /ai/vision/video      # Analyze video

POST /ai/predict/anomaly   # Detect anomalies
POST /ai/predict/forecast  # Generate forecasts

POST /ai/train/anomaly     # Train anomaly model (admin)
POST /ai/train/forecast/{type}  # Train forecast model (admin)
```

### Request/Response Format

**Vision Request**:
```json
{
  "file": "<binary>",
  "location": "MG Road",
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

**Vision Response**:
```json
{
  "event_type": "traffic",
  "description": "Heavy traffic with multiple vehicles",
  "confidence": 0.87,
  "severity": "high",
  "detected_objects": [
    {"class_name": "car", "confidence": 0.92, "bbox": [...]},
    ...
  ],
  "tags": ["traffic", "car", "congestion"],
  "timestamp": "2025-10-11T14:30:00Z",
  "processing_time_ms": 245.3
}
```

**Prediction Request**:
```json
{
  "location": "Whitefield",
  "event_types": ["traffic", "power_outage"],
  "time_window_minutes": 15
}
```

**Prediction Response**:
```json
{
  "alert": "Potential grid outage in Whitefield",
  "alert_type": "power_grid_issue",
  "severity": "high",
  "anomaly_result": {
    "is_anomaly": true,
    "anomaly_score": 0.94,
    "event_count": 12,
    "baseline_count": 2.3
  },
  "recommendations": [
    "Multiple outage reports in 15 minutes",
    "Check transformer status"
  ],
  "processing_time_ms": 156.8
}
```

### Error Handling

```json
{
  "error": "File too large",
  "detail": "Maximum size: 10MB",
  "timestamp": "2025-10-11T14:30:00Z",
  "request_id": "550e8400-e29b-41d4-..."
}
```

---

## Integration Points

### With Data Ingestion (Member A)

**Direction**: A → B2 (via Firebase)

```
Data Ingestion
      │
      ▼ Writes events to
Firebase/Firestore
      │
      ▼ Reads for analysis
AI/ML Module (B2)
```

**Schema Alignment**:
- Both use same event schema (event_type, location, timestamp, etc.)
- Predictive module queries A's ingested events
- No direct API calls needed (decoupled via database)

### With Backend API (Member D)

**Direction**: D ↔ B2 (REST API)

```
Backend (D) ──► POST /ai/vision/image ──► AI/ML (B2)
            ◄── VisionAnalysisResponse ◄──

Backend (D) ──► POST /ai/predict/anomaly ──► AI/ML (B2)
            ◄── PredictionResponse ◄──
```

**Integration Pattern**:
1. Backend receives user upload
2. Backend forwards to AI/ML API
3. AI/ML processes and returns result
4. Backend saves to database + notifies user

**Authentication** (Future):
- API key in request headers
- JWT tokens for user context
- Rate limiting per user/IP

### With Frontend (Member C)

**Direction**: Indirect (via Backend D)

```
Frontend (C) ──► Backend (D) ──► AI/ML (B2)
             ◄──             ◄──
```

**Display Integration**:
- Vision results shown on map (event markers)
- Predictive alerts in notification panel
- Real-time updates via WebSocket (future)

### With Text Summarization (Member B1)

**Parallel Processing**:
```
User Report
    │
    ├──► Vision Analysis (B2) ──► Event Detection
    │
    └──► Text Summarization (B1) ──► Text Summary
                │
                ▼
         Combined in Backend (D)
```

**Complementary Outputs**:
- B2: Visual event classification
- B1: Text description synthesis
- Combined: Rich, multimodal event representation

---

## Scalability

### Horizontal Scaling

**API Server**:
```bash
# Multiple workers
uvicorn main:app --workers 4

# Load balancer (Nginx)
upstream api_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}
```

**Bottlenecks**:
- Vision inference (GPU-bound)
- Database queries (I/O-bound)
- Model loading (memory-bound)

**Solutions**:
- Model caching (load once, reuse)
- Batch processing for multiple images
- Async database operations
- Redis caching for frequent queries

### Vertical Scaling

**Hardware Upgrades**:
- **CPU**: More cores for parallel processing
- **RAM**: Load larger models (YOLOv8m/l)
- **GPU**: NVIDIA T4/V100 for 10x speedup
- **SSD**: Faster model/data loading

**Performance Gains**:
| Hardware | Image/sec | Video (30 frames) |
|----------|-----------|-------------------|
| CPU (4 cores) | 0.5-1 | 60-120 sec |
| GPU (T4) | 5-10 | 10-20 sec |
| GPU (V100) | 15-20 | 5-10 sec |

### Database Optimization

**Firebase/Firestore**:
- Composite indexes on (timestamp, location, event_type)
- Partitioning by date ranges
- Caching frequent queries
- Batch writes for bulk operations

**Query Optimization**:
```python
# Efficient: Query with filters
events = db.collection('events')\
    .where('timestamp', '>=', time_threshold)\
    .where('event_type', '==', 'traffic')\
    .limit(100)\
    .stream()

# Inefficient: Fetch all then filter in code
```

---

## Security

### Input Validation

**File Uploads**:
- Size limits (10 MB default)
- Type validation (image/video MIME types)
- Content verification (check file headers)
- Virus scanning (future)

**API Inputs**:
- Pydantic validation for all request bodies
- SQL injection prevention (parameterized queries)
- Path traversal protection
- Rate limiting

### Authentication & Authorization

**Current**: Open API (development)

**Production TODO**:
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/ai/vision/image")
async def analyze_image(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Verify API key/token
    if not verify_token(credentials.credentials):
        raise HTTPException(401, "Invalid credentials")
    ...
```

### Data Privacy

**User Uploads**:
- Temporary storage only (deleted after processing)
- No permanent storage of user images
- Optional debug image saving (disabled in production)

**Firebase Security Rules**:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /events/{event} {
      allow read: if request.auth != null;
      allow write: if request.auth != null;
    }
  }
}
```

### Secrets Management

**Never Commit**:
- `.env` files
- `firebase-credentials.json`
- API keys

**Best Practices**:
```bash
# Use environment variables
export FIREBASE_CREDENTIALS_PATH=/secure/path/firebase.json

# Or secrets management service
aws secretsmanager get-secret-value --secret-id smartcitysense/firebase
```

---

## Performance Optimization

### Model Optimization

**YOLOv8**:
- Use TorchScript for faster inference
- Quantization (INT8) for 4x speedup
- TensorRT optimization for NVIDIA GPUs

```python
# Export to TorchScript
model.export(format='torchscript')

# Or ONNX for cross-platform
model.export(format='onnx')
```

### Caching Strategy

**Model Caching**:
- Load models once at startup
- Keep in memory (lazy loading)
- Warm up with dummy input

**Result Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_recent_events(event_type, location, minutes):
    # Cache frequent queries
    return firebase_client.get_recent_events(...)
```

### Async Operations

**FastAPI Async**:
```python
@app.post("/ai/vision/image")
async def analyze_image(...):
    # Save to Firebase asynchronously
    background_tasks.add_task(save_to_firebase, result)
    
    # Return immediately
    return result
```

---

## Monitoring & Logging

### Metrics to Track

- **Latency**: p50, p95, p99 response times
- **Throughput**: Requests per second
- **Error Rate**: 4xx, 5xx responses
- **Model Performance**: Inference time, GPU utilization
- **Resource Usage**: CPU, RAM, disk I/O

### Logging Levels

```
DEBUG: Detailed debugging info
INFO:  Normal operations
WARNING: Potential issues
ERROR: Operation failures
CRITICAL: System failures
```

### Health Checks

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models_loaded": check_models(),
        "gpu_available": torch.cuda.is_available(),
        "firebase_connected": firebase_client.initialized
    }
```

---

## Future Enhancements

1. **Model Improvements**:
   - Fine-tune YOLOv8 on Bangalore-specific images
   - Custom object classes (auto-rickshaw, potholes, etc.)
   - Ensemble models for better accuracy

2. **Advanced Features**:
   - Real-time video streaming analysis
   - Multi-camera fusion
   - Sentiment analysis from crowd images
   - Weather-event correlation

3. **Scalability**:
   - Kubernetes deployment
   - GPU autoscaling
   - CDN for model distribution
   - Edge deployment (mobile devices)

4. **Integration**:
   - WebSocket for real-time updates
   - GraphQL API for flexible queries
   - Kafka for event streaming
   - Redis pub/sub for notifications

---

**This architecture provides a solid foundation for intelligent city event analysis and prediction, designed for scalability, maintainability, and integration with the broader SmartCitySense ecosystem.**
