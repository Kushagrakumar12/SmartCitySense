# 🤖 SmartCitySense - AI/ML Module (Members B1 & B2)

> Complete AI Intelligence Layer: Vision, Predictive Analytics, Text Summarization & Sentiment Analysis

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

This is the **complete AI/ML layer** combining:

### **Member B1 - Text Intelligence**
- 📝 **Text Summarization**: LLM-powered summarization of citizen reports using Gemini/GPT
- 💭 **Sentiment Analysis**: BERT-based mood detection with location aggregation
- 🗺️ **Mood Mapping**: City-wide sentiment visualization by area

### **Member B2 - Vision & Predictive**
- 🖼️ **Vision Intelligence**: Automatic event detection from images/videos using YOLOv8
- 🔮 **Predictive Analytics**: Anomaly detection and forecasting using ML models
- 🚨 **Alert Generation**: Real-time alerts for emerging city issues

### **Unified REST API**
- 📊 10 FastAPI endpoints for complete integration
- 🔄 Firebase integration for data persistence
- ⚡ Real-time processing with background tasks

## ✨ Key Features

### 📝 Text Intelligence (Member B1)
- **LLM-Powered Summarization**
  - Dual provider support: Google Gemini 1.5 Flash + OpenAI GPT-4 Turbo
  - Custom prompts for 6 event types (traffic, power, civic, weather, cultural, default)
  - Template fallback when LLM unavailable
  - Intelligent deduplication (80% Jaccard similarity threshold)
  - Confidence scoring and keyword extraction
  
- **Sentiment Analysis**
  - BERT-based classification (DistilBERT fine-tuned on SST-2)
  - Location extraction for 19+ Bengaluru areas
  - Mood map generation with city-wide aggregation
  - Batch processing for efficiency
  - Trend analysis for historical data
  
- **Text Preprocessing**
  - URL, mention, hashtag removal
  - Whitespace normalization
  - Location pattern matching
  - Multilingual support (foundation)

### 🖼️ Vision Intelligence (Member B2)
- Object detection and classification (YOLOv8)
- Event categorization (traffic, obstruction, flooding, fire, etc.)
- Video analysis with key frame extraction
- Automatic description generation
- Severity estimation

### 🔮 Predictive Modeling (Member B2)
- Anomaly detection using Isolation Forest
- Time-series forecasting with Facebook Prophet
- Real-time pattern analysis
- Alert threshold detection
- Trend identification

## 🚀 Quick Start

### 1. Installation

```bash
cd ai-ml

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required configuration:
- **Text Processing (B1)**: LLM provider (Gemini/OpenAI), API keys, sentiment model
- **Vision (B2)**: Model confidence thresholds, image size limits
- **Predictive (B2)**: Anomaly contamination, forecast periods
- **Firebase**: Credentials path, collection names
- **API**: Host, port, CORS settings

### 3. Run API Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at:
- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 📁 Project Structure

```
ai-ml/
├── README.md                    # This file
├── QUICKSTART.md                # Detailed setup guide (B2)
├── ARCHITECTURE.md              # System architecture (B2)
├── IMPLEMENTATION_B1.md         # B1 implementation guide (NEW)
├── TEXT_PROCESSING.md           # B1 documentation (NEW)
├── requirements.txt             # Python dependencies (UPDATED)
├── .env.example                 # Environment template (UPDATED)
├── main.py                      # FastAPI application (UPDATED: 10 endpoints)
│
├── config/                      # Configuration
│   ├── __init__.py
│   └── config.py                # UPDATED: Added TextConfig
│
├── text/                        # Text Intelligence (Member B1) - NEW
│   ├── __init__.py              # Module initialization
│   ├── text_summarizer.py       # LLM-powered summarization (610 lines)
│   └── sentiment_analyzer.py    # Sentiment analysis & mood mapping (450 lines)
│
├── vision/                      # Vision Intelligence (Member B2)
│   ├── __init__.py
│   ├── image_classifier.py      # YOLOv8 image analysis
│   └── video_analyzer.py        # Video frame extraction & analysis
│
├── predictive/                  # Predictive Modeling (Member B2)
│   ├── __init__.py
│   ├── anomaly_detector.py      # Isolation Forest anomaly detection
│   └── timeseries_model.py      # Prophet forecasting
│
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── logger.py                # Logging configuration
│   ├── schemas.py               # UPDATED: Added B1 schemas (8 new models)
│   └── firebase_client.py       # UPDATED: Added B1 storage methods
│
├── tests/                       # Unit tests
│   ├── __init__.py
│   ├── test_text.py             # Text module tests (NEW)
│   ├── test_vision.py           # Vision module tests
│   ├── test_predictive.py       # Predictive module tests
│   └── test_api.py              # API endpoint tests
│
├── models/                      # Saved models (auto-created)
│   ├── yolov8n.pt              # YOLO weights (downloaded)
│   ├── distilbert-*            # Sentiment model (downloaded)
│   ├── isolation_forest.pkl     # Anomaly detector
│   └── prophet_*.pkl            # Forecast models
│
└── logs/                        # Log files (auto-created)
    └── ai_ml_*.log
