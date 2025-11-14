# SmartCitySense Backend - Complete Implementation Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Backend](#running-the-backend)
5. [API Testing](#api-testing)
6. [Integration with Other Services](#integration-with-other-services)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Before setting up the backend, ensure you have:

### Required Software
- **Python 3.11 or higher**
- **pip** (Python package manager)
- **Git**

### Required Services
1. **Firebase Project**
   - Firebase credentials JSON file (from data-ingestion setup)
   - Firebase Cloud Messaging (FCM) server key

2. **AI/ML Service**
   - The ai-ml service should be running on port 8001
   - See `ai-ml/README.md` for setup instructions

3. **Data Ingestion Service** (Optional but recommended)
   - For real-time event data
   - Should be configured to write to the same Firebase project

---

## 📦 Installation

### Step 1: Navigate to Backend Directory

```bash
cd /Users/kushagrakumar/Desktop/citypulseAI/backend
```

### Step 2: Run Setup Script

```bash
# Make scripts executable
chmod +x setup.sh run.sh

# Run setup
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all required dependencies
- Create a `.env` file from template

### Step 3: Manual Installation (Alternative)

If the setup script doesn't work:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### Step 1: Environment Variables

Edit the `.env` file created during setup:

```bash
nano .env  # or use any text editor
```

**Minimum Required Configuration:**

```env
# App Configuration
APP_NAME="SmartCitySense Backend"
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Firebase Configuration (CRITICAL)
FIREBASE_CREDENTIALS_PATH=../data-ingestion/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project.appspot.com

# FCM (Firebase Cloud Messaging) - Required for notifications
FCM_SERVER_KEY=your-fcm-server-key-here

# AI/ML Service URLs
AI_ML_SERVICE_URL=http://localhost:8001
SUMMARIZATION_ENDPOINT=/api/summarize
VISION_ANALYSIS_ENDPOINT=/api/analyze/image
SENTIMENT_ENDPOINT=/api/sentiment
ANOMALY_DETECTION_ENDPOINT=/api/anomaly/detect

# Security
SECRET_KEY=change-this-to-a-random-secure-string-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins (Update with your frontend URL)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Redis (Optional - for background jobs)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Step 2: Firebase Credentials

Ensure Firebase credentials are available:

```bash
# Check if credentials exist
ls -la ../data-ingestion/firebase-credentials.json

# If not present, copy from data-ingestion folder
# Or download from Firebase Console:
# Project Settings > Service Accounts > Generate New Private Key
```

### Step 3: Get FCM Server Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings > Cloud Messaging
4. Copy the **Server Key**
5. Add it to `.env` as `FCM_SERVER_KEY`

---

## 🚀 Running the Backend

### Option 1: Using Run Script (Recommended)

```bash
./run.sh
```

This starts the server with auto-reload enabled (for development).

### Option 2: Manual Start

```bash
# Activate virtual environment
source venv/bin/activate

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Production Mode

```bash
# Without auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Backend is Running

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "timestamp": "...",
#   "services": {
#     "backend": "healthy",
#     "firebase": "healthy",
#     "ai_ml": "healthy"
#   }
# }
```

### Access API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧪 API Testing

### 1. Test Without Authentication

```bash
# List events (public endpoint)
curl http://localhost:8000/api/events

# Get events by category
curl http://localhost:8000/api/events?category=Traffic

# Get events near location
curl "http://localhost:8000/api/events?latitude=12.9716&longitude=77.5946&radius_km=5"
```

### 2. Test With Firebase Authentication

First, get a Firebase ID token from your frontend or using Firebase SDK:

```bash
# Using curl with authentication
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN"
```

### 3. Submit a Report

```bash
curl -X POST http://localhost:8000/api/reports \
  -H "Authorization: Bearer YOUR_FIREBASE_ID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Report",
    "description": "Testing report submission",
    "category": "Civic Issue",
    "location": {
      "latitude": 12.9716,
      "longitude": 77.5946,
      "address": "Test Location"
    }
  }'
```

### 4. Using Postman or Thunder Client

Import the API from Swagger JSON:
```bash
http://localhost:8000/openapi.json
```

---

## 🔗 Integration with Other Services

### With AI/ML Service

**Ensure AI/ML service is running:**

```bash
# In another terminal, start AI/ML service
cd ../ai-ml
source venv/bin/activate
python main.py
```

**Test integration:**

```bash
# Trigger anomaly detection
curl -X POST http://localhost:8000/api/alerts/detect-anomalies?time_window=1h \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create summary
curl -X POST http://localhost:8000/api/summaries \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_ids": ["event1", "event2", "event3"]
  }'
```

### With Data Ingestion

Data from ingestion pipelines automatically appears in events:

```bash
# Start data ingestion in another terminal
cd ../data-ingestion
python main.py
```

Events will be stored in Firebase and accessible via:
```bash
curl http://localhost:8000/api/events
```

### With Frontend

Update frontend API configuration to point to backend:

```javascript
// frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:8000/api';

