# 🔥 Firebase Setup Guide

This guide will help you set up Firebase as an alternative to Kafka for event streaming.

Firebase is simpler to set up and doesn't require running local services.

---

## 📋 Prerequisites

- Google account
- Internet connection
- Python with firebase-admin package

---

## 🚀 Setup Steps

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `citypulse-ai` (or your choice)
4. Disable Google Analytics (not needed for this project)
5. Click **"Create project"**

### Step 2: Enable Firestore Database

1. In Firebase Console, click **"Firestore Database"** in left menu
2. Click **"Create database"**
3. Choose **"Start in production mode"** (we'll adjust rules later)
4. Select location: **asia-south1** (India) or closest to you
5. Click **"Enable"**

### Step 3: Generate Service Account Key

1. Click the **gear icon** ⚙️ next to "Project Overview"
2. Click **"Project settings"**
3. Go to **"Service accounts"** tab
4. Click **"Generate new private key"**
5. Click **"Generate key"** (downloads a JSON file)
6. Save the file as `firebase-credentials.json` in your project:

```bash
# Move the downloaded file
mv ~/Downloads/citypulse-ai-*.json /Users/kushagrakumar/Desktop/citypulseAI/data-ingestion/firebase-credentials.json
```

⚠️ **IMPORTANT:** Add this file to `.gitignore` to keep it secret!

### Step 4: Configure Security Rules

1. In Firestore Database, click **"Rules"** tab
2. Replace with these rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write to events collection
    match /events/{eventId} {
      allow read, write: if true;  // Adjust for production
    }
  }
}
```

3. Click **"Publish"**

### Step 5: Install Firebase SDK

```bash
cd /Users/kushagrakumar/Desktop/citypulseAI/data-ingestion

# Install firebase-admin
pip install firebase-admin

# Update requirements.txt
echo "firebase-admin>=6.0.0" >> requirements.txt
```

### Step 6: Configure Environment Variables

Add to your `.env` file:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=citypulse-ai  # Your project ID
FIREBASE_PRIVATE_KEY_PATH=firebase-credentials.json
```

To get your exact project ID:
1. Go to Firebase Console
2. Click gear icon → Project settings
3. Copy the "Project ID"

---

## ✅ Test Firebase Connection

### Test 1: Run Firebase Producer Test

```bash
cd /Users/kushagrakumar/Desktop/citypulseAI/data-ingestion

# Test Firebase connection
python -m pipelines.firebase_producer
```

Expected output:
```
============================================================
🔥 Firebase Producer Test
============================================================

✓ Connected to Firebase

Sending 2 test events...

✓ Sent 2/2 events

Querying recent events:
1. traffic: Test traffic event for Firebase...
2. civic: Test civic event for Firebase...
```

### Test 2: Run Full Pipeline with Firebase

```bash
# Run one-time ingestion with Firebase
python main.py --mode once --firebase
```

Expected output:
```
✓ Collected 25 events
✓ Sent 25 events
✓ Success rate: 100%
```

---

## 👀 View Events in Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click **"Firestore Database"**
4. You should see an **"events"** collection
5. Click to view all events

Each event document will show:
- Event ID
- Type (traffic, civic, etc.)
- Description
- Location
- Coordinates
- Timestamp
- Tags
- Raw data

---

## 🔄 Running Continuous Ingestion

```bash
# Run every 5 minutes with Firebase
python main.py --mode scheduled --interval 5 --firebase

# Run every 1 minute (more frequent)
python main.py --mode scheduled --interval 1 --firebase
```

Press `Ctrl+C` to stop.

---

## 📊 Query Events from Python

You can query events directly from your code:

```python
from pipelines.firebase_producer import FirebaseProducer

# Connect to Firebase
producer = FirebaseProducer()

# Get recent events
recent_events = producer.query_events(limit=10)

for event in recent_events:
    print(f"{event['type']}: {event['description']}")
```

---

## 🐛 Troubleshooting

### "Firebase SDK not installed"

```bash
pip install firebase-admin
```

### "Failed to initialize Firebase"

**Check:**
1. Is `firebase-credentials.json` in the correct location?
2. Is the path correct in `.env`?
3. Is the file valid JSON?

**Test:**
```bash
# Verify JSON file is valid
python -c "import json; print(json.load(open('firebase-credentials.json'))['project_id'])"
```

