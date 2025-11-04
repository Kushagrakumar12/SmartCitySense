# Person 2 - Detailed Explanation
## Data Processing Pipeline

> **Role**: Transform raw city data into clean, structured, actionable intelligence

---

## 🎯 Your Mission

You are **Person 2** in the SmartCitySense team. Person 1 collects raw data from various sources. Your job is to:

1. **Clean** the data (remove duplicates)
2. **Enhance** the data (add location details, categorization)
3. **Validate** the data (ensure quality)
4. **Store** the data (make it accessible for AI/ML and frontend)

---

## 📊 The Big Picture

```
Person 1 (Data Ingestion)
    ↓
[Raw Events: messy, duplicates, incomplete]
    ↓
YOU (Person 2: Data Processing)
    ↓
[Clean Events: deduplicated, geocoded, categorized]
    ↓
Member B (AI/ML) & Member C (Frontend)
```

---

## 🔄 Your Processing Pipeline

### **Input**: Raw Events from Person 1

Example raw event:
```json
{
  "id": "twitter_123",
  "type": "traffic",
  "description": "Jam on mg road",
  "location": "mg road",
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "twitter",
  "tags": ["traffic"]
}
```

**Problems with this data:**
- Location is vague ("mg road" - which part?)
- No coordinates
- Duplicate reports from multiple sources
- Generic categorization
- No urgency indicator
- Poor quality description

---

### **Step 1: Deduplication** 🔍

**Problem**: Multiple sources report the same event
- Twitter user: "Traffic jam on MG Road"
- Google Maps: "Congestion detected on MG Road near Trinity"
- Reddit: "Heavy traffic at MG Road"

These are all the SAME event!

**Solution**: Text similarity + location proximity + time window

**Algorithm**:
```python
def are_events_similar(event1, event2):
    # Must be same type
    if event1.type != event2.type:
        return False
    
    # Must be within 60 minutes
    if abs(event1.timestamp - event2.timestamp) > 60 min:
        return False
    
    # Check text similarity (TF-IDF)
    text_similarity = cosine_similarity(event1.description, event2.description)
    
    # Check location proximity
    if both have coordinates:
        distance = haversine_distance(event1.coords, event2.coords)
        if distance < 2 km:
            return True
    
    # Or high text similarity
    if text_similarity > 0.85:
        return True
    
    return False
```

**Output**:
```json
{
  "id": "twitter_123",
  "is_duplicate": false,
  "similar_events": ["google_456", "reddit_789"]
}
```

---

### **Step 2: Geo-Normalization** 🗺️

**Problem**: Location data is inconsistent
- "mg road" - no coordinates
- "koramangala 5th block" - which exact location?
- Need to map to zones (North/South/East/West/Central Bangalore)

**Solution**: Geocoding + Reverse Geocoding + Zone Mapping

**Process**:
1. **Forward Geocoding**: Address → Coordinates
   - Input: "MG Road, Bangalore"
   - Output: `{lat: 12.9716, lon: 77.5946}`

2. **Reverse Geocoding**: Coordinates → Full Address
   - Input: `{lat: 12.9716, lon: 77.5946}`
   - Output: "MG Road, Shanthala Nagar, Bangalore, Karnataka 560001"

3. **Zone Mapping**: Assign to city zone
   - Central Bangalore
   - North Bangalore
   - South Bangalore
   - East Bangalore
   - West Bangalore

4. **Neighborhood Detection**: Identify specific area
   - MG Road, Koramangala, Whitefield, etc.

**APIs Used**:
- Google Maps Geocoding API (primary, paid, accurate)
- Nominatim (OpenStreetMap) (fallback, free)

**Caching**: 
- Cache 1000 addresses to avoid repeated API calls
- Reduces costs and improves speed

**Output**:
```json
{
  "location": "MG Road",
  "coordinates": {"lat": 12.9716, "lon": 77.5946},
  "full_address": "MG Road, Shanthala Nagar, Bangalore, Karnataka 560001",
  "zone": "Central Bangalore",
  "neighborhood": "MG Road"
}
```

---

### **Step 3: Categorization** 🏷️

**Problem**: Generic categories aren't useful
- "traffic" - is it accident? jam? road closure?
- Need urgency levels
- Need contextual tags

**Solution**: Keyword-based subtype detection + Context analysis

**Event Type Refinement**:

**Traffic** → Subtypes:
- `traffic_accident`: "accident", "crash", "collision"
- `traffic_congestion`: "jam", "slow", "heavy traffic"
- `traffic_road_closure`: "closed", "blocked", "road closed"
- `traffic_construction`: "construction", "repair", "road work"

**Civic** → Subtypes:
- `civic_power_outage`: "power", "electricity", "BESCOM", "blackout"
- `civic_water_shortage`: "water", "tanker", "supply"
- `civic_garbage`: "garbage", "waste", "trash"
- `civic_pothole`: "pothole", "road damage"
- `civic_drainage`: "drainage", "overflow", "sewage"