```

## 🔌 API Endpoints

### Health Check
```bash
GET /health          # Overall system health
GET /health/models   # Individual model status (vision, predictive, text)
```

### Text Intelligence (Member B1)

**Summarize Reports**
```bash
POST /ai/summarize
Content-Type: application/json

{
  "reports": ["Multiple citizen reports about same incident"],
  "event_type": "traffic",
  "location": "Old Airport Road",
  "use_llm": true
}
```

**Sentiment Analysis**
```bash
POST /ai/sentiment
Content-Type: application/json

{
  "texts": ["Social media posts or comments"],
  "locations": ["Koramangala", "Whitefield"],
  "aggregate_by_location": true
}
```

**Generate Mood Map**
```bash
POST /ai/mood-map
Content-Type: application/json

{
  "texts": ["Multiple texts from across city"],
  "locations": ["Various locations"]
}
```

### Vision Analysis (Member B2)

**Analyze Image**
```bash
POST /ai/vision/image
Content-Type: multipart/form-data

Parameters:
- file: Image file (JPG, PNG)
- location: Optional location description
- latitude: Optional latitude
- longitude: Optional longitude
```

**Analyze Video**
```bash
POST /ai/vision/video
Content-Type: multipart/form-data

Parameters:
- file: Video file (MP4, AVI, MOV)
- location: Optional location
- sample_rate: Frame sampling rate
```

### Predictive Analysis (Member B2)

**Detect Anomalies**
```bash
POST /ai/predict/anomaly
Content-Type: application/json

{
  "location": "MG Road",
  "event_types": ["traffic", "power_outage"],
  "time_window_minutes": 15
}
```

**Forecast Events**
```bash
POST /ai/predict/forecast
Content-Type: application/json

{
  "event_types": ["traffic"],
  "forecast_hours": 24
}
```

### Training (Admin)

```bash
POST /ai/train/anomaly          # Train anomaly detector
POST /ai/train/forecast/{type}  # Train forecast model
```

## 📊 Data Flow

```
                    ┌─────────────────────────────────┐
                    │       SmartCitySense - Full       │
                    │      AI/ML Intelligence         │
                    └─────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Text Posts    │    │  User Upload    │    │  Historical     │
│ (Twitter/Reddit)│    │  (Image/Video)  │    │  Events Data    │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                       │
         ▼                      ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Text Module    │    │  Vision Module  │    │  Predictive     │
│  (B1)           │    │  (B2 - YOLOv8)  │    │  Module (B2)    │
│  • Summarize    │    │  • Classify     │    │  • Anomaly Det  │
│  • Sentiment    │    │  • Detect       │    │  • Forecasting  │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                ▼
                        ┌──────────────────┐
                        │   Firestore      │
                        │   (Events DB)    │
                        │  • events        │
                        │  • summarized_   │
                        │    events        │
                        │  • mood_map      │
                        │  • predictions   │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   REST API       │
                        │   10 Endpoints   │
                        └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
            ┌──────────────┐         ┌──────────────┐
            │  Backend (D) │         │ Frontend (C) │
            │  Integration │         │  Dashboard   │
            └──────────────┘         └──────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_text.py -v         # B1 tests (NEW)
