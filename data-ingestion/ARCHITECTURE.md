# 📊 Person 1 - Data Ingestion Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                        │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Traffic  │        │  Civic   │        │  Social  │
    │   APIs   │        │ Portals  │        │  Media   │
    └──────────┘        └──────────┘        └──────────┘
    │ Google   │        │   BBMP   │        │ Twitter  │
    │   Maps   │        │   Govt   │        │  Reddit  │
    └──────────┘        └──────────┘        └──────────┘
           │                    │                    │
           └────────────────────┴────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   API CONNECTORS      │
                    │  (Your Implementation)│
                    └───────────────────────┘
                    │ - Rate limiting       │
                    │ - Error handling      │
                    │ - Retry logic         │
                    │ - Data normalization  │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   EVENT SCHEMA        │
                    │   (Standardized)      │
                    └───────────────────────┘
                    │ {                     │
                    │   id, type, source,   │
                    │   description,        │
                    │   location, coords,   │
                    │   severity, tags      │
                    │ }                     │
                    └───────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
            ┌──────────────┐       ┌──────────────┐
            │    KAFKA     │  OR   │   FIREBASE   │
            │   Producer   │       │   Firestore  │
            └──────────────┘       └──────────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   STREAMING QUEUE     │
                    │   (For Person 2)      │
                    └───────────────────────┘
```

## Component Details

### 1. API Connectors (`connectors/`)

#### TrafficAPIConnector (`traffic_api.py`)
- **Source**: Google Maps Directions API
- **Data**: Real-time traffic conditions, delays, route information
- **Monitored Areas**: 10 key locations in Bangalore
- **Update Frequency**: Every 5 minutes
- **Mock Data**: Available for testing without API key

**Key Features:**
- Monitors major routes (Airport to MG Road, Whitefield to Koramangala, etc.)
- Calculates delay minutes
- Auto-classifies severity (low/medium/high/critical)
- Handles rate limits gracefully

#### CivicPortalConnector (`civic_portal.py`)
- **Source**: BBMP, Government civic portals
- **Data**: Power outages, water issues, potholes, garbage complaints
- **Categories**: Civic, Emergency
- **Mock Data**: Available

**Key Features:**
- Categorizes complaints automatically
- Maps priority to severity
- Extracts location and coordinates
- Filters for Bangalore-specific issues

#### SocialMediaConnector (`twitter_api.py`)
- **Sources**: Twitter/X, Reddit
- **Subreddits**: r/bangalore
- **Keywords**: Traffic, power, water, accident, civic issues
- **Mock Data**: Available

**Key Features:**
- Filters relevant city events
- Classifies tweet/post content
- Tracks engagement metrics (likes, retweets)
- Respects API rate limits

### 2. Streaming Pipeline (`pipelines/`)

#### KafkaEventProducer (`kafka_producer.py`)
- Connects to Kafka broker
- Serializes events to JSON
- Guarantees message delivery (acks='all')
- Maintains message ordering
- Batch processing support

#### FirebaseProducer (`firebase_producer.py`)
- Alternative to Kafka for Firebase-based projects
- Stores events in Firestore
- Batch write support
- Easier setup for beginners

### 3. Configuration (`config/`)

**Environment Variables (.env):**
```
GOOGLE_MAPS_API_KEY=...
TWITTER_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...
KAFKA_BROKER=localhost:9092
FIREBASE_PROJECT_ID=...
```

**Configurable Parameters:**
- Polling interval (default: 5 minutes)
- City center coordinates
- Search keywords
- Rate limit thresholds

### 4. Utilities (`utils/`)

#### Event Schema
```python
Event {
    id: str              # Unique UUID
    type: EventType      # traffic|civic|emergency|weather
    source: EventSource  # google_maps|twitter|reddit|civic_portal
    description: str     # Human-readable description
    location: str        # Address/landmark
    coordinates: {       # Lat/lon
        lat: float,
        lon: float
    }
    timestamp: datetime  # ISO format
    severity: str        # low|medium|high|critical
    tags: list[str]      # Additional tags
    raw_data: dict       # Original API response
}
```

#### Logger
- Colored console output
- File logging to `logs/ingestion_YYYYMMDD.log`
- Configurable log levels

### 5. Orchestration (`main.py`)

**Main Script Features:**
- Runs all connectors in sequence
- Collects and deduplicates events
- Pushes to streaming queue
- Monitors success rates
- Provides statistics dashboard

**Modes:**
1. **Once**: Single run (testing)
2. **Scheduled**: Continuous with configurable interval

## Data Flow

1. **Collection**: Connectors poll APIs every N minutes
2. **Normalization**: Raw data → standardized Event objects
3. **Validation**: Schema validation via Pydantic
4. **Streaming**: Push to Kafka/Firebase queue
5. **Monitoring**: Track statistics and health

## Error Handling

- **Retry Logic**: Exponential backoff for failed API calls
- **Fallback**: Mock data when APIs unavailable
- **Logging**: All errors logged with context
- **Graceful Degradation**: System continues if one source fails

## Performance

- **Target**: 100-500 events/hour
- **Latency**: < 10 seconds from API fetch to queue
- **Success Rate**: > 95%
- **API Efficiency**: Batched requests where possible

## Testing

**Unit Tests** (`tests/test_connectors.py`):
- Event schema validation
- Connector initialization
- Mock data generation
- Classification logic

**Integration Tests**:
- End-to-end pipeline
- Kafka/Firebase connectivity
- API error handling

## Monitoring Metrics

- Events collected (by source, by type)
- API call rates
- Error rates
- Cycle durations
- Success rates

## Handoff to Person 2

**You Provide:**
- Kafka topic: `smartcitysense_events`
- OR Firebase collection: `events`
- Event schema (see above)
- Sample events for testing

**Person 2 Consumes:**
- Raw events from queue
- Applies deduplication
- Geo-normalization
- Stores in cleaned database

## Key Files

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `main.py` | Main orchestrator | ~200 |
| `connectors/traffic_api.py` | Traffic data | ~250 |
| `connectors/civic_portal.py` | Civic data | ~200 |
| `connectors/twitter_api.py` | Social media | ~300 |
| `pipelines/kafka_producer.py` | Kafka streaming | ~150 |
| `utils/event_schema.py` | Data schema | ~80 |
| `config/config.py` | Configuration | ~120 |

**Total: ~1,300 lines of production code**

## Success Criteria ✅

- [ ] All connectors fetch data successfully
- [ ] Events pushed to streaming queue reliably
- [ ] Error rate < 5%
- [ ] Monitoring dashboard shows real-time stats
- [ ] Integration with Person 2 successful
- [ ] Documentation complete
- [ ] Tests passing

---

**You now have a complete, production-ready data ingestion system!** 🚀