**Emergency** → Subtypes:
- `emergency_fire`: "fire", "burning", "smoke"
- `emergency_medical`: "ambulance", "medical", "hospital"
- `emergency_crime`: "theft", "robbery", "police"

**Urgency Classification**:

1. **Critical**: Immediate action needed
   - Accidents with injuries
   - Fire, medical emergencies
   - Major road blockages
   - Keywords: "emergency", "urgent", "critical", "ambulance"

2. **Needs Attention**: Should be addressed soon
   - Power outages
   - Water shortages
   - Heavy traffic jams
   - Keywords: "blocked", "outage", "shortage"

3. **Can Wait**: Low priority, informational
   - Minor traffic slowdowns
   - Planned construction
   - General updates

4. **Resolved**: Event is over
   - Keywords: "resolved", "cleared", "fixed", "completed"

**Context Tags**:
- Time-based: `morning_rush_hour`, `evening_rush_hour`, `weekend`
- Weather: `weather_related` (rain, flood, storm)
- Government: `government` (BBMP, BESCOM, BWSSB)
- Location-specific: `mgroad`, `koramangala`, `whitefield`

**Output**:
```json
{
  "type": "traffic",
  "subtype": "traffic_accident",
  "urgency": "critical",
  "tags": [
    "traffic", "accident", "mgroad", "urgent", 
    "central_bangalore", "morning_rush_hour"
  ]
}
```

---

### **Step 4: Validation & Quality Scoring** ⭐

**Problem**: Not all data is equally valuable
- Some events have detailed info, some are vague
- Need to prioritize high-quality data

**Solution**: Multi-factor quality score (0.0 - 1.0)

**Quality Score Formula**:

```python
score = 0.0

# Has coordinates (+0.3)
if has_coordinates:
    score += 0.3

# Has detailed description (+0.2)
if description length > 50 chars:
    score += 0.2

# Has zone/neighborhood (+0.2)
if has_zone and has_neighborhood:
    score += 0.2

# Has multiple tags (+0.1)
if len(tags) >= 3:
    score += 0.1

# Is recent (+0.1)
if event_age < 24 hours:
    score += 0.1

# Is verified source (+0.1)
if source in ['google_maps', 'government']:
    score += 0.1

return min(score, 1.0)
```

**Quality Levels**:
- **0.0 - 0.3**: Poor quality (usually filtered out)
- **0.3 - 0.6**: Acceptable quality
- **0.6 - 0.8**: Good quality
- **0.8 - 1.0**: Excellent quality

**Output**:
```json
{
  "quality_score": 0.85
}
```

---

### **Final Output**: Enhanced Event

After all processing steps:

```json
{
  "id": "twitter_123",
  "type": "traffic",
  "subtype": "traffic_accident",
  "description": "Major accident on MG Road blocking two lanes",
  
  "location": "MG Road",
  "coordinates": {"lat": 12.9716, "lon": 77.5946},
  "full_address": "MG Road, Shanthala Nagar, Bangalore, Karnataka 560001",
  "zone": "Central Bangalore",
  "neighborhood": "MG Road",
  
  "urgency": "critical",
  "severity": "high",
  
  "tags": [
    "traffic", "accident", "mgroad", "urgent",
    "central_bangalore", "morning_rush_hour", "road_block"
  ],
  
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "twitter",
  "verified": false,
  
  "is_duplicate": false,
  "similar_events": ["google_456", "reddit_789"],
  "duplicate_of": null,
  
  "quality_score": 0.85,
  "processed_at": "2024-01-15T10:30:15Z"
}
```

**Value Added**:
✅ Geocoded (coordinates + full address)
✅ Zoned (Central Bangalore)
✅ Categorized (traffic_accident)
✅ Prioritized (critical urgency)
✅ Tagged (7 relevant tags)
✅ Deduplicated (marked 2 similar events)
✅ Quality scored (0.85 - excellent)

---

## 🗄️ Storage Strategy

### Firebase Firestore Structure

**Collection**: `processed_events`

**Indexes Required** (for fast queries):
1. `timestamp` (descending) - Get recent events
2. `zone` + `timestamp` - Events by area
3. `type` + `timestamp` - Events by category
4. `urgency` + `timestamp` - Critical events first
5. `tags` (array-contains) + `timestamp` - Search by tag

**Query Examples**:

```javascript
// Get critical events in Central Bangalore
db.collection('processed_events')
  .where('zone', '==', 'Central Bangalore')
  .where('urgency', '==', 'critical')
  .orderBy('timestamp', 'desc')
  .limit(20)

// Get traffic accidents in last hour
db.collection('processed_events')
  .where('subtype', '==', 'traffic_accident')
  .where('timestamp', '>', one_hour_ago)
  .orderBy('timestamp', 'desc')

// Get events tagged with 'mgroad'
db.collection('processed_events')
  .where('tags', 'array-contains', 'mgroad')
  .orderBy('timestamp', 'desc')
  .limit(50)
```

---

## 📈 Performance Metrics

### Key Metrics to Track:

1. **Processing Rate**: events/second
   - Target: 10-50 events/sec
   
