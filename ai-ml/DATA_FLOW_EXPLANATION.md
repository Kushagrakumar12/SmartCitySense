# 🔄 Data Flow: How AI-ML Gets Data from Data-Ingestion

**Date:** October 27, 2025  
**Critical Question:** How does the AI-ML folder receive data from the data-ingestion folder?

---

## 🎯 **Short Answer**

The `ai-ml` folder does **NOT directly** get data from the `data-ingestion` folder.

Instead, they communicate through **Firebase Firestore** (a cloud database) as the middle layer:

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│ data-ingestion/ │  writes │   Firebase   │  reads  │    ai-ml/       │
│  (Person A)     │ ──────► │  Firestore   │ ◄────── │  (Members B1/B2)│
│                 │         │  (Cloud DB)  │         │                 │
└─────────────────┘         └──────────────┘         └─────────────────┘
```

**This is called a "decoupled architecture"** - the two modules don't talk directly to each other!

---

## 📊 **The Complete Data Flow**

### **Step-by-Step Journey of a Traffic Event:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE DATA FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: DATA COLLECTION (data-ingestion folder)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9:00 AM - Traffic jam happens on MG Road

    ├─► Google Maps API detects it
    │       ↓
    │   traffic_api.py (connector)
    │       ↓
    │   Creates Event object:
    │   {
    │     "type": "traffic",
    │     "source": "google_maps",
    │     "description": "Heavy traffic on MG Road",
    │     "location": "MG Road",
    │     "severity": "high",
    │     "timestamp": "2025-10-27T09:00:00Z"
    │   }
    │
    └─► Twitter users tweet about it
    │       ↓
    │   twitter_api.py (connector)
    │       ↓
    │   Creates Event object:
    │   {
    │     "type": "social",
    │     "source": "twitter",
    │     "description": "@blrcitypolice MG Road traffic is terrible!",
    │     "location": "MG Road",
    │     "timestamp": "2025-10-27T09:01:00Z"
    │   }

STEP 2: DATA STORAGE (data-ingestion/pipelines/)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    main.py runs:
        ↓
    firebase_producer.py
        ↓
    FirebaseProducer.send_event()
        ↓
    ┌─────────────────────────────────────┐
    │  Firebase Firestore (Cloud)         │
    │  ─────────────────────────────────  │
    │  Collection: "smartcitysense_events"     │
    │                                      │
    │  Document 1:                         │
    │  {                                   │
    │    "id": "evt_001",                  │
    │    "type": "traffic",                │
    │    "source": "google_maps",          │
    │    "description": "Heavy traffic...", │
    │    "location": "MG Road",            │
    │    "timestamp": "2025-10-27T09:00"   │
    │  }                                   │
    │                                      │
    │  Document 2:                         │
    │  {                                   │
    │    "id": "evt_002",                  │
    │    "source": "twitter",              │
    │    "description": "MG Road jam!",    │
    │    ...                               │
    │  }                                   │
    └─────────────────────────────────────┘
            ▲
            │
        ✅ DATA NOW IN CLOUD!
        Anyone can read it from anywhere!


STEP 3: DATA PROCESSING (ai-ml folder)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Option A: Backend calls AI-ML API
    ↓
Backend sends request to ai-ml:
    POST http://localhost:8001/ai/predict/anomaly
    {
      "location": "MG Road",
      "time_window_minutes": 60
    }
    ↓
AI-ML receives request in main.py
    ↓
main.py calls:
    firebase_client.get_recent_events(
        location="MG Road",
        minutes=60
    )
    ↓
firebase_client.py (ai-ml/utils/)
    ↓
    ┌─────────────────────────────────────┐
    │  Firebase Firestore (Cloud)         │
    │  ─────────────────────────────────  │
    │  READ from "smartcitysense_events"       │
    │  WHERE location = "MG Road"         │
    │  WHERE timestamp > (now - 60 min)   │
    │                                      │
    │  Returns: 50 events                  │
    └─────────────────────────────────────┘
    ↓
AI-ML analyzes the 50 events:
    - Text Summarizer combines descriptions
    - Sentiment Analyzer checks mood
    - Anomaly Detector finds unusual patterns
    ↓
Result:
    {
      "is_anomaly": true,
      "anomaly_score": 0.92,
      "summary": "Heavy traffic on MG Road",
      "sentiment": "negative",
      "alert_type": "traffic_spike"
    }
    ↓
AI-ML saves result back to Firebase:
    firebase_client.save_alert(result)
    ↓
    ┌─────────────────────────────────────┐
    │  Firebase Firestore (Cloud)         │
    │  ─────────────────────────────────  │
    │  Collection: "alerts"               │
    │                                      │
    │  New Document:                       │
    │  {                                   │
    │    "alert_id": "alert_001",          │
    │    "type": "traffic_spike",          │
    │    "location": "MG Road",            │
    │    "severity": "high",               │
    │    "created_at": "2025-10-27T09:02"  │
    │  }                                   │
    └─────────────────────────────────────┘
    ↓
Backend reads alerts from Firebase
    ↓
Frontend displays alert to users!
```

