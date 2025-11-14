# 🏙️ SmartCitySense - AI-Driven Multimodal Data Fusion for Urban Overload optimization

> Real-time city event monitoring, analysis, and prediction system powered by AI/ML

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Powered](https://img.shields.io/badge/AI-Powered-brightgreen.svg)](https://github.com)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

**SmartCitySense** is an end-to-end intelligent city monitoring platform that collects, processes, analyzes, and visualizes urban data in real-time. The system helps city administrators and citizens stay informed about traffic conditions, civic issues, public sentiment, and potential problems before they escalate.

### Key Capabilities

- **Real-Time Data Collection**: Automated ingestion from multiple sources (traffic APIs, civic portals, social media)
- **Intelligent Processing**: Stream processing pipeline for data validation, enrichment, and aggregation
- **AI-Powered Analysis**: Computer vision for image/video analysis, sentiment analysis for text, and predictive modeling
- **Interactive Dashboard**: Modern web interface for monitoring events, viewing insights, and receiving alerts
- **RESTful APIs**: Comprehensive backend APIs for integration with external systems

## ✨ Features

### 📥 Data Ingestion Module
- Multi-source data collection (Google Maps, civic portals, Twitter, Reddit)
- Real-time and scheduled data fetching
- Event normalization and validation
- Firebase/Kafka streaming support
- Health monitoring and metrics

### � Data Processing Module
- Real-time stream processing
- Data validation and enrichment
- Duplicate detection
- Aggregation and statistics
- Persistent storage

### 🤖 AI/ML Module
**Text Intelligence **:
- Sentiment analysis using transformers
- Named Entity Recognition (NER)
- Topic modeling and classification
- Multi-language support

**Vision & Predictive **:
- Event detection from images/videos (YOLOv8)
- Anomaly detection (Isolation Forest)
- Time series forecasting (Prophet)
- Real-time alert generation

### 🎨 Frontend Module
- Interactive dashboard with real-time updates
- Event timeline and map visualization
- Analytics and reporting
- User authentication and profiles
- Alert management system

### 🔌 Backend API Module
- RESTful API endpoints
- Real-time data streaming
- Authentication and authorization
- Comprehensive documentation
- Rate limiting and caching

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SmartCitySense System                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Traffic API │   │ Civic Portal │   │Social Media  │
│ (Google Maps)│   │  (BBM Portal)│   │(Twitter/etc) │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                   ┌──────▼───────┐
                   │ Data Ingestion│
                   │   (Module A)  │
                   └──────┬────────┘
                          │
                   ┌──────▼────────┐
                   │  Firebase /   │
                   │     Kafka     │
                   └──────┬────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
     ┌──────▼────────┐         ┌───────▼────────┐
     │     Data      │         │    AI/ML       │
     │  Processing   │         │   Analysis     │
     │  (Module C)   │         │  (Modules B)   │
     └──────┬────────┘         └───────┬────────┘
            │                           │
            └─────────────┬─────────────┘
                          │
                   ┌──────▼────────┐
                   │    Backend    │
                   │      API      │
                   │  (Module D)   │
                   └──────┬────────┘
                          │
                   ┌──────▼────────┐
                   │   Frontend    │
                   │  Dashboard    │
                   │  (Module E)   │
                   └───────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Firebase account (optional, for cloud deployment)
- API keys for data sources

### Full System Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/SmartCitySense.git
cd SmartCitySense

# 2. Run complete setup
chmod +x setup_complete.sh
./setup_complete.sh

# 3. Configure Firebase credentials
cp firebase-credentials.json.example firebase-credentials.json
# Edit firebase-credentials.json with your Firebase service account credentials

# 4. Set up environment variables
# Each module has a .env.example - copy and configure them
cp data-ingestion/.env.example data-ingestion/.env
cp ai-ml/.env.example ai-ml/.env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 5. Start the complete system
chmod +x run-complete-system.sh
./run-complete-system.sh
```

The system will start all modules and be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080/docs
- AI/ML API: http://localhost:8001/docs

### Individual Module Setup

#### Data Ingestion
```bash
cd data-ingestion
./setup.sh
python main.py --mode scheduled --interval 5
```

#### Data Processing
```bash
cd data-processing
./setup.sh
python main.py
```

#### AI/ML Module
```bash
cd ai-ml
./setup.sh
python main.py
```

#### Backend API
```bash
cd backend
./setup.sh
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

See individual module README files for detailed setup instructions.

## 📁 Project Structure

```
SmartCitySense/
├── README.md                    # Main project documentation
├── .gitignore                   # Git ignore rules
├── setup_complete.sh            # Complete system setup script
├── run-complete-system.sh       # Start all modules
├── stop-all.sh                  # Stop all running services
├── firebase-credentials.json.example  # Firebase config template
│
├── data-ingestion/              # ✅ Data Collection Module
│   ├── README.md                # Module documentation
│   ├── QUICKSTART.md            # Setup guide
│   ├── ARCHITECTURE.md          # System design
│   ├── requirements.txt         # Python dependencies
│   ├── setup.sh                 # Automated setup
│   ├── main.py                  # Main orchestrator
│   ├── monitoring.py            # Health checks
│   │
│   ├── config/                  # Configuration management
│   │   ├── config.py            # Centralized config
│   │   └── __init__.py
│   │
│   ├── connectors/              # API connectors
│   │   ├── traffic_api.py       # Google Maps traffic
│   │   ├── civic_portal.py      # Government portals
│   │   ├── twitter_api.py       # Social media
│   │   └── __init__.py
│   │
│   ├── pipelines/               # Streaming infrastructure
│   │   ├── kafka_producer.py    # Kafka streaming
│   │   ├── firebase_producer.py # Firebase alternative
│   │   └── __init__.py
│   │
│   ├── utils/                   # Shared utilities
│   │   ├── event_schema.py      # Event structure
│   │   ├── logger.py            # Logging config
│   │   └── __init__.py
│   │
│   ├── tests/                   # Unit tests
│   │   ├── test_connectors.py
│   │   └── __init__.py
│   │
│   └── logs/                    # Log files
│       └── ingestion_*.log
│
└── ai-ml/                       # ✅ Module B2: AI/ML Intelligence (Complete)
    ├── README.md                # Module documentation
    ├── QUICKSTART.md            # Setup guide
    ├── ARCHITECTURE.md          # System design
    ├── EXPLANATION.md           # Conceptual guide
    ├── VISUAL_GUIDE.md          # Visual diagrams
    ├── SUMMARY.md               # Complete summary
    ├── requirements.txt         # Python dependencies
    ├── setup.sh                 # Automated setup
    ├── .env.example             # Environment template
    ├── main.py                  # FastAPI application
    │
    ├── config/                  # Configuration management
    │   ├── config.py            # Centralized config
    │   └── __init__.py
    │
    ├── vision/                  # Vision Intelligence
    │   ├── image_classifier.py  # YOLOv8 image analysis
    │   ├── video_analyzer.py    # Video processing
    │   └── __init__.py
    │
    ├── predictive/              # Predictive Analytics
    │   ├── anomaly_detector.py  # Isolation Forest
    │   ├── timeseries_model.py  # Prophet forecasting
    │   └── __init__.py
    │
    ├── utils/                   # Shared utilities
    │   ├── schemas.py           # Pydantic models
    │   ├── firebase_client.py   # Firebase integration
    │   ├── logger.py            # Logging config
    │   └── __init__.py
    │
    ├── tests/                   # Test suite
    │   ├── test_vision.py       # Vision tests
    │   ├── test_predictive.py   # Predictive tests
    │   ├── test_api.py          # API tests
    │   └── __init__.py
    │
    ├── models/                  # Saved ML models
    │   ├── .gitkeep
    │   └── (model checkpoints)
    │
    └── logs/                    # Log files
        └── app_*.log
```

## 🔧 Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Required API keys:
- **Google Maps API**: Traffic data
- **Twitter Bearer Token**: Social media monitoring
- **Reddit API**: r/bangalore posts
- **Kafka/Firebase**: Streaming backend

See [QUICKSTART.md](QUICKSTART.md) for how to obtain these keys.

## 📊 Event Schema

All events follow this standardized format:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "traffic",
  "source": "google_maps",
  "description": "Heavy traffic on MG Road, 20 min delay",
  "location": "MG Road, Bangalore",
  "coordinates": {
    "lat": 12.9760,
    "lon": 77.6061
  },
  "timestamp": "2025-10-04T10:30:00Z",
  "severity": "high",
  "tags": ["traffic", "delay", "mgroad"],
  "raw_data": {...}
}
```

**Event Types**: `traffic`, `civic`, `cultural`, `emergency`, `weather`, `other`

**Severity Levels**: `low`, `medium`, `high`, `critical`

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific connector
python -m connectors.traffic_api

# Test streaming
python -m pipelines.kafka_producer

# Check configuration
python config/config.py
```

