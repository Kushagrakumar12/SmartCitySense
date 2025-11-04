# Data Ingestion Module - Person 1

## Overview
This module handles real-time data collection from multiple sources including traffic APIs, civic portals, and social media platforms. Events are normalized and pushed to Kafka/Firebase Pub/Sub for processing by Person 2.

## Architecture
```
External APIs → Connectors → Event Normalization → Kafka/Pub/Sub Queue
```

## Directory Structure
```
data-ingestion/
├── connectors/          # API-specific connectors
│   ├── traffic_api.py   # Google Maps, transport APIs
│   ├── civic_portal.py  # Government portals
│   └── twitter_api.py   # Social media (Twitter, Reddit, Instagram)
├── pipelines/           # Streaming infrastructure
│   ├── kafka_producer.py
│   └── firebase_producer.py
├── config/              # Configuration files
│   ├── config.py
│   └── api_keys.py
├── utils/               # Shared utilities
│   ├── logger.py
│   └── event_schema.py
├── tests/               # Unit tests
├── main.py              # Main orchestration script
└── requirements.txt     # Python dependencies
```

## Event Schema
All connectors output standardized events:
```json
{
  "id": "unique_event_id",
  "type": "traffic|civic|cultural|emergency|weather",
  "source": "google_maps|twitter|civic_portal|reddit|instagram",
  "description": "Event description text",
  "location": "Address or landmark",
  "coordinates": {"lat": 12.9716, "lon": 77.5946},
  "timestamp": "2025-10-04T10:30:00Z",
  "severity": "low|medium|high|critical",
  "raw_data": {}
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd data-ingestion
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy `.env.example` to `.env` and add your API keys:
```
GOOGLE_MAPS_API_KEY=your_key
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
CIVIC_PORTAL_API_KEY=your_key
KAFKA_BROKER=localhost:9092
FIREBASE_PROJECT_ID=your_project
```

### 3. Run Individual Connectors (Testing)
```bash
python -m connectors.traffic_api
python -m connectors.civic_portal
python -m connectors.twitter_api
```

### 4. Run Full Pipeline
```bash
python main.py
```

## API Sources

### Traffic Data
- **Google Maps Traffic API** - Real-time traffic conditions
- **BMTC API** - Public transport updates
- **Road closure data** - Government feeds

### Civic Data
- **Bangalore Municipal Corporation (BBMP)** - Complaints and civic issues
- **Government portals** - Infrastructure updates
- **Public notice boards** - Event announcements

### Social Media
- **Twitter/X API** - Real-time city mentions, hashtags
- **Reddit API** - r/bangalore, city-related subreddits
- **Instagram API** - Location-tagged posts (if available)

## Monitoring
- Event counts logged every minute
- API failure alerts
- Rate limit tracking
- Queue health checks

## Daily Workflow
1. **Day 1-2**: Set up environment, get API keys
2. **Day 3-5**: Build and test individual connectors
3. **Day 6-7**: Integrate with streaming queue
4. **Day 8-10**: Add error handling, monitoring
5. **Day 11-14**: Optimize, test, document

## Contact
Person 1 - Data Ingestion Lead