**Total Time: 2-3 minutes from event to alert!** ⚡

---

## 🔑 **Key Files Involved**

### **📁 data-ingestion/ (Person A)**

#### **1. pipelines/firebase_producer.py**
```python
class FirebaseProducer:
    """Writes events TO Firebase"""
    
    def send_event(self, event: Event) -> bool:
        # Convert event to dictionary
        event_data = event.to_dict()
        
        # Save to Firestore collection
        doc_ref = self.db.collection("smartcitysense_events").document(event.id)
        doc_ref.set(event_data)
        
        logger.info(f"Event {event.id} saved to Firebase")
```

**What it does:**
- ✍️ **WRITES** events to Firebase
- Collection name: `smartcitysense_events`
- Runs in `data-ingestion/main.py`

---

### **📁 ai-ml/ (Members B1 & B2)**

#### **2. utils/firebase_client.py**
```python
class FirebaseClient:
    """Reads/writes data from/to Firebase"""
    
    def get_recent_events(self, location, minutes=60):
        """READ events from Firebase"""
        
        # Query Firestore
        query = self.db.collection("smartcitysense_events")
        query = query.where("location", "==", location)
        query = query.where("timestamp", ">=", time_threshold)
        
        # Execute and return
        docs = query.stream()
        events = [doc.to_dict() for doc in docs]
        
        return events
    
    def save_alert(self, alert_data):
        """WRITE alerts back to Firebase"""
        self.db.collection("alerts").add(alert_data)
```

**What it does:**
- 📖 **READS** events from Firebase (`get_recent_events`)
- 📖 **READS** historical data (`get_historical_data`)
- 📖 **READS** grouped reports (`get_grouped_reports`)
- ✍️ **WRITES** results back (`save_alert`, `save_summarized_event`, `save_mood_map`)

---

#### **3. main.py (AI-ML API Server)**
```python
@app.post("/ai/predict/anomaly")
async def detect_anomaly(request):
    # Get data from Firebase
    events = firebase_client.get_recent_events(
        location=request.location,
        minutes=request.time_window_minutes
    )
    
    # Analyze with AI
    result = anomaly_detector.detect(events)
    
    # Save result
    if result["is_anomaly"]:
        firebase_client.save_alert(result)
    
    return result
```

**What it does:**
- Provides REST API endpoints
- Calls `firebase_client` to get data
- Processes data with AI models
- Saves results back to Firebase

---

## 🗄️ **Firebase Collections**

Firebase Firestore has multiple "collections" (like database tables):

```
Firebase Firestore Database
├── smartcitysense_events/          ← Written by data-ingestion
│   ├── evt_001
│   ├── evt_002
│   └── evt_003 ...
│
├── alerts/                    ← Written by ai-ml
│   ├── alert_001
│   └── alert_002 ...
│
├── summarized_events/         ← Written by ai-ml (B1)
│   ├── summary_001
│   └── summary_002 ...
│
├── mood_map/                  ← Written by ai-ml (B1)
│   ├── mood_001
│   └── mood_002 ...
│
├── vision_results/            ← Written by ai-ml (B2)
│   ├── vision_001
│   └── vision_002 ...
│
└── predictions/               ← Written by ai-ml (B2)
    ├── prediction_001
    └── prediction_002 ...
```

### **Who Writes What:**

