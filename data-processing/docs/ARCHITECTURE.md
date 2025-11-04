# System Architecture
## Person 2 - Data Processing Pipeline

Comprehensive architecture documentation

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PERSON 1                                │
│                     Data Ingestion Layer                        │
│  (APIs: Google Maps, Twitter, Reddit, Civic Portals)           │
└────────────────┬───────────────┬────────────────────────────────┘
                 │               │
                 ▼               ▼
           ┌─────────┐     ┌──────────┐
           │  Kafka  │     │ Firebase │
           │  Topic  │     │  Input   │
           └─────────┘     └──────────┘
                 │               │
                 └───────┬───────┘
                         │ Raw Events
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                         PERSON 2                                │
│                  Data Processing Pipeline                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Consumer   │→ │Deduplicator │→ │Geo-Normalizer│           │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                            │                    │
│                                            ▼                    │
│                    ┌─────────────┐  ┌─────────────┐            │
│                    │Categorizer  │→ │ Validator   │           │
│                    └─────────────┘  └─────────────┘            │
│                                            │                    │
│                                            ▼                    │
│                                    ┌──────────────┐             │
│                                    │   Storage    │             │
│                                    └──────────────┘             │
└────────────────────────────────────────┬───────────────────────┘
                                         │
                                         ▼
                                  ┌──────────┐
                                  │ Firebase │
                                  │ Firestore│
                                  └──────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
                    ▼                                         ▼
            ┌──────────────┐                          ┌─────────────┐
            │   MEMBER B   │                          │  MEMBER C   │
            │   AI/ML      │                          │  Frontend   │
            │   Analysis   │                          │  Display    │
            └──────────────┘                          └─────────────┘
```

---

## 📦 Component Architecture

### 1. Consumer Layer

**Purpose**: Read events from input sources

**Components**:

#### KafkaConsumer
```python
class EventKafkaConsumer:
    - connect_to_broker()
    - subscribe_to_topic()
    - consume_batch()
    - consume_stream()
```

**Features**:
- Auto-commit offsets
- JSON deserialization
- Batch processing
- Error recovery

**Configuration**:
```python
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "smartcitysense_events"
KAFKA_GROUP_ID = "data_processing_group"
```

#### FirebaseReader
```python
class FirebaseEventReader:
    - read_new_events()
    - read_events_in_range()
    - read_by_type()
    - poll_continuously()
```

**Features**:
- Timestamp tracking
- Range queries
- Type filtering
- Polling loop

---

### 2. Processing Layer

#### Deduplicator

**Algorithm**: Multi-criteria similarity detection

```python
class EventDeduplicator:
    
    # Step 1: Calculate text similarity
    def calculate_text_similarity(text1, text2):
        - TF-IDF vectorization
        - Cosine similarity
        - Fuzzy ratio
        - Jaccard similarity
        return combined_score
    
    # Step 2: Calculate geographic distance
    def calculate_distance(coord1, coord2):
        - Haversine formula
        - Earth's curvature
        return distance_in_km
    
    # Step 3: Check if events are similar
    def are_events_similar(event1, event2):
        - Same type check
        - Time window check (60 min)
        - Text similarity OR geographic proximity
        return boolean
    
    # Step 4: Find all duplicates
    def find_duplicates(events):
        - Pairwise comparison
        - Group similar events
        return duplicate_map
    
    # Step 5: Mark duplicates
    def mark_duplicates(events):
        - Add is_duplicate field
        - Add duplicate_of reference
        - Add similar_events list
        return marked_events