### "Permission denied" errors

**Fix Firestore rules:**
1. Go to Firebase Console → Firestore Database → Rules
2. Make sure rules allow read/write to events collection
3. For development, you can use:
   ```javascript
   match /events/{eventId} {
     allow read, write: if true;
   }
   ```

### "Project ID not found"

**Solution:**
1. Open `firebase-credentials.json`
2. Copy the `project_id` value
3. Update `FIREBASE_PROJECT_ID` in `.env`

---

## 📈 Monitoring Events

### Firebase Console Dashboard

1. Go to Firestore Database
2. Click on "events" collection
3. View real-time updates as events arrive

### Query by Filters

In Firebase Console, you can filter events:
- By type: `type == "traffic"`
- By severity: `severity == "high"`
- By date range: `timestamp >= <date>`

---

## 🔐 Security Best Practices

### 1. Keep Credentials Secret

```bash
# Add to .gitignore
echo "firebase-credentials.json" >> .gitignore
echo "*.json" >> .gitignore
```

### 2. Use Environment Variables

Never hardcode credentials in code!

### 3. Restrict Firestore Rules (Production)

For production, update rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /events/{eventId} {
      // Only allow authenticated writes
      allow read: if true;
      allow write: if request.auth != null;
    }
  }
}
```

### 4. Set Budget Alerts

1. Go to Firebase Console
2. Click gear icon → Usage and billing
3. Set up budget alerts

---

## 💰 Cost Considerations

**Firestore Free Tier (Daily):**
- ✅ 50,000 reads
- ✅ 20,000 writes
- ✅ 1 GB storage

**Your Usage:**
- 25 events per cycle
- 288 cycles per day (every 5 minutes)
- **= 7,200 writes per day** ✅ Well within free tier!

**Estimated Monthly Cost:** $0 (free tier is plenty)

---

## 🆚 Kafka vs Firebase

| Feature | Kafka | Firebase |
|---------|-------|----------|
| **Setup** | Complex | Simple |
| **Local Services** | Required | Not needed |
| **Scalability** | Very high | High |
| **Real-time** | Excellent | Good |
| **Cost** | Free (self-hosted) | Free tier available |
| **Management** | You manage | Google manages |
| **Best For** | Production systems | Quick prototypes |

---

## 🚀 Quick Start Commands

```bash
# 1. Install Firebase
pip install firebase-admin

# 2. Set up credentials
# (Download from Firebase Console)
mv ~/Downloads/citypulse-ai-*.json firebase-credentials.json

# 3. Update .env
echo "FIREBASE_PROJECT_ID=your-project-id" >> .env
echo "FIREBASE_PRIVATE_KEY_PATH=firebase-credentials.json" >> .env

# 4. Test connection
python -m pipelines.firebase_producer

# 5. Run ingestion
python main.py --mode once --firebase
```

---

## ✅ Success Checklist

- [ ] Firebase project created
- [ ] Firestore database enabled
- [ ] Service account key downloaded
- [ ] `firebase-credentials.json` in project directory
- [ ] Environment variables configured in `.env`
- [ ] Firebase SDK installed
- [ ] Test connection successful
- [ ] Events appearing in Firestore console

---

## 🎯 Next Steps

Once Firebase is working:
1. Run continuous ingestion: `python main.py --mode scheduled --interval 5 --firebase`
2. Monitor events in Firebase Console
3. Share Firestore collection with Person 2 (stream processing)
4. Set up indexes for efficient queries (if needed)

---

## 💡 Pro Tips

1. **Use Firebase Emulator** for local development:
   ```bash
   npm install -g firebase-tools
   firebase emulators:start
   ```

2. **Create indexes** for complex queries in Firestore

3. **Set up Cloud Functions** to trigger on new events

4. **Use Firebase Admin SDK** for server-side operations

5. **Monitor quota usage** in Firebase Console

---

## 🤝 Working with Person 2

Share with your teammate:
- **Firestore Project ID**: `citypulse-ai`
- **Collection name**: `events`
- **Service account key**: Share securely (encrypted)
- **Event schema**: See `utils/event_schema.py`

They can read events using:
```python
from firebase_admin import firestore

db = firestore.client()
events = db.collection('events').stream()
```

---

You're now ready to stream events to Firebase! 🔥
