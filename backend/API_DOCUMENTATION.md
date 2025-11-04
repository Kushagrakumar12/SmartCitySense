# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

Most endpoints require Firebase authentication. Include the Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase-id-token>
```

## Response Format

All responses follow this structure:

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "message": "Success message"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error type",
  "detail": "Error details"
}
```

---

## Endpoints

### 🔐 Authentication

#### Verify Token
```http
POST /auth/verify
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "user": {
    "uid": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "subscriptions": {
      "categories": ["Traffic", "Emergency"],
      "areas": ["Indiranagar"]
    }
  }
}
```

#### Get Profile
```http
GET /auth/profile
Authorization: Bearer <token>
```

#### Update Subscriptions
```http
PUT /auth/subscriptions
Authorization: Bearer <token>
Content-Type: application/json

{
  "categories": ["Traffic", "Emergency", "Cultural"],
  "areas": ["Indiranagar", "Koramangala"]
}
```

---

### 📍 Events

#### List Events
```http
GET /events?category=Traffic&latitude=12.9716&longitude=77.5946&radius_km=5&page=1
```

**Query Parameters:**
- `category` (optional): Traffic, Emergency, Civic Issue, etc.
- `severity` (optional): low, medium, high, critical
- `status` (optional): active, resolved, monitoring
- `area` (optional): Area name
- `latitude` (optional): Latitude for geospatial search
- `longitude` (optional): Longitude for geospatial search
- `radius_km` (optional): Search radius in kilometers
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": "evt123",
      "title": "Heavy Traffic on MG Road",
      "description": "Major congestion due to accident",
      "category": "Traffic",
      "severity": "high",
      "location": {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "area": "Central Bengaluru"
      },
      "status": "active",
      "timestamp": "2025-10-25T10:00:00Z",
      "upvotes": 15,
      "sentiment_score": -0.6
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

#### Get Event
```http
GET /events/{event_id}
```

#### Create Event
```http
POST /events
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Traffic Jam on Old Airport Road",
  "description": "Heavy congestion near HAL",
  "category": "Traffic",
  "severity": "high",
  "location": {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "Old Airport Road",
    "area": "HAL"
  },
  "tags": ["accident", "congestion"]
}
```

#### Upvote Event
```http
POST /events/{event_id}/upvote
```

---

### 📝 Reports

#### Submit Report
```http
POST /reports
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Waterlogged Street",
  "description": "Heavy waterlogging after rain",
  "category": "Civic Issue",
  "location": {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "MG Road"
  },
  "media_urls": [
    "https://storage.googleapis.com/bucket/image1.jpg"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "report": {
    "id": "rpt123",
    "title": "Waterlogged Street",
    "status": "pending",
    "ai_analysis": {
      "vision": {
        "detected_objects": ["water", "road", "vehicles"],
        "confidence": 0.85
      },
      "sentiment": {
        "score": -0.7,
        "label": "negative"
      }
    },
    "created_at": "2025-10-25T10:00:00Z"
  },
  "message": "Report submitted successfully"
}
```

#### List My Reports
```http
GET /reports?status=pending&page=1
Authorization: Bearer <token>
```

---

### 🚨 Alerts

#### List Alerts
```http
GET /alerts?priority=high&is_active=true
```

**Query Parameters:**
- `alert_type`: predictive, anomaly, emergency, trend
- `priority`: low, medium, high, urgent
- `category`: Event category
- `area`: Geographic area
- `is_active`: true/false (default: true)

**Response:**
```json
{
  "success": true,
  "alerts": [
    {
      "id": "alt123",
      "title": "Potential Grid Issue in HSR Layout",
      "message": "Multiple power outage reports detected",
      "alert_type": "predictive",
      "priority": "high",
      "category": "Power Outage",
      "affected_areas": ["HSR Layout", "BTM Layout"],
      "confidence_score": 0.85,
      "recommendations": [
        "Check your UPS/inverter",
        "Report to electricity board"
      ],
      "created_at": "2025-10-25T10:00:00Z",
      "is_active": true
    }
  ],
  "total": 5,
  "has_more": false
}
```

#### Trigger Anomaly Detection
```http
POST /alerts/detect-anomalies?time_window=1h
Authorization: Bearer <token>
```

Analyzes recent events and creates alerts for detected anomalies.

#### Get Alerts for Area
```http
GET /alerts/area/Koramangala
```

---

### 📊 Summaries

#### List Summaries
```http
GET /summaries?category=Traffic&page=1
```

**Response:**
```json
{
  "success": true,
  "summaries": [
    {
      "id": "sum123",
      "title": "Traffic Congestion on Old Airport Road",
      "summary_text": "15 reports of heavy traffic on Old Airport Road due to multi-vehicle accident near HAL. Average delay of 30 minutes. Alternative routes via Marathahalli recommended.",
      "category": "Traffic",
      "event_count": 15,
      "area": "HAL",
      "key_points": [
        "Multi-vehicle accident near HAL",
        "30-minute average delay",
        "15 confirmed reports"
      ],
      "recommendations": [
        "Avoid Old Airport Road until 7 PM",
        "Use Marathahalli route"
      ],
      "sentiment_score": -0.6,
      "created_at": "2025-10-25T10:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

#### Create Summary
```http
POST /summaries
Authorization: Bearer <token>
Content-Type: application/json

{
  "event_ids": ["evt1", "evt2", "evt3", "evt4"],
  "category": "Traffic",
  "area": "HAL"
}
```

#### Auto-Summarize by Category
```http
POST /summaries/auto/category/Traffic?hours=2
Authorization: Bearer <token>
```

Creates an automatic summary of recent traffic events.

#### Auto-Summarize by Area
```http
POST /summaries/auto/area/Koramangala?hours=2
Authorization: Bearer <token>
```

---

## Event Categories

- `Traffic`
- `Emergency`
- `Civic Issue`
- `Cultural`
- `Weather`
- `Power Outage`
- `Water Supply`
- `Protest`
- `Construction`
- `Other`

## Severity Levels

- `low` - Minor issues
- `medium` - Moderate impact
- `high` - Significant impact
- `critical` - Severe/emergency

## Alert Priorities

- `low` - Informational
- `medium` - Worth noting
- `high` - Important
- `urgent` - Immediate attention required

---

## Rate Limiting

- Default: 60 requests per minute per IP
- Authenticated users may have higher limits
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Request limit
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Reset timestamp

---

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Examples

### cURL

```bash
# Get events
curl "http://localhost:8000/api/events?category=Traffic"

# Submit report
curl -X POST http://localhost:8000/api/reports \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","description":"Test report","category":"Civic Issue","location":{"latitude":12.9716,"longitude":77.5946}}'
```

### JavaScript

```javascript
// Get events
const events = await fetch('http://localhost:8000/api/events').then(r => r.json());

// Submit report with auth
const report = await fetch('http://localhost:8000/api/reports', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${firebaseToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(reportData)
}).then(r => r.json());
```

### Python

```python
import requests

# Get events
response = requests.get('http://localhost:8000/api/events')
events = response.json()

# Submit report with auth
headers = {'Authorization': f'Bearer {firebase_token}'}
response = requests.post(
    'http://localhost:8000/api/reports',
    json=report_data,
    headers=headers
)
```

---

For interactive API testing, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
