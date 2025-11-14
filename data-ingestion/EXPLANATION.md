# 📋 Person 1 - Complete Task List & Explanation

## 🎯 Your Role in Detail

You are **Person 1 - Data Ingestion Engineer**. Your mission is to build the "front door" of SmartCitySense - the system that collects raw data from the outside world and feeds it into the pipeline.

### What You're Building

Think of yourself as a **data collector**. You're building robots (API connectors) that:
1. Go out to different sources (Google Maps, Twitter, government portals)
2. Collect information about what's happening in Bangalore
3. Standardize it into a clean format
4. Push it to a queue where Person 2 will process it

---

## 🔍 Detailed Explanation of Each Component

### 1️⃣ API Connectors (The Data Collectors)

#### Traffic API Connector (`traffic_api.py`)
**What it does:**
- Connects to Google Maps API
- Checks traffic conditions on major Bangalore routes
- Example: "How long does it take to get from Airport to MG Road right now?"
- Compares normal time vs. current time → calculates delay
- If delay > 10 minutes → creates a traffic event

**How it works:**
```python
# Pseudo-code explanation
1. Define routes to monitor (Airport→MG Road, Whitefield→Koramangala, etc.)
2. Every 5 minutes:
   a. Ask Google Maps: "What's the traffic like?"
   b. Get response: "Normal: 30 min, Today: 50 min"
   c. Calculate: 20 min delay = HIGH severity
   d. Create event: "Heavy traffic, 20 min delay"
   e. Send to queue
```

**Real-world example:**
- Normal route time: 30 minutes
- Current time with traffic: 50 minutes
- System generates: "Heavy traffic on Airport Road, 20 min delay, avoid until 6PM"

#### Civic Portal Connector (`civic_portal.py`)
**What it does:**
- Connects to government complaint systems
- Fetches civic issues (power cuts, water problems, potholes)
- Example complaints:
  - "Power outage in Koramangala"
  - "Water shortage in Whitefield"
  - "Potholes on MG Road"

**How it works:**
```python
1. Connect to civic portal API
2. Every 5 minutes:
   a. Fetch new complaints
   b. Filter for Bangalore
   c. Categorize (power/water/road/garbage)
   d. Determine severity (based on priority)
   e. Create standardized event
   f. Send to queue
```

#### Social Media Connector (`twitter_api.py`)
**What it does:**
- Monitors Twitter and Reddit
- Looks for posts about Bangalore
- Filters for relevant keywords: traffic, power, accident, jam, etc.
- Example tweets:
  - "Massive traffic on Silk Board, avoid!"
  - "Power cut in Indiranagar since 2 hours"

**How it works:**
```python
# Twitter
1. Search for: "bangalore OR bengaluru"
2. Filter for keywords: traffic, power, accident, jam
3. Exclude retweets (we want original reports)
4. For each relevant tweet:
   a. Extract text
   b. Classify type (traffic/civic/emergency)
   c. Determine location (from text or geo-tag)
   d. Create event
   e. Send to queue

# Reddit
1. Monitor r/bangalore subreddit
2. Check hot posts
3. Filter for city events
4. Same processing as Twitter
```

---

### 2️⃣ Event Schema (The Standard Format)

**Problem:** Each API gives data in different formats
- Google Maps: JSON with routes, durations, distances
- Twitter: Tweets with text, timestamps, user info
- Civic portal: Complaints with ID, category, status

**Solution:** Convert everything to ONE standard format

**Standard Event Format:**
```json
{
  "id": "unique-id-12345",
  "type": "traffic",              // What kind of event?
  "source": "google_maps",        // Where did it come from?
  "description": "Heavy traffic on MG Road, 20 min delay",
  "location": "MG Road, Bangalore",
  "coordinates": {
    "lat": 12.9760,
    "lon": 77.6061
  },
  "timestamp": "2025-10-04T10:30:00Z",
  "severity": "high",             // How serious is it?
  "tags": ["traffic", "delay", "mgroad"],
  "raw_data": {...}               // Original API response
}
```