pytest tests/test_vision.py -v       # B2 vision tests
pytest tests/test_predictive.py -v   # B2 predictive tests
pytest tests/test_api.py -v          # API endpoint tests

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Test specific functionality
pytest tests/test_text.py::TestTextSummarizer -v
pytest tests/test_text.py::TestSentimentAnalyzer -v
```

## 🔧 Configuration

### Model Settings

Edit `.env` file:

```bash
# Text Processing (Member B1)
SUMMARIZATION_LLM_PROVIDER=gemini  # gemini or openai
SUMMARIZATION_MODEL_NAME=gemini-1.5-flash
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
MAX_REPORTS_PER_SUMMARY=50
SUMMARY_MAX_LENGTH=200
SENTIMENT_MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
ENABLE_MULTILINGUAL=False
TEXT_BATCH_SIZE=32

# Vision Model (Member B2)
YOLO_MODEL_SIZE=n  # n, s, m, l, x (nano to xlarge)
VISION_CONFIDENCE_THRESHOLD=0.65
MAX_IMAGE_SIZE=1280
MAX_VIDEO_DURATION_SECONDS=30

# Predictive Models (Member B2)
ANOMALY_CONTAMINATION=0.1
ANOMALY_THRESHOLD=0.85
FORECAST_PERIODS=24
MIN_REPORTS_FOR_ANOMALY=5

# Firebase Collections
FIRESTORE_COLLECTION_EVENTS=events
FIRESTORE_COLLECTION_SUMMARIZED_EVENTS=summarized_events
FIRESTORE_COLLECTION_MOOD_MAP=mood_map
FIRESTORE_COLLECTION_PREDICTIONS=predictions

# API
API_PORT=8001
API_WORKERS=4
MAX_UPLOAD_SIZE_MB=10
```

### Hardware Acceleration

**GPU Support (CUDA)**:
```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Set in .env
USE_GPU=True
```

## 📈 Usage Examples

### Text Intelligence Examples (Member B1)

**Summarize Traffic Reports:**
```python
import requests

response = requests.post(
    'http://localhost:8001/ai/summarize',
    json={
        'reports': [
            'Heavy traffic jam on Silk Board',
            'Silk Board completely blocked',
            'Avoid Silk Board, 1 hour delay'
        ],
        'event_type': 'traffic',
        'location': 'Silk Board',
        'use_llm': True
    }
)
result = response.json()
print(f"Summary: {result['summary']}")
print(f"Confidence: {result['confidence']}")
```

**Analyze Sentiment:**
```python
response = requests.post(
    'http://localhost:8001/ai/sentiment',
    json={
        'texts': [
            'Love the new metro station!',
            'Traffic is terrible today'
        ],
        'aggregate_by_location': True
    }
)
sentiment = response.json()
print(f"City sentiment: {sentiment['city_wide']['sentiment']}")
```

**Generate Mood Map:**
```python
response = requests.post(
    'http://localhost:8001/ai/mood-map',
    json={
        'texts': [
            'Great day at Cubbon Park!',
            'Traffic nightmare on ORR',
            'Amazing food in Indiranagar'
        ]
    }
)
mood_map = response.json()
for location, data in mood_map['locations'].items():
    print(f"{location}: {data['sentiment']} ({data['score']:.2f})")
```

### Vision Intelligence Examples (Member B2)

**Analyze Image:**

```python
import requests

# Analyze image
with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/ai/vision/image',
        files={'file': f},
        data={'location': 'MG Road'}
    )
    result = response.json()
    print(f"Event: {result['event_type']}")
    print(f"Description: {result['description']}")

**Detect Anomalies:**

