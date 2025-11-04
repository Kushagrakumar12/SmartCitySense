# 🚀 Quick Start Guide - AI/ML Module

Complete setup guide from zero to running API server.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional)
- 8GB+ RAM recommended
- CUDA-capable GPU (optional, for faster processing)

## Step 1: Environment Setup

### macOS/Linux

```bash
# Navigate to AI-ML directory
cd ai-ml

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Windows

```powershell
# Navigate to AI-ML directory
cd ai-ml

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

## Step 2: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# This will install:
# - PyTorch & torchvision (deep learning)
# - Ultralytics (YOLOv8)
# - OpenCV (image/video processing)
# - FastAPI & uvicorn (API server)
# - scikit-learn (ML algorithms)
# - Prophet (time series forecasting)
# - Firebase Admin SDK
# - And more...

# Installation may take 5-10 minutes
```

### Optional: GPU Support

If you have an NVIDIA GPU with CUDA:

```bash
# Uninstall CPU-only PyTorch
pip uninstall torch torchvision

# Install CUDA-enabled PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Verify GPU detection
python -c "import torch; print('GPU Available:', torch.cuda.is_available())"
```

## Step 3: Configuration

### Create Environment File

```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env  # or use any text editor
```

### Minimal .env Configuration

```bash
# Firebase (if you have credentials)
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=smartcitysense

# Model Settings (defaults are fine for testing)
YOLO_MODEL_SIZE=n
VISION_CONFIDENCE_THRESHOLD=0.65

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
API_RELOAD=True

# Development
ENVIRONMENT=development
MOCK_MODE=False
SAVE_DEBUG_IMAGES=True
```

### Optional: Firebase Setup

If you have Firebase credentials:

1. Download your Firebase service account key
2. Save it as `firebase-credentials.json` in the `ai-ml/` directory
3. Update `.env` with the path

If you don't have Firebase, the system will run in mock mode (no database operations).

## Step 4: Test Configuration

```bash
# Test configuration loading
python config/config.py

# Expected output:
# ============================================================
# 🤖 AI/ML Module Configuration
# ============================================================
# Environment: development
# Device: cuda (GPU Available: True/False)
# ...
```

## Step 5: Download Models

Models are downloaded automatically on first run, but you can pre-download:

```bash
# Create models directory
mkdir -p models

# Download YOLOv8 nano model (happens automatically, ~6MB)
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# The model will be cached in models/ directory
```

## Step 6: Run Tests

```bash
# Run basic tests to verify installation
pytest tests/test_vision.py::TestImageClassifier::test_initialization -v

# If successful, you'll see:
# tests/test_vision.py::TestImageClassifier::test_initialization PASSED
```

## Step 7: Start the API Server

```bash
# Start server in development mode
python main.py

# You should see:
# ============================================================
# 🚀 Starting SmartCitySense - AI/ML API Server
# ============================================================
# ...
# INFO:     Uvicorn running on http://0.0.0.0:8001
```

## Step 8: Test the API

### Open API Documentation

Visit http://localhost:8001/docs in your browser to see interactive API documentation.

### Test Health Endpoint

```bash
# Terminal
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-11T10:30:00Z",
  "version": "1.0.0",
  "models_loaded": {...},
  "gpu_available": true/false
}
```

### Test Vision Analysis

```bash
# Prepare a test image
# Download or use any JPG/PNG image

# Analyze image
curl -X POST \
  -F "file=@test_image.jpg" \
  -F "location=Test Location" \
  http://localhost:8001/ai/vision/image

# Expected response:
{
  "event_type": "traffic",
  "description": "Traffic situation with car, truck detected",
  "confidence": 0.87,
  "severity": "medium",
  "detected_objects": [...],
  ...
}
```

### Test Anomaly Detection

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"location":"MG Road","time_window_minutes":15}' \
  http://localhost:8001/ai/predict/anomaly

# Expected response:
{
  "severity": "low",
  "anomaly_result": {
    "is_anomaly": false,
    "anomaly_score": 0.0,
    "event_count": 0,
    ...
  },
  ...
}
```