| Collection           | Written By       | Read By          | Purpose                          |
|----------------------|------------------|------------------|----------------------------------|
| `smartcitysense_events`   | data-ingestion   | ai-ml, backend   | Raw events from connectors       |
| `alerts`             | ai-ml            | backend          | Anomaly alerts                   |
| `summarized_events`  | ai-ml (B1)       | backend          | Text summaries                   |
| `mood_map`           | ai-ml (B1)       | backend          | Sentiment analysis results       |
| `vision_results`     | ai-ml (B2)       | backend          | Image/video analysis             |
| `predictions`        | ai-ml (B2)       | backend          | Forecasts and predictions        |

---

## 🔧 **Configuration**

### **data-ingestion/.env**
```bash
# Person A configures this
FIREBASE_PROJECT_ID=smartcitysense
FIREBASE_PRIVATE_KEY_PATH=./firebase-credentials.json
FIREBASE_COLLECTION=smartcitysense_events  # Where to WRITE events
```

### **ai-ml/.env**
```bash
# Members B1/B2 configure this
FIREBASE_PROJECT_ID=smartcitysense
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_EVENTS_COLLECTION=smartcitysense_events  # Where to READ events
FIREBASE_ALERTS_COLLECTION=alerts            # Where to WRITE alerts
FIREBASE_SUMMARIZED_COLLECTION=summarized_events
FIREBASE_MOOD_MAP_COLLECTION=mood_map
```

**⚠️ IMPORTANT:** Both folders need:
1. Same Firebase project ID
2. Same `firebase-credentials.json` file
3. Same collection names

---

## 🎯 **Why This Architecture?**

### **❌ What We DON'T Do (Direct Connection):**
```
┌─────────────────┐
│ data-ingestion/ │ ──X──► ai-ml/ (NO DIRECT CONNECTION!)
└─────────────────┘
```

### **✅ What We DO (Decoupled via Firebase):**
```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│ data-ingestion/ │ ──────► │   Firebase   │ ◄────── │    ai-ml/       │
└─────────────────┘         └──────────────┘         └─────────────────┘
```

### **Benefits:**

1. **Independence** 🔓
   - Both modules can run separately
   - Person A can work without waiting for B1/B2
   - B1/B2 can develop without Person A running

2. **Scalability** 📈
   - Can have multiple AI-ML servers reading same data
   - Firebase handles load balancing
   - Cloud-native architecture

3. **Reliability** 💪
   - If one module crashes, other keeps working
   - Data persists in Firebase
   - No data loss if modules restart

4. **Flexibility** 🎨
   - Easy to add new modules (backend, frontend)
   - Can switch between Kafka and Firebase
   - Can add more connectors or AI models

5. **Real-time** ⚡
   - Firebase supports real-time listeners
   - AI can get notified of new events instantly
   - No polling needed (optional)

---

## 🚀 **How To Run Both Modules Together**

### **Terminal 1: Start Data Ingestion**
```bash
cd /Users/kushagrakumar/Desktop/SmartCitySense/data-ingestion

# Setup (first time only)
./setup.sh

# Configure Firebase
nano .env  # Make sure Firebase credentials are set

# Run in scheduled mode (every 5 minutes)
python main.py --mode scheduled --interval 5 --firebase

# Output:
# ✓ Firebase connected
# ✓ Traffic connector ready
# ✓ Civic portal connector ready
# Running every 5 minutes...
# Collected 25 events, sent to Firebase ✓
```

### **Terminal 2: Start AI-ML Server**
```bash
cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml

# Setup (first time only)
./setup.sh

# Configure Firebase
cp .env.example .env
nano .env  # Same Firebase credentials as data-ingestion

# Start server
python main.py

# Output:
# ✓ Firebase initialized - Project: smartcitysense
# ✓ Server started at http://localhost:8001
# ✓ Docs: http://localhost:8001/docs
```

### **Terminal 3: Test The Connection**
```bash
# Wait for data-ingestion to collect some events (5+ minutes)

# Then test AI-ML anomaly detection
curl -X POST http://localhost:8001/ai/predict/anomaly \
  -H "Content-Type: application/json" \
  -d '{
    "location": "MG Road",
    "time_window_minutes": 60
  }'

# If successful, you'll see:
# {
#   "is_anomaly": true/false,
#   "anomaly_score": 0.85,
#   "events_analyzed": 42,
#   ...
# }

# This proves:
# 1. data-ingestion wrote events to Firebase ✓
# 2. ai-ml read events from Firebase ✓
# 3. ai-ml analyzed the data ✓
# 4. The connection works! ✓
```