export const getEvents = async () => {
  const response = await fetch(`${API_BASE_URL}/events`);
  return response.json();
};
```

---

## 📦 Docker Deployment

### Build Docker Image

```bash
# From backend directory
docker build -t citypulse-backend .
```

### Run with Docker

```bash
docker run -d \
  --name citypulse-backend \
  -p 8000:8000 \
  -e FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json \
  -e AI_ML_SERVICE_URL=http://host.docker.internal:8001 \
  -v $(pwd)/../data-ingestion/firebase-credentials.json:/app/firebase-credentials.json \
  citypulse-backend
```

### Docker Compose (Full Stack)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AI_ML_SERVICE_URL=http://ai-ml:8001
      - FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
    volumes:
      - ./data-ingestion/firebase-credentials.json:/app/firebase-credentials.json
    depends_on:
      - ai-ml

  ai-ml:
    build: ./ai-ml
    ports:
      - "8001:8001"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api
```

Run:
```bash
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Firebase authentication fails

**Solution:**
1. Check `firebase-credentials.json` path in `.env`
2. Verify file exists and is valid JSON
3. Check Firebase project configuration

```bash
# Validate credentials file
python -c "import json; print(json.load(open('../data-ingestion/firebase-credentials.json'))['project_id'])"
```

### Issue: AI/ML service connection refused

**Solution:**
1. Ensure AI/ML service is running:
```bash
curl http://localhost:8001/health
```

2. Check AI_ML_SERVICE_URL in `.env`
3. Start AI/ML service if not running

### Issue: "Rate limit exceeded"

**Solution:**
- Increase `RATE_LIMIT_PER_MINUTE` in `.env`
- Or use authentication for higher limits

### Issue: CORS errors from frontend

**Solution:**
Add frontend URL to `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://your-frontend-url
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8080
```

### Check Logs

```bash
# View recent logs
tail -f logs/backend.log

# Or check console output when running with uvicorn
```

---

## 📊 Monitoring & Health Checks

### Health Check

```bash
curl http://localhost:8000/health
```

### Check Service Status

```bash
# Check if backend is running
curl http://localhost:8000/

# Check specific service health
curl http://localhost:8000/health | jq '.services'
```

### Metrics (Optional)

For production, add monitoring:
- Prometheus metrics endpoint
- Grafana dashboards
- Error tracking (Sentry)

---

## 🔐 Security Best Practices

### For Production Deployment:

1. **Change SECRET_KEY** to a strong random string
2. **Disable DEBUG** mode (`DEBUG=false`)
3. **Use HTTPS** only
4. **Restrict CORS** to specific domains
5. **Use environment-specific** `.env` files
6. **Secure Firebase credentials** (use secrets management)
7. **Enable rate limiting**
8. **Set up monitoring** and alerts

---

## 📝 API Usage Examples

### JavaScript (Frontend)

```javascript
// Get events near user location
const getEventsNearMe = async (lat, lng) => {
  const response = await fetch(
    `http://localhost:8000/api/events?latitude=${lat}&longitude=${lng}&radius_km=5`
  );
  return response.json();
};

// Submit report with authentication
const submitReport = async (reportData, token) => {
  const response = await fetch('http://localhost:8000/api/reports', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(reportData)
  });
  return response.json();
};

// Update user subscriptions
const updateSubscriptions = async (subscriptions, token) => {
  const response = await fetch('http://localhost:8000/api/auth/subscriptions', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(subscriptions)
  });
  return response.json();
};
```

### Python (Testing/Automation)

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get events
def get_events(category=None):
    params = {}
    if category:
        params['category'] = category
    
    response = requests.get(f"{BASE_URL}/events", params=params)
    return response.json()

# Submit authenticated request
def get_profile(firebase_token):
    headers = {'Authorization': f'Bearer {firebase_token}'}
    response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    return response.json()
```

---

## 🎯 Next Steps

1. **Test all endpoints** using Swagger UI
2. **Connect frontend** to backend APIs
3. **Set up notifications** with FCM
4. **Configure monitoring** for production
5. **Write custom tests** for your use cases
6. **Deploy to cloud** (GCP, AWS, or Azure)

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [Project README](../README.md)

---

## 💡 Tips

- Use **Swagger UI** (`/docs`) for interactive API testing
- Check **health endpoint** (`/health`) before debugging
- Enable **DEBUG mode** during development for detailed errors
- Use **Postman** or **Thunder Client** for API testing
- Check **logs** for error details

---

## ✅ Checklist

Before going live, ensure:

- [ ] Firebase credentials configured
- [ ] FCM server key added
- [ ] AI/ML service running and accessible
- [ ] All environment variables set
- [ ] CORS configured for frontend
- [ ] Rate limiting enabled
- [ ] Health check returns "healthy"
- [ ] API documentation accessible
- [ ] Tests passing
- [ ] Security best practices followed

---

## 🆘 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review error logs
3. Test individual components
4. Verify environment configuration
5. Check Firebase console for issues

For more help, refer to the main project documentation or create an issue in the repository.

---

**Backend is now ready! 🎉**

Your backend should be running on http://localhost:8000 with full API documentation at http://localhost:8000/docs
