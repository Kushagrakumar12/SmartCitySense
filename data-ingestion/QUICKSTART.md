# 🚀 Quick Start Guide - Data Ingestion (Person 1)

## Your Mission
You're building the **data collection layer** of SmartCitySense. Your job is to pull real-time data from multiple sources (traffic APIs, civic portals, social media) and push it to a streaming queue where Person 2 will process it.

---

## 📦 Setup (5 minutes)

### 1. Install Dependencies
```bash
cd data-ingestion

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all required packages
- Create a `.env` file for your API keys

### 2. Get API Keys

You'll need API keys for the data sources. **Don't worry if you don't have all of them** - the system works with mock data!

#### Google Maps API (Traffic Data)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Maps JavaScript API" and "Directions API"
4. Create credentials (API Key)
5. Add to `.env`: `GOOGLE_MAPS_API_KEY=your_key`

#### Twitter API (Social Media)
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app
3. Get Bearer Token
4. Add to `.env`: `TWITTER_BEARER_TOKEN=your_token`

#### Reddit API (Social Media)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create an app (script type)
3. Note client ID and secret
4. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   ```

### 3. Choose Streaming Backend

**Option A: Kafka (Recommended for production)**
```bash
# Install Kafka locally (macOS)
brew install kafka

# Start Zookeeper
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

# Start Kafka (in another terminal)
kafka-server-start /usr/local/etc/kafka/server.properties
```

**Option B: Firebase (Easier for beginners)**
1. Create Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Download service account key JSON
3. Add to `.env`:
   ```
   FIREBASE_PROJECT_ID=your_project_id
   FIREBASE_PRIVATE_KEY_PATH=path/to/key.json
   ```

---

## 🧪 Testing Individual Components

### Test 1: Configuration
```bash
python config/config.py
```
Should show your configuration status.

### Test 2: Traffic Connector
```bash
python -m connectors.traffic_api
```
Fetches traffic data (or shows mock data).

### Test 3: Civic Connector
```bash
python -m connectors.civic_portal
```
Fetches civic complaints (or shows mock data).

### Test 4: Social Media Connectors
```bash
python -m connectors.twitter_api
```
Fetches tweets and Reddit posts (or shows mock data).

### Test 5: Streaming Pipeline
```bash
# For Kafka
python -m pipelines.kafka_producer

# For Firebase
python -m pipelines.firebase_producer
```

---

## 🏃 Running the Full Pipeline

### One-Time Run (Testing)
```bash
python main.py --mode once
```

This will:
1. Fetch from all connectors
2. Push to Kafka/Firebase
3. Show statistics

### Scheduled Mode (Production)
```bash
# Run every 5 minutes
python main.py --mode scheduled --interval 5

# Run every 1 minute (more frequent)
python main.py --mode scheduled --interval 1

# Use Firebase instead of Kafka
python main.py --mode scheduled --interval 5 --firebase
```

Press `Ctrl+C` to stop.

---

## 📊 Monitoring

The system logs to:
- **Console**: Real-time colored output
- **Files**: `logs/ingestion_YYYYMMDD.log`

Statistics shown:
- Events collected per source
- Events sent to queue
- Success rates
- API health

---

## 🐛 Troubleshooting

### "Import could not be resolved"
This is just a VS Code warning. The code will work fine when you run it.

To fix: Install dependencies in VS Code's Python environment
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "API key not configured"
No problem! The system automatically uses mock data for testing.

### "Kafka connection failed"
Either:
1. Start Kafka (see setup instructions)
2. Use Firebase: `python main.py --firebase`

### "Rate limit exceeded"
Social media APIs have rate limits. The system handles this with exponential backoff and retries.

---

## 📁 Project Structure

```
data-ingestion/
├── connectors/           # API connectors
│   ├── traffic_api.py   # Traffic data (Google Maps)
│   ├── civic_portal.py  # Civic complaints
│   └── twitter_api.py   # Social media (Twitter, Reddit)
├── pipelines/           # Streaming infrastructure
│   ├── kafka_producer.py
│   └── firebase_producer.py
├── config/              # Configuration
│   └── config.py
├── utils/               # Shared utilities
│   ├── logger.py
│   └── event_schema.py
├── main.py              # Main orchestrator
└── monitoring.py        # Statistics & health checks
```

---

## ✅ Your Daily Checklist

### Week 1 (Days 1-7)
- [ ] Day 1: Set up environment, get API keys
- [ ] Day 2: Test traffic connector
- [ ] Day 3: Test civic portal connector
- [ ] Day 4: Test social media connectors
- [ ] Day 5: Set up Kafka/Firebase
- [ ] Day 6: Add error handling
- [ ] Day 7: Test scheduling

### Week 2 (Days 8-14)
- [ ] Day 8: End-to-end testing
- [ ] Day 9: Add logging & monitoring
- [ ] Day 10: Optimize API calls
- [ ] Day 11: Stress test
- [ ] Day 12: Write documentation
- [ ] Day 13: Integration test with Person 2
- [ ] Day 14: Final polish & demo

---

## 🤝 Working with Person 2

**You provide:** Clean events in standardized format pushed to Kafka/Firebase

**Person 2 needs:**
- Event schema (see `utils/event_schema.py`)
- Kafka topic name or Firebase collection name
- Sample events for testing

**Sync points:**
- Day 5: Confirm event schema
- Day 8: Integration test
- Day 13: Final integration

---

## 📈 Success Metrics

By Day 14, you should have:
- ✅ Real-time data from 3+ sources
- ✅ Events pushed to Kafka/Firebase
- ✅ < 5% error rate
- ✅ Monitoring dashboard
- ✅ Complete documentation

---

## 💡 Tips

1. **Start with mock data** - Test your pipeline logic before worrying about API keys
2. **Test frequently** - Run individual connectors after each change
3. **Monitor logs** - Check `logs/` directory for detailed information
4. **Rate limits** - Be careful with API calls (use scheduled mode with 5+ minute intervals)
5. **Version control** - Commit frequently to track your progress

---

## 🆘 Getting Help

If you're stuck:
1. Check the logs in `logs/` directory
2. Run tests: `python -m pytest tests/`
3. Review example output in connector test functions
4. Check if API keys are correct in `.env`

---

## 🎯 Next Steps

Once your pipeline is running:
1. Share event schema with Person 2
2. Provide sample events for testing
3. Coordinate on Kafka topic / Firebase collection
4. Monitor integration success rate

**You're ready to go! Start with `./setup.sh` and test each component.** 🚀