# Detect anomalies
response = requests.post(
    'http://localhost:8001/ai/predict/anomaly',
    json={
        'location': 'Whitefield',
        'time_window_minutes': 15
    }
)
prediction = response.json()
print(f"Anomaly detected: {prediction['anomaly_result']['is_anomaly']}")
```

### cURL Examples

**Text Summarization:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"reports":["Traffic jam","Road blocked"],"event_type":"traffic"}' \
  http://localhost:8001/ai/summarize
```

**Sentiment Analysis:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"texts":["Great service!","Terrible experience"]}' \
  http://localhost:8001/ai/sentiment
```

**Vision Analysis:**

```bash
# Health check
curl http://localhost:8001/health

# Analyze image
curl -X POST \
  -F "file=@test_image.jpg" \
  -F "location=MG Road" \
  http://localhost:8001/ai/vision/image

# Detect anomalies
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"location":"MG Road","time_window_minutes":15}' \
  http://localhost:8001/ai/predict/anomaly
```

## 🔄 Integration with Other Modules

### With Data Ingestion (Member A)
- Receives real-time events from Firebase
- Uses events for anomaly detection
- Builds historical dataset for training

### With Backend (Member D)
- REST API integration
- Event notifications
- Alert propagation
- User authentication (future)

### With Frontend (Member C)
- Vision analysis results displayed on map
- Predictive alerts shown in UI
- Real-time updates via WebSocket (future)

## 🎓 Model Details

### Text Intelligence Models (Member B1)

**Google Gemini 1.5 Flash**
- **Type**: Large Language Model (LLM)
- **Purpose**: Text summarization
- **Context Window**: 1M tokens
- **Latency**: ~1.2s per summary
- **Cost**: Free tier: 15 RPM, 1M TPM

**OpenAI GPT-4 Turbo**
- **Type**: Large Language Model (LLM)
- **Purpose**: Fallback summarization
- **Context Window**: 128K tokens
- **Latency**: ~1.5s per summary
- **Cost**: $0.01 per 1K tokens

**DistilBERT (SST-2 Fine-tuned)**
- **Type**: Transformer-based classifier
- **Purpose**: Sentiment analysis
- **Model Size**: ~250MB
- **Accuracy**: 89% on benchmark
- **Latency**: ~0.15s per text
- **Classes**: Positive, Negative, Neutral

### Vision Intelligence Models (Member B2)

**YOLOv8 (Vision)**
- **Model**: YOLOv8n (nano) - fast, lightweight
- **Input**: Images (640x640) or video frames
- **Output**: Bounding boxes + class labels
- **Classes**: 80 COCO classes + custom events
- **Performance**: ~45 FPS on GPU, ~5 FPS on CPU

### Predictive Models (Member B2)

**Isolation Forest (Anomaly Detection)**
- **Algorithm**: Unsupervised outlier detection
- **Features**: Event count, time of day, location
- **Contamination**: 10% (configurable)
- **Threshold**: 0.85 for alerts

### Prophet (Forecasting)
- **Type**: Additive time series model
- **Seasonality**: Daily + weekly patterns
- **Forecast Horizon**: 24 hours (configurable)
- **Confidence Interval**: 95%

## 🚨 Troubleshooting

### Text Processing Issues (B1)

**LLM Timeout:**
```bash
# Reduce number of reports
MAX_REPORTS_PER_SUMMARY=30

# Or use template mode
use_llm=False
```

**API Key Not Found:**
```bash
# Check .env file
cat .env | grep API_KEY

# Verify format
GOOGLE_API_KEY=AIzaSy...
OPENAI_API_KEY=sk-...
```

**Sentiment Model Download Failed:**
```python
# Manually download
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
```

### Vision & Predictive Issues (B2)

**Import Errors**
The red squiggly lines in VS Code are normal before installing dependencies:
```bash
pip install -r requirements.txt
```

### YOLO Model Download
First run downloads YOLOv8 weights automatically (~6MB). Subsequent runs use cached model.

### GPU Not Detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Force CPU mode
echo "USE_GPU=False" >> .env
```