```

**Parameters**:
```python
SIMILARITY_THRESHOLD = 0.85  # Text similarity cutoff
TIME_WINDOW_MINUTES = 60     # Temporal window
DISTANCE_THRESHOLD_KM = 2    # Geographic radius
```

**Performance**:
- Time complexity: O(n²) for n events
- Optimization: Time-windowing reduces comparisons
- Caching: Similarity scores cached

---

#### Geo-Normalizer

**Architecture**: Multi-provider with caching

```python
class GeoNormalizer:
    
    # Initialization
    def __init__():
        - Initialize Google Maps client
        - Initialize Nominatim client
        - Set up LRU caches
    
    # Forward geocoding
    @lru_cache(maxsize=1000)
    def geocode_address(address):
        try:
            # Primary: Google Maps
            coords = google_maps.geocode(address)
        except:
            # Fallback: Nominatim
            coords = nominatim.geocode(address)
        return coords
    
    # Reverse geocoding
    @lru_cache(maxsize=500)
    def reverse_geocode(lat, lon):
        try:
            # Primary: Google Maps
            address = google_maps.reverse_geocode(lat, lon)
        except:
            # Fallback: Nominatim
            address = nominatim.reverse_geocode(lat, lon)
        return address
    
    # Zone mapping
    def find_zone(lat, lon):
        - Calculate distance to each zone center
        - Return closest zone
        return zone_name
    
    # Neighborhood detection
    def find_neighborhood(address, zone):
        - Extract neighborhood from address
        - Match against known neighborhoods
        return neighborhood_name
    
    # Main processing
    def normalize_event_location(event):
        if has_location:
            coords = geocode_address(location)
        if has_coordinates:
            address = reverse_geocode(coords)
        zone = find_zone(coords)
        neighborhood = find_neighborhood(address, zone)
        return enhanced_event
```

**Providers**:

| Provider | Type | Cost | Accuracy | Rate Limit |
|----------|------|------|----------|------------|
| Google Maps | Primary | Paid | Excellent | 50k/day free |
| Nominatim | Fallback | Free | Good | 1 req/sec |

**Caching Strategy**:
- LRU (Least Recently Used)
- Forward geocoding: 1000 addresses
- Reverse geocoding: 500 coordinates
- Cache hit rate: ~60-70%

**Zone Configuration**:
```python
BANGALORE_ZONES = {
    "North Bangalore": {
        "center": (13.0358, 77.5970),
        "neighborhoods": ["Hebbal", "Yelahanka", "Malleshwaram"]
    },
    "South Bangalore": {
        "center": (12.9173, 77.6221),
        "neighborhoods": ["Jayanagar", "BTM Layout", "Silk Board"]
    },
    "East Bangalore": {
        "center": (12.9698, 77.7500),
        "neighborhoods": ["Whitefield", "Marathahalli", "Bellandur"]
    },
    "West Bangalore": {
        "center": (12.9894, 77.5408),
        "neighborhoods": ["Rajajinagar", "Peenya"]
    },
    "Central Bangalore": {
        "center": (12.9716, 77.5946),
        "neighborhoods": ["MG Road", "Koramangala", "Indiranagar"]
    }
}
```

---

#### Event Categorizer

**Architecture**: Rule-based classification with context analysis

```python
class EventCategorizer:
    
    # Subtype determination
    def determine_subtype(event):
        type_mapping = {
            "traffic": {
                "accident": ["accident", "crash", "collision"],
                "congestion": ["jam", "traffic", "slow"],
                "road_closure": ["closed", "blocked", "closure"],
                "construction": ["construction", "repair"]
            },
            "civic": {
                "power_outage": ["power", "electricity", "BESCOM"],
                "water_shortage": ["water", "tanker", "supply"],
                "garbage": ["garbage", "waste", "trash"],
                "pothole": ["pothole", "damage"],
                "drainage": ["drainage", "overflow", "sewage"]
            },
            "emergency": {
                "fire": ["fire", "burning", "smoke"],
                "medical": ["ambulance", "medical", "hospital"],
                "crime": ["theft", "robbery", "police"]
            }
        }
        # Keyword matching
        return subtype
    
    # Tag extraction
    def extract_tags(event):
        tags = []
        # Event type tags
        # Location tags (zone, neighborhood)
        # Context tags (government, weather)
        # Time tags (rush hour, weekend)
        return tags
    
    # Urgency classification
    def classify_urgency(event):
        # Critical indicators
        critical_keywords = ["emergency", "urgent", "fire", "accident"]
        
        # Resolved indicators
        resolved_keywords = ["resolved", "cleared", "fixed"]
        
        # Context-based rules
        if "accident" in subtype and severity == "high":
            return "critical"
        
        return urgency_level
    
    # Time context
    def add_time_context(event):
        hour = event.timestamp.hour
        day = event.timestamp.weekday()
        
        if 7 <= hour < 10 and is_weekday:
            tags.append("morning_rush_hour")
        
        if 17 <= hour < 21 and is_weekday:
            tags.append("evening_rush_hour")
        
        return time_tags
