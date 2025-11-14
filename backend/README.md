# SmartCitySense Backend

Backend API service for SmartCitySense - provides REST APIs for events, reports, alerts, summaries, and user management.

## 🏗️ Architecture

The backend is built with **FastAPI** and follows a layered architecture:

```
backend/
├── app/
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   ├── models/         # Pydantic models
│   ├── utils/          # Helper functions
│   └── tests/          # Unit tests
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
└── setup.sh           # Setup script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Firebase credentials (from data-ingestion folder)
- AI/ML service running (from ai-ml folder)

### Setup

```bash
# Make setup script executable
chmod +x setup.sh run.sh

# Run setup
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start the server
./run.sh
```

The server will start on `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000
```

## 📡 API Endpoints

### Authentication (`/api/auth`)
- `POST /verify` - Verify Firebase token
- `GET /profile` - Get user profile
- `PUT /profile` - Update profile
- `PUT /subscriptions` - Update notification subscriptions
- `POST /fcm-token` - Update FCM device token

### Events (`/api/events`)
- `GET /` - List events (with filters)
- `GET /{id}` - Get event details
- `POST /` - Create event
- `PUT /{id}` - Update event
- `POST /{id}/upvote` - Upvote event
- `GET /category/{category}` - Get events by category
- `GET /area/{area}` - Get events by area

### Reports (`/api/reports`)
- `POST /` - Submit citizen report
- `GET /` - List user's reports
- `GET /{id}` - Get report details

### Alerts (`/api/alerts`)
- `GET /` - List alerts
- `GET /{id}` - Get alert details
- `POST /detect-anomalies` - Trigger anomaly detection
- `GET /area/{area}` - Get alerts for area

### Summaries (`/api/summaries`)
- `GET /` - List summaries
- `GET /{id}` - Get summary details
- `POST /` - Create summary from events
- `POST /auto/category/{category}` - Auto-summarize by category
- `POST /auto/area/{area}` - Auto-summarize by area

## 🔒 Authentication

The backend uses **Firebase Authentication**. Protected endpoints require a Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase-id-token>
```

## 🔗 Integration with Other Services

### AI/ML Service
The backend communicates with the AI/ML service for:
- Event summarization
- Image/video analysis
- Sentiment analysis
- Anomaly detection

Configure AI/ML service URL in `.env`:
```
AI_ML_SERVICE_URL=http://localhost:8001
```

### Data Ingestion
Events from data-ingestion pipelines are stored in Firebase and accessed via the backend API.

### Frontend
The frontend application calls these REST APIs to:
- Display events on map
- Submit reports
- Show alerts and summaries
- Manage user subscriptions

## 🗄️ Database Schema

### Firestore Collections

**users/**
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "subscriptions": {
    "categories": ["Traffic", "Emergency"],
    "areas": ["Indiranagar", "Koramangala"]
  },
  "fcm_token": "device-token",
  "created_at": "2025-10-25T10:00:00Z"
}
```

**events/**
```json
{
  "title": "Traffic on MG Road",
  "description": "Heavy congestion",
  "category": "Traffic",
  "severity": "high",
  "location": {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "area": "Central Bengaluru"
  },
  "status": "active",
  "timestamp": "2025-10-25T10:00:00Z",
  "sentiment_score": -0.5,
  "upvotes": 15
}
```

**reports/**
```json
{
  "title": "Waterlogged street",
  "description": "Heavy waterlogging",
  "category": "Civic Issue",
  "location": {...},
  "reported_by": "user_id",
  "media_urls": ["url1", "url2"],
  "ai_analysis": {...},
  "status": "pending"
}
```

**alerts/**
```json
{
  "title": "Potential Grid Issue",
  "message": "Multiple power outage reports",
  "alert_type": "predictive",
  "priority": "high",
  "affected_areas": ["HSR Layout"],
  "confidence_score": 0.85,
  "recommendations": ["Check UPS"]
}
```

**summaries/**
```json
{
  "title": "Traffic Summary",
  "summary_text": "15 reports of heavy traffic...",
  "source_event_ids": ["evt1", "evt2"],
  "event_count": 15,
  "key_points": ["Accident at HAL"],
  "recommendations": ["Use alternate route"]
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py
```

## 🐳 Docker Deployment

```bash
# Build image
docker build -t citypulse-backend .

# Run container
docker run -p 8000:8000 \
  -e FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json \
  -e AI_ML_SERVICE_URL=http://ai-ml:8001 \
  citypulse-backend
```

## 🔧 Configuration

Key environment variables (in `.env`):

```bash
# App
DEBUG=false
PORT=8000

# Firebase
FIREBASE_CREDENTIALS_PATH=../data-ingestion/firebase-credentials.json
FCM_SERVER_KEY=your-fcm-key

# AI/ML Service
AI_ML_SERVICE_URL=http://localhost:8001

# Security
SECRET_KEY=your-secret-key
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📊 Monitoring

Health check endpoint: `GET /health`

Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-25T10:00:00Z",
  "services": {
    "backend": "healthy",
    "firebase": "healthy",
    "ai_ml": "healthy"
  }
}
```

## 🔐 Security Features

- ✅ Firebase authentication
- ✅ Rate limiting (60 requests/minute by default)
- ✅ CORS configuration
- ✅ Request logging
- ✅ Input validation with Pydantic
- ✅ Secure token verification

## 🤝 Integration Examples

### Submitting a Report (Frontend)

```javascript
const response = await fetch('http://localhost:8000/api/reports', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${firebaseToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Waterlogged Street',
    description: 'Heavy waterlogging on main road',
    category: 'Civic Issue',
    location: {
      latitude: 12.9716,
      longitude: 77.5946,
      area: 'MG Road'
    },
    media_urls: ['https://storage.../image.jpg']
  })
});
```

### Getting Events (Frontend)

```javascript
const response = await fetch(
  'http://localhost:8000/api/events?category=Traffic&radius_km=5&latitude=12.9716&longitude=77.5946'
);
const data = await response.json();
// data.events contains filtered events
```

## 📝 Development

### Adding a New Endpoint

1. Create model in `app/models/`
2. Create service in `app/services/`
3. Create route in `app/routes/`
4. Add router to `app/main.py`
5. Write tests in `app/tests/`

### Code Style

- Use type hints
- Follow PEP 8
- Document functions with docstrings
- Use async/await for I/O operations

## 🐛 Troubleshooting

**Firebase connection fails**
- Check `firebase-credentials.json` path
- Verify Firebase project configuration

**AI/ML service unavailable**
- Ensure ai-ml service is running
- Check `AI_ML_SERVICE_URL` in `.env`

**Rate limit errors**
- Adjust `RATE_LIMIT_PER_MINUTE` in `.env`
- Implement authentication for higher limits

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 👥 Support

For issues or questions, refer to the main project README or create an issue in the repository.