2. **Deduplication Rate**: % duplicates found
   - Expected: 15-30% (multiple sources report same events)
   
3. **Geocoding Success Rate**: % successfully geocoded
   - Target: >80%
   
4. **Average Quality Score**: Overall data quality
   - Target: >0.65
   
5. **Processing Time**: milliseconds per event
   - Target: <100ms per event
   
6. **Error Rate**: % of failures
   - Target: <5%

---

## 🔧 Technologies Explained

### Why These Tools?

**scikit-learn** (Machine Learning):
- TF-IDF vectorization for text similarity
- Cosine similarity calculation
- Why? Better than simple string matching

**NumPy** (Numerical Computing):
- Fast array operations
- Mathematical calculations (Haversine formula)
- Why? Performance for large datasets

**Pandas** (Data Manipulation):
- Batch processing
- Data transformation
- Why? Efficient for structured data

**NLTK** (Natural Language Processing):
- Text preprocessing
- Tokenization
- Why? Better text understanding

**fuzzywuzzy** (Fuzzy String Matching):
- Handle typos and variations
- "mg road" = "MG Road" = "mg rd"
- Why? Real-world text is messy

**geopy** (Geocoding):
- Interface to geocoding services
- Distance calculations
- Why? Abstraction over multiple providers

**googlemaps** (Google Maps API):
- Accurate geocoding
- Address components
- Why? Best geocoding accuracy

**Firebase Admin** (Database):
- Store processed events
- Real-time updates
- Why? Scalable, real-time, easy queries

---

## 🚀 Running Your System

### Mode 1: Batch Processing
Process existing events once and exit.
```bash
python3 main.py batch --max-events 100
```

**Use case**: Testing, backfill, one-time processing

### Mode 2: Stream Processing
Continuously process new events as they arrive.
```bash
python3 main.py stream
```

**Use case**: Production, real-time processing

### Mode 3: Backfill
Reprocess historical events.
```bash
python3 main.py backfill --hours 24
```

**Use case**: Fix processing errors, update logic

---

## 🎓 Key Concepts

### Text Similarity (TF-IDF)

**TF-IDF** = Term Frequency - Inverse Document Frequency

**What it does**: Converts text to numbers that capture meaning

**Example**:
```
Event 1: "Traffic jam on MG Road"
Event 2: "Heavy traffic on MG Road"
Event 3: "Power outage in Koramangala"

TF-IDF Similarity:
Event 1 vs Event 2: 0.89 (very similar - both about MG Road traffic)
Event 1 vs Event 3: 0.12 (different - traffic vs power)
```

### Haversine Distance

**What it does**: Calculates distance between two GPS coordinates

**Formula**: Accounts for Earth's curvature (not flat!)

**Example**:
```python
point1 = (12.9716, 77.5946)  # MG Road
point2 = (12.9352, 77.6245)  # Koramangala

distance = haversine(point1, point2)
# Result: ~5.2 km
```

### Fuzzy Matching

**What it does**: Matches strings even with typos/variations

**Example**:
```python
fuzzy_ratio("MG Road", "mg road") = 100  # Perfect match
fuzzy_ratio("MG Road", "mg rd") = 83     # Close match
fuzzy_ratio("MG Road", "whitefield") = 0 # No match
```

---

## 💡 Design Decisions

### Why Deduplication First?
- Reduces processing load
- Avoids geocoding same location multiple times
- Saves API costs

### Why Multiple Geocoding Providers?
- Reliability (fallback if one fails)
- Cost (free Nominatim for non-critical)
- Accuracy (Google Maps when precision matters)

### Why Cache Geocoding Results?
- Same addresses repeated often ("MG Road", "Koramangala")
- Expensive API calls
- LRU cache = Keep most recent 1000

### Why Quality Scoring?
- Not all data is useful
- Prioritize what to show users
- Filter out noise

---

## 🤝 Integration with Team

### To Person 1 (Data Ingestion):
**You provide**: Schema for raw events
**You need**: Consistent event structure, proper timestamps

### From Person 1:
**You receive**: Raw events via Kafka or Firebase
**Format**: JSON with id, type, description, location, timestamp, source

### To Member B (AI/ML):
**You provide**: Clean, structured, geocoded events
**They need**: Consistent data quality, proper categorization, coordinates

### To Member C (Frontend):
**You provide**: Enriched events ready for display
**They need**: Urgency levels, zones, tags for filtering/search

---

## 📚 Next Steps

1. **Set up environment**: Run `./setup.sh`
2. **Configure APIs**: Add credentials to `.env`
3. **Test components**: Run `python3 test_pipeline.py`
4. **Start processing**: Run `python3 main.py stream`
5. **Monitor performance**: Check `monitoring.py`

---

## 🎯 Success Criteria

You're doing well if:
- ✅ Deduplication rate is 15-30%
- ✅ Geocoding success is >80%
- ✅ Average quality score is >0.65
- ✅ Processing time is <100ms per event
- ✅ Error rate is <5%
- ✅ Member B and C are happy with data quality!

---

**You are Person 2. You make messy data beautiful. 🎨**
