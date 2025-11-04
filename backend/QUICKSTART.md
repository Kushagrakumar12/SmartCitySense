# ⚡ SmartCitySense Backend - Quick Start Guide

## 🎯 Goal
Get the backend running in **5 minutes** or less!

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Firebase credentials file (from data-ingestion folder)
- [ ] 5 minutes of time

---

## 🚀 Quick Start (3 Steps)

### Step 1: Setup (2 minutes)

```bash
# Navigate to backend folder
cd /Users/kushagrakumar/Desktop/SmartCitySense/backend

# Run setup script
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` file

---

### Step 2: Configure (1 minute)

```bash
# Edit .env file
nano .env
```

**Minimum required changes:**

```env
# Update this line with your Firebase project details
FIREBASE_CREDENTIALS_PATH=../data-ingestion/firebase-credentials.json

# Get FCM key from Firebase Console → Project Settings → Cloud Messaging
FCM_SERVER_KEY=your-actual-fcm-server-key-here

# If AI/ML service runs on different port, update this:
AI_ML_SERVICE_URL=http://localhost:8001
```

**Save and exit** (Ctrl+X, then Y, then Enter)

---

### Step 3: Run (30 seconds)

```bash
# Start the server
./run.sh
```

**That's it! 🎉**

Your backend is now running at:
- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ✅ Verify It's Working

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "backend": "healthy",
    "firebase": "healthy",
    "ai_ml": "unknown"
  }
}
```

### Test 2: List Events
```bash
curl http://localhost:8000/api/events
```

**Expected output:**
```json
{
  "success": true,
  "events": [],
  "total": 0,
  "page": 1
}
```

### Test 3: Interactive Documentation
Open in browser: http://localhost:8000/docs

---

## 🔧 Troubleshooting

### Problem: "Module not found"
```bash
# Solution: Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Firebase credentials not found"
```bash
# Solution: Check the path
ls -la ../data-ingestion/firebase-credentials.json

# If missing, copy it to the right location
# Or update FIREBASE_CREDENTIALS_PATH in .env
```

### Problem: "Port 8000 already in use"
```bash
# Solution: Kill the process
lsof -i :8000
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8080
```

### Problem: AI/ML service connection fails
This is OK for now! The backend will work without it. Just some features won't be available:
- Event summarization
- Image analysis
- Anomaly detection

To fix: Start the AI/ML service in another terminal
```bash
cd ../ai-ml
python main.py
```

---

## 📖 What's Next?

### 1. Explore the API
Visit http://localhost:8000/docs and try out the endpoints!

### 2. Test with Frontend
Update your frontend to connect to `http://localhost:8000/api`

### 3. Read Full Documentation
- **Complete Guide**: `IMPLEMENTATION_GUIDE.md`
- **API Reference**: `API_DOCUMENTATION.md`
- **Complete Summary**: `COMPLETE_SUMMARY.md`

---

## 🎓 Common Use Cases

### List Events Near a Location
```bash
curl "http://localhost:8000/api/events?latitude=12.9716&longitude=77.5946&radius_km=5"
```

### Filter Events by Category
```bash
curl "http://localhost:8000/api/events?category=Traffic"
```

### Get Health Status
```bash
curl http://localhost:8000/health
```

---

## 🛑 Stop the Server

Press `Ctrl + C` in the terminal where the server is running.

---

## 🔄 Restart the Server

```bash
./run.sh
```

---

## 📊 What You Have

✅ **28+ API endpoints** ready to use
✅ **Interactive documentation** at /docs
✅ **Firebase integration** for auth & data
✅ **AI/ML integration** for smart features
✅ **Push notifications** via FCM
✅ **Geospatial queries** for location-based features
✅ **Production-ready** with security features

---

## 🎯 Quick Commands Reference

```bash
# Setup (first time only)
./setup.sh

# Verify setup
./verify.sh

# Start server
./run.sh

# Stop server
Ctrl + C

# Check if running
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs  # macOS
# or just visit http://localhost:8000/docs in browser
```

---

## 🆘 Need Help?

1. **Run verification script**: `./verify.sh`
2. **Check logs**: Look at terminal output
3. **Read full guide**: `IMPLEMENTATION_GUIDE.md`
4. **Check API docs**: http://localhost:8000/docs

---

## 🎉 Success!

If you can see the Swagger UI at http://localhost:8000/docs, you're all set!

**Your backend is ready to power the SmartCitySense application!**

---

## 📝 Important URLs

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Alternative Docs | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

**Time to completion: ~5 minutes** ⏱️

**Next step: Connect your frontend! 🚀**
