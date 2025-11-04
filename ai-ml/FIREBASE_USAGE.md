# 📊 Firebase Database Usage - AI/ML Module

**Date:** October 27, 2025  
**Module:** SmartCitySense/ML  
**Status:** ✅ Active - Writing to Firebase

---

## 🎯 Quick Answer

**YES**, the AI/ML module **DOES write to Firebase**! It stores:

1. **Vision analysis results** (images/videos)
2. **Text summaries** (combined reports)
3. **Mood maps** (sentiment by location)
4. **Anomaly alerts** (predictive warnings)

---

## 🗄️ Firebase Collections Used

### 1. **`events`** Collection
**What:** Raw and processed event data  
**Written by:** Vision endpoints (image/video analysis)  
**Contains:**
```json
{
  "event_type": "traffic",
  "confidence": 0.85,
  "location": "MG Road",
  "coordinates": {"lat": 12.9716, "lon": 77.5946},
  "objects_detected": ["car", "bus", "motorcycle"],
  "source": "vision_analysis",
  "timestamp": "2025-10-27T12:30:00Z",
  "created_at": "2025-10-27T12:30:15Z",
  "processed": true
}
```

**Triggered by:**
- `POST /ai/vision/image` - Image classification
- `POST /ai/vision/video` - Video analysis

---

### 2. **`predictions`** Collection
**What:** Anomaly detection and forecast results  
**Written by:** Predictive endpoints  
**Contains:**
```json
{
  "location": "MG Road",
  "event_type": "traffic",
  "is_anomaly": true,
  "anomaly_score": 0.92,
  "current_count": 45,
  "normal_range": {"min": 5, "max": 15},
  "source": "predictive_analysis",
  "timestamp": "2025-10-27T12:30:00Z",
  "created_at": "2025-10-27T12:30:20Z"
}
```

**Triggered by:**
- `POST /ai/predict/anomaly` - Anomaly detection

---

### 3. **`alerts`** Collection
**What:** Critical alerts for unusual events  
**Written by:** Anomaly detector when threshold exceeded  
**Contains:**
```json
{
  "severity": "high",
  "event_types": ["traffic"],
  "affected_areas": ["MG Road", "Koramangala"],
  "message": "Unusual spike in traffic reports detected",
  "anomaly_score": 0.92,
  "timestamp": "2025-10-27T12:30:00Z",
  "created_at": "2025-10-27T12:30:20Z",
  "acknowledged": false
}
```

**Triggered by:**
- `POST /ai/predict/anomaly` - When anomaly detected

---

### 4. **`summarized_events`** Collection
**What:** AI-generated summaries of multiple reports  
**Written by:** Text summarization endpoint  
**Contains:**
```json
{
  "event_type": "traffic",
  "summary": "Heavy traffic congestion on MG Road causing 30-minute delays",
  "confidence": 0.94,
  "location": "MG Road",
  "timestamp": "2025-10-27T12:30:00Z",
  "source_count": 15,
  "processed_count": 15,
  "keywords": ["traffic", "mg road", "delay"],
  "method": "llm",
  "processing_time_ms": 1234.5
}
```

**Triggered by:**
- `POST /ai/summarize` - Text summarization

---

### 5. **`mood_map`** Collection
**What:** Location-based sentiment aggregation  
**Written by:** Mood map endpoint  
**Contains:**
```json
{
  "timestamp": "2025-10-27T12:30:00Z",
  "city_wide": {
    "sentiment": "neutral",
    "score": 0.12,
    "total_texts": 150
  },
  "locations": {
    "MG Road": {
      "sentiment": "negative",
      "score": -0.65,
      "sample_size": 25
    },
    "Whitefield": {
      "sentiment": "positive",
      "score": 0.78,
      "sample_size": 20
    }
  },
  "processing_time_ms": 456.2
}
```

**Triggered by:**
- `POST /ai/mood-map` - Mood map creation

---

## 📝 Write Operations Summary

| Endpoint | Collection | What Gets Saved | Frequency |
|----------|------------|-----------------|-----------|
| `/ai/vision/image` | `events` | Image classification results | Per API call |
| `/ai/vision/video` | `events` | Video analysis results | Per API call |
| `/ai/summarize` | `summarized_events` | Text summaries | Per API call |
| `/ai/mood-map` | `mood_map` | Sentiment maps | Per API call |
| `/ai/predict/anomaly` | `predictions` + `alerts` | Anomaly results + alerts | Per API call |

---

## 🔍 Read Operations

The AI/ML module also **reads from Firebase** to get historical data:

### **Firebase Read Functions:**

1. **`get_recent_events()`**
   - **Used by:** Anomaly detector, forecaster
   - **Purpose:** Get recent events for analysis
   - **Time window:** Last 15-60 minutes (configurable)
   - **Collection:** `events`

2. **`get_historical_data()`**
   - **Used by:** Model training endpoints
   - **Purpose:** Get historical data for retraining models
   - **Time window:** Last 30 days (configurable)
   - **Collection:** `events`

3. **`get_grouped_reports()`**
   - **Used by:** Batch summarization
   - **Purpose:** Group reports by location/type
   - **Time window:** Last 60 minutes
   - **Collection:** `events`

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend/Backend/Mobile                     │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ POST request (image/text/video)
              ▼