### Firebase Connection Failed
Ensure `firebase-credentials.json` exists:
```bash
# Check if file exists
ls -la firebase-credentials.json

# Update path in .env
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### Memory Issues
Reduce batch size or use smaller YOLO model:
```bash
```

**Memory Issues**
```bash
# For text processing
TEXT_BATCH_SIZE=16  # Reduce from 32

# For vision
YOLO_MODEL_SIZE=n  # Use nano instead of medium/large
MAX_IMAGE_SIZE=640  # Reduce from 1280
```
```

## 📚 Additional Documentation

### Member B1 (Text Intelligence)
- **[TEXT_PROCESSING.md](TEXT_PROCESSING.md)** - Complete text module documentation
- **[IMPLEMENTATION_B1.md](IMPLEMENTATION_B1.md)** - Step-by-step implementation guide
- **[tests/test_text.py](tests/test_text.py)** - 40+ test cases for text processing

### Member B2 (Vision & Predictive)
- **[QUICKSTART.md](QUICKSTART.md)** - Step-by-step setup guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system design
- **[tests/test_vision.py](tests/test_vision.py)** - Vision module tests
- **[tests/test_predictive.py](tests/test_predictive.py)** - Predictive module tests

### API Documentation
- **[Interactive Docs](http://localhost:8001/docs)** - Swagger UI (when server running)
- **[ReDoc](http://localhost:8001/redoc)** - Alternative API documentation

## 🎯 Success Criteria

By completion, you should have:

### Member B1 (Text Intelligence)
- ✅ Text summarization with dual LLM support (Gemini + OpenAI)
- ✅ Sentiment analysis with BERT classification
- ✅ Location-based mood mapping for Bengaluru
- ✅ 3 REST API endpoints for text processing
- ✅ Firebase integration for storing summaries and sentiment
- ✅ Comprehensive test coverage (40+ tests)
- ✅ Complete documentation

### Member B2 (Vision & Predictive)
- ✅ Vision module detecting events from images/videos
- ✅ Predictive models generating anomaly alerts
- ✅ REST API serving both modules
- ✅ Integration with Firebase
- ✅ Comprehensive test coverage
- ✅ Complete documentation

### Combined System
- ✅ 10 functional API endpoints
- ✅ 6 AI models deployed (2 text, 2 vision, 2 predictive)
- ✅ Firebase integration across all modules
- ✅ Unified configuration system
- ✅ Complete test suite
- ✅ Production-ready deployment

## 🔒 Security Notes

- Never commit `.env` or `firebase-credentials.json`
- API authentication recommended for production
- Rate limiting for public endpoints
- Input validation for uploads

## 📄 License

MIT License - see LICENSE file for details

## 👥 Team Integration

### Module Ownership
**Member B1** (Text Intelligence) - Text summarization & sentiment analysis  
**Member B2** (Vision & Predictive) - Image/video analysis & forecasting  

### Integration Points
**Member A** (Data Ingestion)
- Provides raw text posts and events → B1 summarization input
- Provides historical data → B2 predictive models
- Receives processed events from vision analysis

**Member D** (Backend API)
- Orchestrates B1 + B2 services
- Combines text sentiment with vision detection
- Serves unified results to frontend

**Member C** (Frontend)
- Displays summarized reports from B1
- Shows mood maps by location
- Visualizes vision detection results
- Presents predictive alerts

---

## 🆘 Need Help?

1. Check [QUICKSTART.md](QUICKSTART.md) for setup issues
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design questions
3. Test with: `python -m pytest tests/ -v`
4. Check logs: `tail -f logs/ai_ml_*.log`
5. API docs: http://localhost:8001/docs

---

**Built with ❤️ for SmartCitySense - Members B1 & B2**

*Complete AI Intelligence: Vision, Predictive, Text & Sentiment for Making Bangalore Smarter* 🏙️🤖

**Total Implementation:**
- **Lines of Code**: 2,500+ (B1: ~1,460, B2: ~1,040)
- **AI Models**: 6 deployed (Gemini, GPT, BERT, YOLO, Isolation Forest, Prophet)
- **API Endpoints**: 10 production-ready
- **Test Coverage**: 80+ test cases
- **Documentation**: 3,500+ lines

---