**Why this matters:**
- Person 2 knows exactly what to expect
- Easy to store in database
- Can be processed by AI/ML models
- Consistent across all sources

---

### 3️⃣ Streaming Pipeline (The Delivery System)

You have TWO options:

#### Option A: Kafka (Industry Standard)
**What it is:** A message queue - like a conveyor belt for data

**How it works:**
```
Your Code → Kafka Topic → Person 2's Code
           (Message Queue)
```

**Analogy:** 
- You're a restaurant taking orders (API data)
- Kafka is the order window where you place tickets
- Person 2 is the kitchen reading tickets and cooking (processing)

**Commands:**
```bash
# Start Kafka
kafka-server-start /usr/local/etc/kafka/server.properties

# Your code pushes to topic "citypulse_events"
# Person 2 reads from same topic
```

#### Option B: Firebase (Easier Alternative)
**What it is:** Google's cloud database

**How it works:**
```
Your Code → Firebase Firestore Collection → Person 2's Code
           (Cloud Database)
```

**Advantage:** No Kafka setup needed, easier for beginners

---

### 4️⃣ Main Orchestrator (The Brain)

**File:** `main.py`

**What it does:**
1. Runs all connectors in order
2. Collects all events
3. Sends to Kafka/Firebase
4. Logs statistics
5. Repeats every N minutes

**Flow:**
```
┌─────────────────────────────────────┐
│  START                              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Fetch Traffic Events               │
│  (Google Maps)                      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Fetch Civic Events                 │
│  (Government Portal)                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Fetch Social Media Events          │
│  (Twitter + Reddit)                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Combine All Events                 │
│  (100-500 events collected)         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Push to Kafka/Firebase             │
│  (Send to queue)                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Log Statistics                     │
│  (Success rate, counts, etc.)       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Wait 5 minutes                     │
└────────────┬────────────────────────┘
             │
             └──────► REPEAT
```

---

## 📅 Day-by-Day Task Breakdown

### Day 1-2: Setup & Environment
**Tasks:**
1. ✅ Run `./setup.sh` → Creates Python environment
2. ✅ Get API keys:
   - Google Maps API (traffic)
   - Twitter Bearer Token (social media)
   - Reddit API (social media)
3. ✅ Add keys to `.env` file
4. ✅ Test: `python config/config.py` → Should show configuration status

**Deliverable:** Working development environment

---

### Day 3: Traffic Connector
**Tasks:**
1. ✅ Code already written in `connectors/traffic_api.py`
2. Test it: `python -m connectors.traffic_api`
3. Should see: List of traffic events (real or mock)
4. Verify: Events have correct format (id, type, description, etc.)

**Your job:** Understand how it works, test it, maybe add more routes

**Deliverable:** Working traffic connector

---

### Day 4: Civic Portal Connector
**Tasks:**
1. ✅ Code already written in `connectors/civic_portal.py`
2. Test it: `python -m connectors.civic_portal`
3. Should see: List of civic complaints
4. Verify: Events are categorized correctly (power, water, road, etc.)

**Your job:** Test and understand civic data collection

**Deliverable:** Working civic connector

---

### Day 5: Social Media Connector
**Tasks:**
1. ✅ Code already written in `connectors/twitter_api.py`
2. Test it: `python -m connectors.twitter_api`
3. Should see: Tweets and Reddit posts about Bangalore
4. Verify: Content is relevant to city events

**Your job:** Test social media monitoring

**Deliverable:** Working social media connector

---

### Day 6: Streaming Setup
**Tasks:**
1. Choose: Kafka OR Firebase
2. If Kafka:
   ```bash
   brew install kafka
   zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties
   kafka-server-start /usr/local/etc/kafka/server.properties
   ```
3. If Firebase:
   - Create project at console.firebase.google.com
   - Download credentials JSON
   - Add to `.env`
