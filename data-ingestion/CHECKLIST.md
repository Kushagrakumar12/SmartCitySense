# ✅ Getting Started Checklist

Print this out and check off each item as you complete it!

---

## 📋 Week 1 Checklist

### Day 1-2: Setup
- [ ] Navigate to project: `cd /Users/kushagrakumar/Desktop/SmartCitySense/data-ingestion`
- [ ] Run setup script: `./setup.sh`
- [ ] Create `.env` file: `cp .env.example .env`
- [ ] Get Google Maps API key from [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Get Twitter API key from [Twitter Developer Portal](https://developer.twitter.com/)
- [ ] Get Reddit API credentials from [Reddit Apps](https://www.reddit.com/prefs/apps)
- [ ] Add all API keys to `.env` file
- [ ] Test configuration: `python config/config.py`
- [ ] Read `README.md` and `QUICKSTART.md`

### Day 3: Traffic Connector
- [ ] Test traffic connector: `python -m connectors.traffic_api`
- [ ] Verify it shows traffic events (real or mock)
- [ ] Check event format has all required fields
- [ ] Review code in `connectors/traffic_api.py` to understand how it works
- [ ] Note: If no API key, mock data is used automatically ✓

### Day 4: Civic Portal Connector
- [ ] Test civic connector: `python -m connectors.civic_portal`
- [ ] Verify it shows civic complaints
- [ ] Check event categorization (power, water, road, etc.)
- [ ] Review code in `connectors/civic_portal.py`

### Day 5: Social Media Connector
- [ ] Test social media: `python -m connectors.twitter_api`
- [ ] Verify it shows tweets and Reddit posts
- [ ] Check content is relevant to Bangalore
- [ ] Review code in `connectors/twitter_api.py`

### Day 6: Streaming Setup
- [ ] **Choose ONE:** Kafka OR Firebase

#### If using Kafka:
- [ ] Install Kafka: `brew install kafka`
- [ ] Start Zookeeper: `zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties`
- [ ] Start Kafka (new terminal): `kafka-server-start /usr/local/etc/kafka/server.properties`
- [ ] Test producer: `python -m pipelines.kafka_producer`

#### If using Firebase:
- [ ] Create project at [Firebase Console](https://console.firebase.google.com/)
- [ ] Download service account JSON
- [ ] Add path to `.env`: `FIREBASE_PRIVATE_KEY_PATH=path/to/key.json`
- [ ] Add project ID to `.env`: `FIREBASE_PROJECT_ID=your_id`
- [ ] Test producer: `python -m pipelines.firebase_producer`

### Day 7: Full Pipeline Integration
- [ ] Run full pipeline once: `python main.py --mode once`
- [ ] Verify output shows:
  - [ ] Traffic events collected
  - [ ] Civic events collected
  - [ ] Social media events collected
  - [ ] Events sent to Kafka/Firebase
  - [ ] Success rate shown
- [ ] Check events are in Kafka/Firebase
- [ ] Review statistics printed at end

---

## 📋 Week 2 Checklist

### Day 8-9: Monitoring & Logging
- [ ] Run scheduled mode: `python main.py --mode scheduled --interval 5`
- [ ] Let it run for 30 minutes
- [ ] Monitor console output for errors
- [ ] Check log file: `tail -f logs/ingestion_*.log`
- [ ] Verify success rate > 95%
- [ ] Press Ctrl+C to stop, review statistics

### Day 10-11: Stress Testing
- [ ] Run scheduled mode for 1 hour: `python main.py --mode scheduled --interval 1`
- [ ] Monitor system resources (Activity Monitor on Mac)
- [ ] Check for:
  - [ ] No crashes
  - [ ] Memory stable
  - [ ] No excessive CPU usage
  - [ ] API rate limits not exceeded
- [ ] Review error logs if any failures

### Day 12-13: Integration with Person 2
- [ ] Share event schema (from `utils/event_schema.py`)
- [ ] Share Kafka topic name or Firebase collection name
- [ ] Send sample events to Person 2 for testing
- [ ] Coordinate on:
  - [ ] Event format confirmed
  - [ ] Queue/collection name confirmed
  - [ ] Test data provided
- [ ] Run integration test:
  - [ ] Your code runs
  - [ ] Events sent to queue
  - [ ] Person 2 can read events
  - [ ] Person 2 confirms data is clean

### Day 14: Documentation & Demo
- [ ] Review all documentation files
- [ ] Update any outdated information
- [ ] Create demo script or slides
- [ ] Prepare to show:
  - [ ] Running system
  - [ ] Statistics dashboard
  - [ ] Sample events
  - [ ] Integration with Person 2
- [ ] Test demo run-through
- [ ] Celebrate completion! 🎉

---

## 🆘 Emergency Checklist

If something isn't working, go through this:

### System won't start
- [ ] Virtual environment activated? `source venv/bin/activate`
- [ ] Dependencies installed? `pip install -r requirements.txt`
- [ ] `.env` file exists? `ls -la .env`
- [ ] Python 3.8+? `python --version`

### Connectors not working
- [ ] Check API keys in `.env` file
- [ ] Check if mock data is showing (that's OK for testing!)
- [ ] Review logs: `cat logs/ingestion_*.log`
- [ ] Test configuration: `python config/config.py`

### Kafka/Firebase issues
- [ ] Kafka: Is it running? Check with `ps aux | grep kafka`
- [ ] Firebase: Credentials file exists? Check path in `.env`
- [ ] Try the other option: Use `--firebase` or switch to Kafka

### Events not being collected
- [ ] Run test script: `python test_all.py`
- [ ] Check individual connector: `python -m connectors.traffic_api`
- [ ] Review connector code for errors
- [ ] Check API rate limits

---

## 📊 Daily Progress Tracker

| Day | Task | Status | Notes |
|-----|------|--------|-------|
| 1   | Setup environment | ⬜ |  |
| 2   | Get API keys | ⬜ |  |
| 3   | Traffic connector | ⬜ |  |
| 4   | Civic connector | ⬜ |  |
| 5   | Social connector | ⬜ |  |
| 6   | Streaming setup | ⬜ |  |
| 7   | Full integration | ⬜ |  |
| 8   | Monitoring | ⬜ |  |
| 9   | Error handling | ⬜ |  |
| 10  | Stress testing | ⬜ |  |
| 11  | Optimization | ⬜ |  |
| 12  | Person 2 sync | ⬜ |  |
| 13  | Integration test | ⬜ |  |
| 14  | Demo & docs | ⬜ |  |

Legend: ⬜ Not started | 🟨 In progress | ✅ Complete

---

## 🎯 Final Success Criteria

Before marking complete, verify:

- [ ] All 3 connectors working (traffic, civic, social)
- [ ] Events in standardized format
- [ ] Streaming to Kafka or Firebase
- [ ] Error rate < 5%
- [ ] Monitoring dashboard shows statistics
- [ ] Integration with Person 2 successful
- [ ] Can run scheduled mode without crashes
- [ ] All documentation complete
- [ ] Demo prepared

---

## 📞 Quick Reference

**Start everything:**
```bash
cd data-ingestion
source venv/bin/activate
python main.py --mode scheduled --interval 5
```

**Test everything:**
```bash
python test_all.py
```

**Check logs:**
```bash
tail -f logs/ingestion_*.log
```

**Stop everything:**
Press `Ctrl + C`

---

**YOU'VE GOT THIS! START WITH DAY 1!** 🚀