## 📈 Monitoring

The system provides real-time monitoring:

```bash
python main.py --mode scheduled --interval 5
```

Output includes:
- Events collected per source
- Events sent to queue
- Success rates
- API health status
- Error tracking

Logs are saved to `logs/ingestion_YYYYMMDD.log`

## 🛠️ Dependencies

Core packages:
- `requests` - HTTP client
- `googlemaps` - Google Maps API
- `tweepy` - Twitter API
- `praw` - Reddit API
- `kafka-python` - Kafka streaming
- `firebase-admin` - Firebase integration
- `pydantic` - Data validation
- `schedule` - Task scheduling

Install all with:
```bash
pip install -r requirements.txt
```

## 🚦 Usage Examples

### One-time collection
```bash
python main.py --mode once
```

### Scheduled collection (every 5 minutes)
```bash
python main.py --mode scheduled --interval 5
```

### Using Firebase instead of Kafka
```bash
python main.py --mode scheduled --interval 5 --firebase
```

### Help
```bash
python main.py --help
```

## 🔗 Module Integration

### Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SmartCitySense System                          │
└─────────────────────────────────────────────────────────────────────┘

┌───────────────┐      ┌──────────────┐      ┌────────────────────┐
│  Data Sources │      │   Firebase   │      │   AI/ML Module     │
│               │      │  Firestore   │      │                    │
│ • Google Maps │─────▶│              │─────▶│ • Vision Analysis  │
│ • Twitter/X   │      │  Collection: │      │ • Anomaly Detect   │
│ • Reddit      │      │   'events'   │      │ • Forecasting      │
│ • Gov Portals │      │              │      │ • Alert Gen        │
└───────────────┘      └──────────────┘      └────────────────────┘
        │                      │                        │
        ▼                      ▼                        ▼
 Module A Output        Data Store           Module B2 Output
  (Ingestion)          (Shared DB)          (AI Analysis)