---

## 🔍 **Debugging The Connection**

### **Problem: AI-ML says "No events found"**

**Check 1: Is data-ingestion writing to Firebase?**
```bash
cd data-ingestion
python -m pipelines.firebase_producer

# Should see:
# ✓ Connected to Firebase
# ✓ Sent 2 events to Firebase
```

**Check 2: Is Firebase configured correctly?**
```bash
# Both folders should have same config
diff data-ingestion/.env ai-ml/.env

# Should have same:
# - FIREBASE_PROJECT_ID
# - Same firebase-credentials.json file
```

**Check 3: Are collections named correctly?**
```bash
# In data-ingestion/.env:
FIREBASE_COLLECTION=smartcitysense_events

# In ai-ml/.env:
FIREBASE_EVENTS_COLLECTION=smartcitysense_events

# ☝️ Must match!
```

**Check 4: Manually verify Firebase has data**
```bash
cd ai-ml
python -c "
from utils.firebase_client import firebase_client
events = firebase_client.get_recent_events(minutes=1440)  # Last 24 hours
print(f'Found {len(events)} events in Firebase')
if events:
    print('Latest event:', events[0])
else:
    print('No events found - data-ingestion may not be writing')
"
```

---

## 📊 **Data Flow Timing**

Typical timeline for one event:

```
T+0:00  🚗 Traffic jam happens on MG Road
T+0:30  📱 Citizens start tweeting
T+1:00  🔄 data-ingestion scheduled run starts
T+1:05  ✍️  Events written to Firebase
T+1:06  📡 Backend polls for new events
T+1:07  🤖 Backend calls ai-ml API for analysis
T+1:08  📖 ai-ml reads events from Firebase
T+1:10  🧠 AI models process data
T+1:11  ✍️  Results saved to Firebase
T+1:12  📺 Frontend displays alert to users

Total: ~12 minutes from real event to user alert
```

**Where time is spent:**
- Waiting for scheduled run: 0-5 minutes (depends on interval)
- API calls to connectors: 3-5 seconds
- Firebase write: 1-2 seconds
- AI processing: 1-3 seconds
- Firebase read: 1 second

**How to make it faster:**
- Reduce scheduled interval (e.g., every 2 minutes instead of 5)
- Use Firebase real-time listeners (instant notification)
- Cache AI models (already implemented)

---

## 🎓 **Summary**

### **The Key Points:**

1. ✅ **ai-ml does NOT directly access data-ingestion**
2. ✅ **Firebase Firestore is the bridge between them**
3. ✅ **data-ingestion WRITES to Firebase**
4. ✅ **ai-ml READS from Firebase**
5. ✅ **ai-ml WRITES results back to Firebase**
6. ✅ **Backend reads everything from Firebase**
7. ✅ **This is called "decoupled architecture"**

### **The Data Journey:**

```
Real World Event
    ↓
data-ingestion/connectors (collect)
    ↓
data-ingestion/pipelines (normalize)
    ↓
Firebase/smartcitysense_events (store)
    ↓
ai-ml/firebase_client (read)
    ↓
ai-ml/models (analyze)
    ↓
Firebase/alerts,summaries,etc (store results)
    ↓
backend (fetch)
    ↓
frontend (display)
    ↓
Users see alert! 🎉
```

### **Configuration Files:**

Both modules need:
- ✅ Same `FIREBASE_PROJECT_ID`
- ✅ Same `firebase-credentials.json`
- ✅ Matching collection names
- ✅ Internet connection (Firebase is cloud-based)

---

## 🔗 **Related Documentation**

- **data-ingestion/FIREBASE_SETUP.md** - How to setup Firebase for data collection
- **ai-ml/COMPLETE_IMPLEMENTATION_GUIDE.md** - Full AI-ML setup guide
- **ai-ml/FOLDER_EXPLANATION.md** - What each folder/file does
- **README.md** (root) - Complete system overview

---

**Last Updated:** October 27, 2025  
**Author:** GitHub Copilot  
**For:** SmartCitySense Project

**🎯 TL;DR: Firebase is the middleman. data-ingestion writes events to it, ai-ml reads events from it. They never talk directly!**