4. Test: `python -m pipelines.kafka_producer` OR `python -m pipelines.firebase_producer`

**Deliverable:** Working streaming queue

---

### Day 7: Integration
**Tasks:**
1. Run full pipeline: `python main.py --mode once`
2. Should see:
   ```
   Fetching traffic events... ✓ Collected 5 events
   Fetching civic events... ✓ Collected 8 events
   Fetching social media events... ✓ Collected 12 events
   
   Sent 25/25 events to Kafka
   Success rate: 100%
   ```
3. Verify events are in Kafka/Firebase

**Deliverable:** End-to-end working pipeline

---

### Day 8-10: Error Handling & Monitoring
**Tasks:**
1. ✅ Error handling already implemented (retry logic, fallbacks)
2. Test error scenarios:
   - Disconnect internet → Should use mock data
   - Wrong API key → Should log error, continue
   - Rate limit hit → Should retry with backoff
3. Monitor logs: `tail -f logs/ingestion_*.log`

**Deliverable:** Robust, production-ready system

---

### Day 11: Stress Testing
**Tasks:**
1. Run scheduled mode: `python main.py --mode scheduled --interval 1`
2. Let it run for 1 hour
3. Check:
   - No crashes?
   - Memory stable?
   - Success rate > 95%?
   - API rate limits not exceeded?

**Deliverable:** Verified system stability

---

### Day 12-13: Integration with Person 2
**Tasks:**
1. Share event schema with Person 2
2. Send sample events for testing
3. Coordinate on:
   - Kafka topic name / Firebase collection
   - Event format confirmation
   - Testing integration
4. Run integration test: Your code → Queue → Person 2's code

**Deliverable:** Successful handoff to Person 2

---

### Day 14: Documentation & Demo
**Tasks:**
1. ✅ Documentation already written (README, QUICKSTART, ARCHITECTURE)
2. Review and update if needed
3. Prepare demo:
   - Show running system
   - Display statistics
   - Show sample events
4. Create presentation slides (optional)

**Deliverable:** Complete, documented system ready for production

---

## 🎓 Learning Outcomes

By the end, you'll understand:
- ✅ How to integrate multiple APIs
- ✅ Data normalization and standardization
- ✅ Streaming architectures (Kafka/Firebase)
- ✅ Error handling and retry logic
- ✅ Rate limiting and API best practices
- ✅ Monitoring and logging
- ✅ Production-ready code structure

---

## 🚨 Common Issues & Solutions

### "Import could not be resolved"
**Cause:** VS Code can't find packages
**Solution:** 
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "API key invalid"
**Cause:** Wrong key or not configured
**Solution:** Check `.env` file, re-copy API key

### "Kafka connection refused"
**Cause:** Kafka not running
**Solution:** Start Kafka or use Firebase mode

### "Rate limit exceeded"
**Cause:** Too many API calls
**Solution:** Increase polling interval to 5-10 minutes

---

## ✅ Success Checklist

By Day 14, you should have:
- [ ] All connectors fetching data
- [ ] Events in standardized format
- [ ] Streaming to Kafka/Firebase
- [ ] Monitoring dashboard working
- [ ] Error rate < 5%
- [ ] Integration with Person 2 successful
- [ ] Complete documentation
- [ ] Demo ready

---

## 🎯 What You've Accomplished

You've built:
- ✅ 3 API connectors (Traffic, Civic, Social Media)
- ✅ Event standardization system
- ✅ Streaming pipeline (Kafka/Firebase)
- ✅ Orchestration and scheduling
- ✅ Monitoring and logging
- ✅ Error handling and resilience
- ✅ ~1,300 lines of production code
- ✅ Complete test suite
- ✅ Comprehensive documentation

**This is real-world, production-grade software engineering!** 🚀

---

**You're ready to start! Begin with:** `cd data-ingestion && ./setup.sh` 🎉