## Step 9: Interactive Testing with Python

```python
# Create test_api.py
import requests
import json

# Test health
response = requests.get('http://localhost:8001/health')
print('Health:', response.json()['status'])

# Test image analysis
with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/ai/vision/image',
        files={'file': ('test.jpg', f, 'image/jpeg')},
        data={'location': 'MG Road'}
    )
    result = response.json()
    print(f"\nEvent Detected: {result['event_type']}")
    print(f"Description: {result['description']}")
    print(f"Confidence: {result['confidence']:.2%}")
```

Run it:
```bash
python test_api.py
```

## Common Issues & Solutions

### Issue 1: Import Errors

**Problem**: Red squiggly lines in VS Code
**Solution**: 
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: Port Already in Use

**Problem**: `Address already in use`
**Solution**:
```bash
# Change port in .env
echo "API_PORT=8002" >> .env

# Or kill process using port 8001
lsof -ti:8001 | xargs kill -9  # macOS/Linux
```

### Issue 3: YOLO Model Download Failed

**Problem**: Model download times out
**Solution**:
```bash
# Manual download
mkdir -p models
cd models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Or use smaller model
echo "YOLO_MODEL_SIZE=n" >> ../.env
```

### Issue 4: Out of Memory

**Problem**: GPU/RAM exhausted
**Solution**:
```bash
# Use CPU instead
echo "USE_GPU=False" >> .env

# Reduce image size
echo "MAX_IMAGE_SIZE=640" >> .env

# Reduce batch size
echo "BATCH_SIZE=16" >> .env
```

### Issue 5: Firebase Connection Failed

**Problem**: Firebase authentication error
**Solution**:
```bash
# Run without Firebase (mock mode)
echo "MOCK_MODE=True" >> .env

# Or verify credentials file exists
ls -la firebase-credentials.json
```

## Next Steps

1. **Read ARCHITECTURE.md** - Understand system design
2. **Explore API docs** - http://localhost:8001/docs
3. **Train models** - Use historical data to train predictive models
4. **Integrate with backend** - Connect to Member D's API
5. **Test with real data** - Upload actual city images/videos

## Development Workflow

```bash
# 1. Start server with auto-reload
python main.py

# 2. Make code changes (server auto-restarts)

# 3. Test changes
curl http://localhost:8001/health

# 4. Run tests
pytest tests/ -v

# 5. Check logs
tail -f logs/ai_ml_*.log
```

## Production Deployment

For production:

```bash
# Disable debug features
sed -i 's/API_RELOAD=True/API_RELOAD=False/' .env
sed -i 's/SAVE_DEBUG_IMAGES=True/SAVE_DEBUG_IMAGES=False/' .env
sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env

# Run with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

# Or use gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## Testing Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list` shows all packages)
- [ ] Configuration file created (`.env` exists)
- [ ] API server starts without errors
- [ ] Health endpoint responds (200 OK)
- [ ] Image analysis works (with test image)
- [ ] Tests pass (`pytest tests/`)
- [ ] Logs are being written (`logs/` directory)
- [ ] Models are loaded (check `/health` response)

## Performance Benchmarks

**Expected Performance** (on modern hardware):

| Operation | CPU | GPU |
|-----------|-----|-----|
| Image Classification | 1-2 sec | 0.2-0.3 sec |
| Video Analysis (30 frames) | 30-60 sec | 5-10 sec |
| Anomaly Detection | 0.5-1 sec | 0.5-1 sec |
| Forecasting (24h) | 2-5 sec | 2-5 sec |

## Getting Help

- **API Issues**: Check http://localhost:8001/docs for endpoint specs
- **Model Issues**: Review logs in `logs/ai_ml_*.log`
- **Configuration**: Run `python config/config.py` to verify settings
- **Tests**: Run `pytest tests/ -v --tb=short` for detailed errors

---

**You're all set! 🎉**

The AI/ML module is now ready to analyze city events and generate predictions.

Next: Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand how everything works together.