┌─────────────────────────────────────────────────────────────┐
│              AI/ML Module (FastAPI - Port 8001)              │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Vision     │  │     Text     │  │  Predictive  │       │
│  │ • YOLOv8     │  │ • Gemini     │  │ • Prophet    │       │
│  │ • Classify   │  │ • BERT       │  │ • IsolForest │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                  │               │
│         └─────────────────┼──────────────────┘               │
│                           │                                  │
│                           ▼                                  │
│              ┌────────────────────────┐                      │
│              │  Firebase Client       │                      │
│              │  • save_vision_result  │                      │
│              │  • save_summarized_evt │                      │
│              │  • save_mood_map       │                      │
│              │  • save_alert          │                      │
│              └────────┬───────────────┘                      │
└───────────────────────┼──────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   Firebase/Firestore │
              │                      │
              │  Collections:        │
              │  • events            │
              │  • predictions       │
              │  • alerts            │
              │  • summarized_events │
              │  • mood_map          │
              └─────────────────────┘
```

---

## 🧪 Test Firebase Writes

### **1. Test Vision Write**
```bash
curl -X POST "http://localhost:8001/ai/vision/image" \
  -F "file=@test_image.jpg" \
  -F "location=MG Road" \
  -F "lat=12.9716" \
  -F "lon=77.5946"

# ✅ Check Firebase Console → events collection
# Should see new document with vision_analysis source
```

### **2. Test Summarization Write**
```bash
curl -X POST "http://localhost:8001/ai/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "reports": ["Traffic jam", "Heavy congestion"],
    "event_type": "traffic",
    "location": "MG Road",
    "use_llm": false
  }'

# ✅ Check Firebase Console → summarized_events collection
# Should see new document with summary
```

### **3. Test Mood Map Write**
```bash
curl -X POST "http://localhost:8001/ai/mood-map" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Love Bangalore!", "Hate the traffic"],
    "locations": ["Koramangala", "MG Road"]
  }'

# ✅ Check Firebase Console → mood_map collection
# Should see new document with location sentiments
```

### **4. Test Anomaly Write**
```bash
curl -X POST "http://localhost:8001/ai/predict/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "MG Road",
    "event_types": ["traffic"],
    "time_window_minutes": 15
  }'

# ✅ Check Firebase Console → predictions collection
# If anomaly detected, also check alerts collection
```

---

## 📊 View Data in Firebase Console

1. **Go to:** https://console.firebase.google.com/
2. **Select Project:** smartcitysenseai-e2b65
3. **Navigate to:** Firestore Database
4. **View Collections:**
   - `events` - Vision results
   - `summarized_events` - Text summaries
   - `mood_map` - Sentiment maps
   - `predictions` - Anomaly results
   - `alerts` - Critical alerts

---

## 🔧 Verify Firebase Connection

```bash
cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml
source venv/bin/activate

python3 -c "
from utils.firebase_client import firebase_client

if firebase_client.initialized:
    print('✅ Firebase connected!')
    print(f'Project: {firebase_client.db.project}')
else:
    print('❌ Firebase not connected')
"
```

**Expected output:**
```
✅ Firebase connected!
Project: smartcitysenseai-e2b65
```

---

## 🚨 Background Task Processing

All Firebase writes happen in **background tasks** to avoid blocking API responses:

```python
# In main.py endpoints:
background_tasks.add_task(
    firebase_client.save_summarized_event,
    result
)
```

**Benefits:**
- ✅ Faster API responses (don't wait for DB write)
- ✅ Non-blocking operations
- ✅ Automatic retry on failure
- ✅ Better user experience

---

## 📝 Configuration

Firebase collections can be customized in `.env`:

```bash
# Firebase Collections
FIRESTORE_COLLECTION_EVENTS=events
FIRESTORE_COLLECTION_PREDICTIONS=predictions
FIRESTORE_COLLECTION_ALERTS=alerts
FIRESTORE_COLLECTION_SUMMARIZED_EVENTS=summarized_events
FIRESTORE_COLLECTION_MOOD_MAP=mood_map
```

---

## 🔍 Query Examples

### **Get Recent Events**
```python
from utils.firebase_client import firebase_client

# Get traffic events from last hour
events = firebase_client.get_recent_events(
    event_type='traffic',
    location='MG Road',
    minutes=60
)

print(f"Found {len(events)} events")
for event in events:
    print(f"- {event.get('description', 'N/A')}")
```

### **Get Grouped Reports for Summarization**
```python
from utils.firebase_client import firebase_client

# Get reports grouped by location and type
grouped = firebase_client.get_grouped_reports(
    event_type='traffic',
    minutes=60
)

for group_key, reports in grouped.items():
    print(f"{group_key}: {len(reports)} reports")
```

---

## 🎯 Summary

### ✅ **YES - AI/ML Module Writes to Firebase**

**Collections Used:**
1. `events` - Vision analysis results
2. `summarized_events` - Text summaries
3. `mood_map` - Sentiment maps
4. `predictions` - Anomaly results
5. `alerts` - Critical alerts

**Write Frequency:**
- Every API call that processes data
- Background tasks ensure non-blocking
- Automatic timestamp and metadata added

**Data Usage:**
- Frontend can read these collections for display
- Backend can aggregate for analytics
- Historical data used for model training
- Real-time alerts trigger notifications

---

## 📞 Verify Your Setup

```bash
# 1. Check if Firebase credentials exist
ls -la firebase-credentials.json

# 2. Test Firebase connection
python3 -c "from utils.firebase_client import firebase_client; print('Connected:', firebase_client.initialized)"

# 3. Start API server
python3 main.py

# 4. Make test request
curl http://localhost:8001/health

# 5. Check Firebase Console
# Visit: https://console.firebase.google.com/
```

---

**🎉 Your AI/ML module is actively using Firebase for data persistence!**