```

### Integration Points

**Module A → Firebase:**
- Output: Events pushed to Firestore collection `events`
- Format: Standardized event schema (JSON)
- Frequency: Real-time streaming (5-min intervals)

**Firebase → Module B2:**
- Input: Events queried from `events` collection
- Processing: Vision analysis, anomaly detection, forecasting
- Output: Results saved to `predictions` and `alerts` collections

**Module B2 API:**
- Endpoints available at `http://localhost:8001`
- Interactive docs at `http://localhost:8001/docs`
- Can be consumed by frontend (Member C) or backend (Member D)

### Integration with Other Team Members

**Member B1 (Text Processing):**
- Can consume events from Firebase
- Extract text from social media posts
- Perform NLP analysis
- Save results back to Firebase

**Member C (Frontend):**
- Consumes data from Module B2 REST API
- Displays real-time predictions and alerts
- Visualizes event patterns

**Member D (Backend):**
- Orchestrates data flow between modules
- Implements business logic
- Manages authentication and authorization

## 🐛 Troubleshooting

### Import errors in VS Code
These are just IDE warnings. The code runs fine. To fix:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### API connection failures
The system automatically falls back to mock data for testing. Configure API keys in `.env` for production.

### Kafka connection errors
Either start Kafka locally or use Firebase mode:
```bash
python main.py --firebase
```

