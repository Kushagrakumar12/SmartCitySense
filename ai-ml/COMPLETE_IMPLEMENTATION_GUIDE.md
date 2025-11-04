# 🚀 Complete AI/ML Module Implementation Guide
## Comprehensive Setup for Members B1 & B2

**Date:** October 25, 2025  
**Status:** ✅ Production Ready  
**Estimated Time:** 2-3 hours (first-time setup)  
**Difficulty:** Intermediate

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Architecture](#system-architecture)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Testing & Verification](#testing--verification)
6. [Running the System](#running-the-system)
7. [API Usage](#api-usage)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)

---

## 🎯 What You're Building

A complete AI intelligence layer with **6 AI models** and **10 API endpoints**:

### **Member B1 - Text Intelligence**
- 📝 Text summarization (Gemini/GPT)
- 💭 Sentiment analysis (BERT)
- 🗺️ Location-based mood mapping

### **Member B2 - Vision & Predictive**
- 🖼️ Image/video analysis (YOLOv8)
- 🔮 Anomaly detection (Isolation Forest)
- 📈 Event forecasting (Prophet)

---

## ✅ Prerequisites

### **1. System Requirements**

**Minimum:**
- OS: macOS, Linux, or Windows
- RAM: 8GB (16GB recommended)
- Storage: 5GB free space
- Python: 3.8 or higher

**Optional (for better performance):**
- GPU: NVIDIA GPU with CUDA support
- Internet: For downloading models (~500MB total)

### **2. Check Python Version**

```bash
# Check Python version (must be 3.8+)
python --version
# or
python3 --version

# If not installed, install Python 3.8+
# macOS:
brew install python@3.11

# Linux (Ubuntu/Debian):
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### **3. Required Accounts & API Keys**

You'll need **at least one** of these:

#### **Option A: Google Gemini (Recommended - Free)**
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)
5. **FREE TIER:** 15 requests/minute, 1M tokens/day

#### **Option B: OpenAI GPT (Paid)**
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. **PAID:** $0.01 per 1K tokens (GPT-4 Turbo)

#### **Firebase Setup (Required)**
1. Go to: https://console.firebase.google.com/
2. Create a new project (or use existing)
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Download JSON file (rename to `firebase-credentials.json`)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              SmartCitySense - Complete AI/ML Module            │
│                    (Members B1 + B2)                         │
└─────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   Data Sources  │
                    │  • Twitter      │
                    │  • Reddit       │
                    │  • Images       │
                    │  • Videos       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Firebase DB   │
                    │   (Firestore)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│  TEXT (B1)    │    │ VISION (B2)  │    │PREDICTIVE(B2)│
│               │    │              │    │              │
│ • Gemini/GPT  │    │ • YOLOv8     │    │• IsolForest  │
│ • BERT        │    │ • Video      │    │• Prophet     │
│ • Locations   │    │ • Objects    │    │• Anomalies   │
└───────┬───────┘    └──────┬───────┘    └──────┬───────┘
        │                   │                    │
        └───────────────────┼────────────────────┘
                            ▼
                  ┌──────────────────┐
                  │   FastAPI Server │
                  │   10 Endpoints   │
                  │  Port: 8001      │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │Frontend │  │Backend  │  │ Mobile  │
        │  (C)    │  │  (D)    │  │  App    │
        └─────────┘  └─────────┘  └─────────┘
```

---

## 📦 Installation Steps

### **Step 1: Navigate to Project Directory**

```bash
# Open terminal and navigate to the ai-ml folder
cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml

# Verify you're in the right place
pwd
# Should show: /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml

# List files to confirm
ls
# Should see: main.py, requirements.txt, config/, text/, vision/, etc.
```

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# You should see (venv) in your terminal prompt
# (venv) username@computer ai-ml %

# To deactivate later (don't do this now):
# deactivate
```

### **Step 3: Upgrade pip**

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Verify pip version
pip --version
# Should be 23.0 or higher
```

### **Step 4: Install Dependencies**

This will download all required packages (~500MB total):

```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt

# This will install:
# - FastAPI & Uvicorn (API server)
# - Firebase Admin SDK
# - YOLOv8 (vision)
# - Transformers & PyTorch (BERT)
# - Langchain (LLM integration)
# - Google Generative AI (Gemini)
# - OpenAI SDK
# - Prophet & scikit-learn (predictive)
# - And 30+ other packages

# ⏱️ This takes 5-10 minutes depending on internet speed
```

**Expected output:**
```
Collecting fastapi>=0.104.0
  Downloading fastapi-0.104.1-py3-none-any.whl
...
Successfully installed 45 packages
```

### **Step 5: Download AI Models**

Some models auto-download on first use, but you can pre-download them:

```bash
# Create models directory
mkdir -p models

# Download YOLOv8 model (for vision)
python3 -c "
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Downloads ~6MB
print('YOLOv8 downloaded successfully!')
"

# Download BERT model (for sentiment)
python3 -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
print('BERT model downloaded successfully!')
"
# Downloads ~250MB

# ⏱️ This takes 2-5 minutes
```

---

## ⚙️ Configuration

### **Step 6: Set Up Firebase**

```bash
# 1. Place your Firebase credentials file in the ai-ml directory
# It should be named: firebase-credentials.json

# 2. Verify the file exists
ls -la firebase-credentials.json

# Should show the file with your credentials
```

**Firebase credentials file structure:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "firebase-adminsdk-...@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### **Step 7: Configure Environment Variables**

```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Open .env in your text editor
nano .env
# or
code .env  # if using VS Code
# or
vim .env
```

**Edit the `.env` file with your settings:**

```bash
# ========================================
# FIREBASE CONFIGURATION
# ========================================
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIRESTORE_COLLECTION_EVENTS=events
FIRESTORE_COLLECTION_PREDICTIONS=predictions
FIRESTORE_COLLECTION_SUMMARIZED_EVENTS=summarized_events
FIRESTORE_COLLECTION_MOOD_MAP=mood_map

# ========================================
# TEXT PROCESSING (Member B1)
# ========================================

# Choose your LLM provider (gemini or openai)
SUMMARIZATION_LLM_PROVIDER=gemini

# If using Gemini (recommended - free):
SUMMARIZATION_MODEL_NAME=gemini-1.5-flash
GOOGLE_API_KEY=AIzaSy_YOUR_ACTUAL_KEY_HERE

# If using OpenAI (paid alternative):
# SUMMARIZATION_MODEL_NAME=gpt-4-turbo
# OPENAI_API_KEY=sk-YOUR_ACTUAL_KEY_HERE

# Summarization settings
MAX_REPORTS_PER_SUMMARY=50
SUMMARY_MAX_LENGTH=200

# Sentiment analysis settings
SENTIMENT_MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
ENABLE_MULTILINGUAL=False
TEXT_BATCH_SIZE=32

# ========================================
# VISION MODEL (Member B2)
# ========================================
YOLO_MODEL_SIZE=n  # Options: n(nano), s(small), m(medium), l(large), x(xlarge)
VISION_CONFIDENCE_THRESHOLD=0.65
MAX_IMAGE_SIZE=1280
MAX_VIDEO_DURATION_SECONDS=30
VIDEO_SAMPLE_RATE=1  # Extract 1 frame per second

# ========================================
# PREDICTIVE MODELS (Member B2)
# ========================================
ANOMALY_CONTAMINATION=0.1
ANOMALY_THRESHOLD=0.85
FORECAST_PERIODS=24
MIN_REPORTS_FOR_ANOMALY=5
CONFIDENCE_THRESHOLD=0.7

# ========================================
# API CONFIGURATION
# ========================================
API_HOST=0.0.0.0
API_PORT=8001
API_WORKERS=4
DEBUG_MODE=True
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# ========================================
# SYSTEM SETTINGS
# ========================================
ENVIRONMENT=development
USE_GPU=False  # Set to True if you have NVIDIA GPU with CUDA
MAX_UPLOAD_SIZE_MB=10
ENABLE_BACKGROUND_TASKS=True
```

**Save the file** (Ctrl+O, Enter, Ctrl+X in nano)

### **Step 8: Verify Configuration**

```bash
# Test if configuration loads correctly
python3 -c "
from config.config import Config
config = Config()
config.print_config()
"
```

**Expected output:**
```
============================================================
🤖 AI/ML Module Configuration
============================================================
Environment: development
Device: cpu (GPU Available: False)

Firebase:
  Credentials: ./firebase-credentials.json
  Collections: events, predictions, summarized_events, mood_map

Text Intelligence:
  LLM Provider: gemini
  Model: gemini-1.5-flash
  Sentiment Model: distilbert-base-uncased-finetuned-sst-2-english
  Multilingual: False

Vision:
  Model: yolov8n
  Confidence: 0.65
  Max Image Size: 1280

Predictive:
  Anomaly Threshold: 0.85
  Forecast Periods: 24

API:
  Host: 0.0.0.0:8001
  Workers: 4
  Debug: True
============================================================
```

---

## 🧪 Testing & Verification

### **Step 9: Run Unit Tests**

```bash
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_text.py -v          # B1 tests (40+ cases)
pytest tests/test_vision.py -v        # B2 vision tests
pytest tests/test_predictive.py -v    # B2 predictive tests

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

**Expected output:**
```
======================== test session starts ========================
collected 80+ items

tests/test_text.py::TestTextSummarizer::test_initialization PASSED
tests/test_text.py::TestTextSummarizer::test_preprocess_reports PASSED
tests/test_text.py::TestSentimentAnalyzer::test_analyze_sentiment PASSED
...

======================== 80 passed in 45.23s ========================
```

### **Step 10: Test Individual Components**

**Test Text Summarizer:**
```bash
python3 -c "
from text.text_summarizer import TextSummarizer

summarizer = TextSummarizer()

reports = [
    'Heavy traffic on MG Road',
    'MG Road completely jammed',
    'Avoid MG Road until evening'
]

result = summarizer.summarize(reports, event_type='traffic', use_llm=False)
print('Summary:', result['summary'])
print('Confidence:', result['confidence'])
"
```

**Test Sentiment Analyzer:**
```bash
python -c "
from text.simple_sentiment_analyzer import SimpleSentimentAnalyzer

# Note: Using SimpleSentimentAnalyzer for Python 3.13 compatibility
# For Python 3.11, you can use SentimentAnalyzer (BERT-based)
analyzer = SimpleSentimentAnalyzer()

result = analyzer.analyze_sentiment('I love Bangalore!', location='Bangalore')
print('Sentiment:', result['sentiment'])
print('Score:', result['score'])
print('Confidence:', result['confidence'])
"
```

**Note:** If you're using Python 3.13 on Apple Silicon, use `SimpleSentimentAnalyzer` to avoid bus errors. For Python 3.11 or lower, you can use the BERT-based `SentimentAnalyzer` for higher accuracy. See `FIX_BUS_ERROR.md` for details.

**Test Vision Classifier:**
```bash
# Download a test image first
curl -o test_image.jpg "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=400"

python3 -c "
from vision.image_classifier import ImageClassifier
from PIL import Image

classifier = ImageClassifier()

# Method 1: Load from PIL Image
image = Image.open('test_image.jpg')
result = classifier.classify_image(image)
print('Event Type:', result.event_type.value)
print('Confidence:', result.confidence)

# Method 2: Load from file path
result2 = classifier.classify_image('test_image.jpg')
print('Event Type:', result2.event_type.value)
print('Confidence:', result2.confidence)
"
```

---

## 🚀 Running the System

### **Step 11: Start the API Server**

```bash
# Method 1: Using main.py (recommended)
python3 main.py

# Method 2: Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Method 3: With specific workers
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
```

**Expected output:**
```
============================================================
🤖 AI/ML Module Configuration
============================================================
Environment: development
Device: cpu (GPU Available: False)

Text Intelligence:
  LLM Provider: gemini
  Model: gemini-2.5-flash
  Sentiment Model: distilbert-base-uncased-finetuned-sst-2-english

Vision:
  Model: yolov8n
  Confidence: 0.65

API:
  Host: 0.0.0.0:8001
  Workers: 4
============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

### **Step 12: Verify Server is Running**

**Open a new terminal window and test:**

```bash
# Test health endpoint
curl http://localhost:8001/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-25T10:30:00Z",
#   "version": "1.0.0",
#   "environment": "development"
# }

# Test model health
curl http://localhost:8001/health/models

# Expected response:
# {
#   "models": {
#     "vision": "ready",
#     "video": "ready",
#     "anomaly": "ready",
#     "forecast": "ready",
#     "summarization": "ready",
#     "sentiment": "ready"
#   },
#   "device": "cpu"
# }
```

### **Step 13: Access Interactive API Documentation**

Open your web browser and go to:

**Swagger UI (Interactive):**
```
http://localhost:8001/docs
```

**ReDoc (Alternative):**
```
http://localhost:8001/redoc
```

You'll see all 10 endpoints with:
- Request/response schemas
- Try-it-out functionality
- Example payloads
- Response codes

---

## 🎮 API Usage

### **Endpoint 1: Summarize Text Reports**

```bash
curl -X POST "http://localhost:8001/ai/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "reports": [
      "Heavy traffic on MG Road near Trinity Metro",
      "MG Road completely jammed, 30 min delay",
      "Avoid MG Road, use alternate route"
    ],
    "event_type": "traffic",
    "location": "MG Road",
    "use_llm": true
  }'
```

**Response:**
```json
{
  "event_type": "traffic",
  "summary": "Heavy traffic congestion on MG Road near Trinity Metro causing 30-minute delays. Consider alternate routes.",
  "confidence": 0.94,
  "location": "MG Road",
  "timestamp": "2025-10-25T10:35:00Z",
  "source_count": 3,
  "processed_count": 3,
  "keywords": ["traffic", "mg road", "delay", "jam"],
  "method": "llm",
  "processing_time_ms": 1234.5
}
```

### **Endpoint 2: Analyze Sentiment**

```bash
curl -X POST "http://localhost:8001/ai/sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Love the new metro station in Whitefield!",
      "Traffic is horrible in Koramangala today",
      "Great weather in Bangalore"
    ],
    "aggregate_by_location": true
  }'
```

**Response:**
```json
{
  "location_aggregates": {
    "Whitefield": {
      "sentiment": "positive",
      "score": 0.92,
      "sample_size": 1,
      "distribution": {"positive": 1.0, "negative": 0.0, "neutral": 0.0}
    },
    "Koramangala": {
      "sentiment": "negative",
      "score": -0.88,
      "sample_size": 1,
      "distribution": {"positive": 0.0, "negative": 1.0, "neutral": 0.0}
    }
  },
  "city_wide": {
    "sentiment": "neutral",
    "score": 0.01,
    "distribution": {"positive": 0.67, "negative": 0.33, "neutral": 0.0}
  },
  "total_analyzed": 3,
  "processing_time_ms": 456.2
}
```

### **Endpoint 3: Generate Mood Map**

```bash
curl -X POST "http://localhost:8001/ai/mood-map" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Great day at Cubbon Park!",
      "Traffic nightmare on ORR",
      "Love Indiranagar cafes"
    ]
  }'
```

### **Endpoint 4: Analyze Image**

```bash
curl -X POST "http://localhost:8001/ai/vision/image" \
  -F "file=@/path/to/image.jpg" \
  -F "location=MG Road"
```

### **Endpoint 5: Analyze Video**

```bash
curl -X POST "http://localhost:8001/ai/vision/video" \
  -F "file=@/path/to/video.mp4" \
  -F "location=Silk Board" \
  -F "sample_rate=2"
```

### **Endpoint 6: Detect Anomalies**

```bash
curl -X POST "http://localhost:8001/ai/predict/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "MG Road",
    "event_types": ["traffic", "power_outage"],
    "time_window_minutes": 15
  }'
```

### **Endpoint 7: Forecast Events**

```bash
curl -X POST "http://localhost:8001/ai/predict/forecast" \
  -H "Content-Type: application/json" \
  -d '{
    "event_types": ["traffic"],
    "forecast_hours": 24
  }'
```

---

## 🔧 Troubleshooting

### **Issue 1: Module Import Errors**

**Problem:**
```
ImportError: No module named 'transformers'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### **Issue 2: API Key Not Working**

**Problem:**
```
Error: API key not configured or invalid
```

**Solution:**
```bash
# 1. Check .env file
cat .env | grep API_KEY

# 2. Verify key format
# Gemini: AIzaSy...
# OpenAI: sk-...

# 3. Test key
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Google Key:', os.getenv('GOOGLE_API_KEY'))
print('OpenAI Key:', os.getenv('OPENAI_API_KEY'))
"

# 4. Restart server after fixing .env
```

### **Issue 3: Port Already in Use**

**Problem:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 8001
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8002
```

### **Issue 4: Firebase Connection Failed**

**Problem:**
```
Error: Could not authenticate with Firebase
```

**Solution:**
```bash
# 1. Verify credentials file exists
ls -la firebase-credentials.json

# 2. Check file permissions
chmod 600 firebase-credentials.json

# 3. Verify path in .env
cat .env | grep FIREBASE_CREDENTIALS_PATH

# 4. Test Firebase connection
python3 -c "
from utils.firebase_client import firebase_client
print('Firebase connected:', firebase_client.db is not None)
"
```

### **Issue 5: Model Download Failed**

**Problem:**
```
Error downloading model files
```

**Solution:**
```bash
# 1. Check internet connection
ping google.com

# 2. Clear cache and retry
rm -rf ~/.cache/huggingface/
rm -rf ~/.cache/torch/

# 3. Manual download
python3 -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
print('Model downloaded!')
"
```

### **Issue 6: Out of Memory**

**Problem:**
```
RuntimeError: CUDA out of memory
```

**Solution:**
```bash
# 1. Reduce batch size in .env
TEXT_BATCH_SIZE=16  # Instead of 32

# 2. Use smaller YOLO model
YOLO_MODEL_SIZE=n  # Instead of m or l

# 3. Disable GPU if causing issues
USE_GPU=False

# 4. Restart server
```

### **Issue 7: Slow Performance**

**Solutions:**
```bash
# 1. Enable template mode (skip LLM)
# In requests, set: "use_llm": false

# 2. Reduce image size
MAX_IMAGE_SIZE=640  # Instead of 1280

# 3. Use batch processing
# Send multiple texts at once instead of individually

# 4. Enable GPU if available
USE_GPU=True
```

---

## 🌐 Production Deployment

### **Step 14: Prepare for Production**

```bash
# 1. Update .env for production
ENVIRONMENT=production
DEBUG_MODE=False
LOG_LEVEL=WARNING

# 2. Set proper CORS origins
CORS_ORIGINS=["https://yourfrontend.com"]

# 3. Use stronger workers
API_WORKERS=8  # Or more based on CPU cores

# 4. Enable GPU if available
USE_GPU=True
```

### **Step 15: Run with Gunicorn (Production Server)**

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### **Step 16: Set Up as System Service (Linux)**

Create `/etc/systemd/system/smartcitysense.service`:

```ini
[Unit]
Description=SmartCitySense/ML Module
After=network.target

[Service]
Type=notify
User=your-username
WorkingDirectory=/path/to/SmartCitySense/ai-ml
Environment="PATH=/path/to/SmartCitySense/ai-ml/venv/bin"
ExecStart=/path/to/SmartCitySense/ai-ml/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable smartcitysense
sudo systemctl start smartcitysense

# Check status
sudo systemctl status smartcitysense

# View logs
sudo journalctl -u smartcitysense -f
```

### **Step 17: Set Up Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/smartcitysense`:

```nginx
server {
    listen 80;
    server_name ai.smartcitysense.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        
        # WebSocket support (future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Max upload size
    client_max_body_size 10M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/smartcitysense /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### **Step 18: Enable HTTPS (Let's Encrypt)**

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d ai.smartcitysense.com

# Auto-renewal is set up automatically
```

---

## 📊 Monitoring & Logging

### **View Logs**

```bash
# Application logs
tail -f logs/ai_ml_*.log

# System service logs (if using systemd)
sudo journalctl -u smartcitysense -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Monitor Performance**

```bash
# Check CPU/Memory usage
htop

# Check disk usage
df -h

# Check network
netstat -tulpn | grep 8001
```

---

## ✅ Final Checklist

Before going live, verify:

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] API keys configured and working
- [ ] Firebase credentials valid
- [ ] All models downloaded successfully
- [ ] Health endpoints return 200
- [ ] Can access interactive docs at `/docs`
- [ ] All 10 endpoints tested and working
- [ ] Environment set to production
- [ ] CORS configured for your domain
- [ ] Logs directory writable
- [ ] Firewall allows port 8001 (or your port)
- [ ] SSL certificate installed (HTTPS)
- [ ] Backup strategy in place
- [ ] Monitoring set up

---

## 🎓 Learning Resources

### **Official Documentation**
- FastAPI: https://fastapi.tiangolo.com/
- Gemini API: https://ai.google.dev/docs
- Transformers: https://huggingface.co/docs/transformers
- YOLOv8: https://docs.ultralytics.com/

### **Video Tutorials**
- FastAPI Crash Course: YouTube
- Gemini API Tutorial: Google AI
- BERT Sentiment Analysis: HuggingFace

### **Community**
- Stack Overflow: [fastapi], [transformers], [pytorch]
- Discord: FastAPI Server, HuggingFace
- Reddit: r/MachineLearning, r/FastAPI

---

## 📞 Getting Help

### **Documentation Files**
1. **[TEXT_PROCESSING.md](TEXT_PROCESSING.md)** - B1 API reference
2. **[IMPLEMENTATION_B1.md](IMPLEMENTATION_B1.md)** - B1 detailed guide
3. **[QUICKSTART.md](QUICKSTART.md)** - B2 quick start
4. **[ARCHITECTURE.md](ARCHITECTURE.md)** - B2 architecture

### **Interactive API Docs**
```
http://localhost:8001/docs
```

### **Test Endpoints**
```bash
# Run comprehensive tests
pytest tests/ -v --tb=short
```

### **Check Logs**
```bash
# View recent errors
tail -50 logs/ai_ml_*.log | grep ERROR
```

---

## 🚀 You're Ready!

**Your complete AI/ML module is now operational with:**

✅ **6 AI Models**
- Gemini/GPT for text summarization
- BERT for sentiment analysis
- YOLOv8 for vision
- Isolation Forest for anomalies
- Prophet for forecasting

✅ **10 API Endpoints**
- 3 text processing endpoints
- 2 vision endpoints
- 2 predictive endpoints
- 2 training endpoints
- 2 health check endpoints

✅ **Production Ready**
- Error handling
- Logging
- Monitoring
- Documentation
- Tests

---

**🎉 Congratulations! Your AI/ML module is fully implemented and running!**

For any issues, refer to the troubleshooting section or documentation files.

**Happy coding! 🚀**

---

**Last Updated:** October 25, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