```

**Urgency Levels**:
1. **Critical** (immediate action)
   - Accidents with injuries
   - Fire, medical emergencies
   - Major blockages

2. **Needs Attention** (address soon)
   - Power outages
   - Water shortages
   - Traffic jams

3. **Can Wait** (informational)
   - Minor slowdowns
   - Planned construction

4. **Resolved** (completed)
   - Cleared traffic
   - Fixed issues

---

#### Data Validator

**Quality Scoring System**:

```python
class DataValidator:
    
    def calculate_quality_score(event):
        score = 0.0
        
        # Location quality (0.3)
        if has_coordinates:
            score += 0.3
        
        # Description quality (0.2)
        if len(description) > 50:
            score += 0.2
        
        # Geographic detail (0.2)
        if has_zone and has_neighborhood:
            score += 0.2
        
        # Tagging richness (0.1)
        if len(tags) >= 3:
            score += 0.1
        
        # Recency (0.1)
        if event_age < 24_hours:
            score += 0.1
        
        # Source reliability (0.1)
        if source in trusted_sources:
            score += 0.1
        
        return min(score, 1.0)
```

**Validation Rules**:
```python
def validate_event(event):
    errors = []
    
    # Required fields
    if not event.get('id'):
        errors.append("Missing ID")
    
    # Timestamp format
    if not valid_iso_timestamp(event.timestamp):
        errors.append("Invalid timestamp")
    
    # Coordinates range
    if coordinates:
        if not (12.7 <= lat <= 13.2):
            errors.append("Latitude out of Bangalore range")
        if not (77.3 <= lon <= 77.9):
            errors.append("Longitude out of Bangalore range")
    
    return len(errors) == 0, errors
```

---

### 3. Storage Layer

**Firebase Firestore Schema**:

```javascript
processed_events/ (collection)
  ├─ {event_id}/ (document)
      ├─ id: string
      ├─ type: string ["traffic", "civic", "emergency", "social"]
      ├─ subtype: string ["traffic_accident", "civic_power_outage", ...]
      ├─ description: string
      ├─ location: string
      ├─ coordinates: {lat: number, lon: number}
      ├─ full_address: string
      ├─ zone: string ["Central Bangalore", ...]
      ├─ neighborhood: string ["MG Road", ...]
      ├─ urgency: string ["critical", "needs_attention", "can_wait", "resolved"]
      ├─ severity: string ["low", "medium", "high", "critical"]
      ├─ tags: array [string]
      ├─ timestamp: timestamp
      ├─ source: string ["twitter", "google_maps", ...]
      ├─ verified: boolean
      ├─ is_duplicate: boolean
      ├─ duplicate_of: string (event_id)
      ├─ similar_events: array [event_id]
      ├─ quality_score: number (0.0 - 1.0)
      ├─ processed_at: timestamp
      └─ updated_at: timestamp (optional)
```

**Indexes**:
```javascript
// Composite indexes (create in Firebase Console)
1. timestamp DESC
2. zone ASC, timestamp DESC
3. type ASC, timestamp DESC
4. urgency ASC, timestamp DESC
5. tags ARRAY_CONTAINS, timestamp DESC
6. zone ASC, type ASC, timestamp DESC
7. quality_score DESC, timestamp DESC
```

**Security Rules**:
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Processed events - read by anyone, write only by processor
    match /processed_events/{eventId} {
      allow read: if true;
      allow write: if request.auth.token.role == "processor";
    }
  }
}
```

---

## 🔄 Data Flow

### Event Lifecycle