### Rate limits
Increase polling interval:
```bash
python main.py --mode scheduled --interval 10
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Setup and usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design details
- **[.env.example](.env.example)** - Configuration template

## ⚙️ Configuration

### Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firestore Database
3. Create a service account and download credentials
4. Save as `firebase-credentials.json` in the root directory

### Environment Variables

Each module requires specific configuration. Copy the `.env.example` files:

```bash
# Data Ingestion
GOOGLE_MAPS_API_KEY=your_key_here
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here

# AI/ML Module
FIREBASE_CREDS_PATH=../firebase-credentials.json
MODEL_PATH=./models/

# Backend
DATABASE_URL=your_database_url
JWT_SECRET=your_secret_key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8080
```

See individual module documentation for complete configuration options.

## 📖 API Documentation

### Backend API (Port 8080)
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

**Main Endpoints**:
- `GET /api/events` - List all events
- `GET /api/events/{id}` - Get event details
- `POST /api/events` - Create new event
- `GET /api/analytics` - Get analytics data
- `GET /api/alerts` - List active alerts

### AI/ML API (Port 8001)
- **Swagger UI**: http://localhost:8001/docs

**Vision Endpoints**:
- `POST /ai/vision/image` - Analyze image
- `POST /ai/vision/video` - Analyze video

**Text Endpoints**:
- `POST /ai/text/sentiment` - Analyze sentiment
- `POST /ai/text/entities` - Extract entities

**Predictive Endpoints**:
- `POST /ai/predict/anomaly` - Detect anomalies
- `POST /ai/predict/forecast` - Generate forecast

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
   ```bash
   cd module-name
   ./test_all.sh
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint/Prettier for TypeScript/JavaScript
- Write tests for new features
- Update documentation
- Keep commits atomic and meaningful

## 🧪 Testing

Each module includes comprehensive tests:

```bash
# Data Ingestion
cd data-ingestion
python -m pytest tests/

# AI/ML Module
cd ai-ml
./test_all.sh

# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## 🐛 Troubleshooting

### Common Issues

**Import errors in VS Code**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**API connection failures**
- System automatically falls back to mock data
- Check API keys in `.env` files
- Verify internet connection

**Firebase connection errors**
- Verify `firebase-credentials.json` is configured correctly
- Check Firebase project permissions
- Ensure Firestore is enabled

**Port already in use**
```bash
# Find and kill process using port
lsof -ti:8080 | xargs kill -9
```

## 🔒 Security Best Practices

- ✅ Never commit API keys or credentials
- ✅ Use environment variables for secrets
- ✅ Keep `firebase-credentials.json` in `.gitignore`
- ✅ Rotate API keys regularly
- ✅ Monitor API usage to avoid unexpected charges
- ✅ Use HTTPS in production
- ✅ Implement rate limiting
- ✅ Validate all user inputs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team & Acknowledgments

Built with ❤️ by the SmartCitySense team.

**Modules**:
- **Module A**: Data Ingestion
- **Module B1**: Text Intelligence (AI/ML)
- **Module B2**: Vision & Predictive Analytics (AI/ML)
- **Module C**: Data Processing
- **Module D**: Backend API
- **Module E**: Frontend Dashboard

## 📞 Support

For issues and questions:
- 📧 Open an issue on GitHub
- 📚 Check module-specific documentation
- 💬 Review troubleshooting section

---

**Built with ❤️ for SmartCitySense**
  -F "file=@traffic_image.jpg" \
  -F "location=MG Road, Bangalore"

# Get anomaly prediction
curl -X POST "http://localhost:8001/ai/predict/anomaly" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "traffic",
    "location": "MG Road",
    "latitude": 12.9716,
    "longitude": 77.5946
  }'
```

**Built with ❤️ for SmartCitySense**

*Making Bangalore smarter, one event at a time.* 🏙️