```
1. RAW EVENT (from Person 1)
   ↓
   {
     "id": "twitter_123",
     "type": "traffic",
     "description": "jam on mg road",
     "location": "mg road",
     "timestamp": "2024-01-15T10:30:00Z",
     "source": "twitter"
   }

2. AFTER DEDUPLICATION
   ↓
   {
     ...previous fields,
     "is_duplicate": false,
     "similar_events": ["google_456", "reddit_789"]
   }

3. AFTER GEO-NORMALIZATION
   ↓
   {
     ...previous fields,
     "coordinates": {"lat": 12.9716, "lon": 77.5946},
     "full_address": "MG Road, Shanthala Nagar, Bangalore 560001",
     "zone": "Central Bangalore",
     "neighborhood": "MG Road"
   }

4. AFTER CATEGORIZATION
   ↓
   {
     ...previous fields,
     "subtype": "traffic_congestion",
     "urgency": "needs_attention",
     "tags": ["traffic", "mgroad", "central_bangalore", "morning_rush_hour"]
   }

5. AFTER VALIDATION
   ↓
   {
     ...previous fields,
     "quality_score": 0.75,
     "processed_at": "2024-01-15T10:30:15Z"
   }

6. STORED IN FIREBASE
   ✓ Ready for Member B (AI/ML) and Member C (Frontend)
```

---

## 📊 Performance Characteristics

### Throughput

| Component | Events/sec | Bottleneck |
|-----------|------------|------------|
| Consumer | 1000+ | Network I/O |
| Deduplicator | 500 | O(n²) comparison |
| Geo-Normalizer | 100 | API rate limits |
| Categorizer | 1000+ | CPU (minimal) |
| Validator | 1000+ | CPU (minimal) |
| Storage | 500 | Firestore writes |

**Overall Pipeline**: ~50-100 events/sec (limited by geocoding)

### Scalability

**Horizontal Scaling**:
- Run multiple processor instances
- Kafka consumer groups distribute load
- Firebase handles concurrent writes

**Vertical Scaling**:
- Increase `NUM_WORKERS` for parallel processing
- Add more RAM for larger caches
- Faster CPU for text processing

---

## 🔐 Security

### API Key Management
- Store in `.env` file (not committed)
- Use environment variables
- Rotate keys periodically

### Firebase Security
- Service account with minimal permissions
- Firestore rules restrict writes
- Read access for authenticated users only

### Data Privacy
- No PII (Personal Identifiable Information)
- Anonymize sources when needed
- GDPR compliance (data retention policies)

---

## 📈 Monitoring & Observability

### Metrics Collected

```python
{
  "events_received": int,
  "events_processed": int,
  "events_stored": int,
  "duplicates_found": int,
  "geocoding_success_rate": float,
  "average_quality_score": float,
  "processing_rate": float,  # events/sec
  "error_rate": float,
  "average_processing_time_ms": float
}
```

### Health Checks

```python
def check_health():
    checks = {
        "consumer": check_consumer_connection(),
        "geocoding_api": check_google_maps_api(),
        "storage": check_firebase_connection(),
        "processing_rate": check_rate_acceptable(),
        "error_rate": check_error_rate_low()
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    return overall_status, checks
```

---

## 🚀 Deployment Architecture

### Development
```
Local Machine
├─ Python 3.9
├─ Virtual Environment
├─ .env with test credentials
└─ Manual execution
```

### Staging
```
Cloud VM (e.g., AWS EC2)
├─ Python 3.9
├─ systemd service
├─ .env with staging credentials
└─ Automated restarts
```

### Production
```
Kubernetes Cluster
├─ Docker container
├─ ConfigMap for configuration
├─ Secrets for credentials
├─ Horizontal Pod Autoscaler
├─ Health checks & probes
└─ Logging to CloudWatch/Stackdriver
```

---

## 🔧 Configuration Management

### Environment-based Config

```python
# Development
ENV = "development"
LOG_LEVEL = "DEBUG"
BATCH_SIZE = 10
ENABLE_CACHING = False

# Production
ENV = "production"
LOG_LEVEL = "INFO"
BATCH_SIZE = 50
ENABLE_CACHING = True
```

### Feature Flags

```python
FEATURES = {
    "deduplication": True,
    "geocoding": True,
    "parallel_processing": True,
    "advanced_categorization": False  # Beta feature
}
```

---

## 📚 Further Reading

- [EXPLANATION.md](EXPLANATION.md) - Detailed component explanations
- [QUICKSTART.md](QUICKSTART.md) - Get started quickly
- [TASKS.md](TASKS.md) - Implementation checklist
- [API_REFERENCE.md](API_REFERENCE.md) - Function documentation

---

**Person 2 Architecture: Clean, scalable, and production-ready. 🏗️**
