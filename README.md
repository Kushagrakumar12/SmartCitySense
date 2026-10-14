# 🏙️ SmartCitySense

> A real-time intelligent city monitoring and analytics platform powered by AI/ML, designed to make cities smarter by analyzing citizen reports, social media, and visual data.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

**SmartCitySense** is a comprehensive smart city platform that combines real-time data ingestion, AI-powered analysis, and interactive visualization to help city administrators and citizens stay informed about urban events and issues.

### Key Features

- 🔄 **Real-time Data Ingestion** - Multi-source data collection from Reddit, Twitter, sensors, and user reports
- 🤖 **AI/ML Intelligence** - Advanced text summarization, sentiment analysis, computer vision, and predictive analytics
- 📊 **Data Processing Pipeline** - Efficient streaming data processing with Firebase integration
- 🌐 **REST API Backend** - Scalable FastAPI-based backend with comprehensive endpoints
- 💻 **Interactive Dashboard** - Modern React-based frontend with real-time visualization
- 🗺️ **Geospatial Analysis** - Location-based event tracking and mood mapping
- 🚨 **Smart Alerts** - Automated anomaly detection and predictive warnings

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SmartCitySense Platform                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │     Data     │ │     Data     │ │    AI/ML     │
        │  Ingestion   │ │  Processing  │ │   Engine     │
        │   (Member A) │ │  (Member A)  │ │ (Members B1) │
        │              │ │              │ │  (Member B2) │
        │ • Reddit API │ │ • Stream     │ │ • Vision     │
        │ • Twitter    │ │   Processing │ │ • Sentiment  │
        │ • Sensors    │ │ • Firebase   │ │ • Predictive │
        │ • Mock Data  │ │   Integration│ │ • Summary    │
        └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
               │                │                │
               └────────────────┼────────────────┘
                                ▼
                        ┌──────────────┐
                        │   Firebase   │
                        │  (Firestore) │
                        │              │
                        │ • Events     │
                        │ • Analytics  │
                        │ • User Data  │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   Backend    │
                        │ API (FastAPI)│
                        │  (Member D)  │
                        │              │
                        │ • REST API   │
                        │ • WebSocket  │
                        │ • Auth       │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   Frontend   │
                        │    (React)   │
                        │  (Member C)  │
                        │              │
                        │ • Dashboard  │
                        │ • Maps       │
                        │ • Analytics  │
                        └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend services)
- **Node.js 16+** (for frontend)
- **Firebase account** with Firestore enabled
- **API Keys**: Google Gemini, OpenAI (optional), Reddit, Twitter (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SmartCitySense.git
   cd SmartCitySense
   ```

2. **Set up Firebase credentials**
   ```bash
   # Download your Firebase service account key from Firebase Console
   # Place it as firebase-credentials.json in each module directory
   cp your-firebase-key.json ai-ml/firebase-credentials.json
   cp your-firebase-key.json backend/firebase-credentials.json
   cp your-firebase-key.json data-ingestion/firebase-credentials.json
   cp your-firebase-key.json data-processing/firebase-credentials.json
   ```

3. **Run the complete setup**
   ```bash
   chmod +x setup_complete.sh
   ./setup_complete.sh
   ```

   This will:
   - Set up Python virtual environments for all modules
   - Install all dependencies
   - Create necessary directories
   - Set up configuration files

4. **Configure environment variables**
   
   Each module has a `.env.example` file. Copy and configure:
   ```bash
   # AI/ML module
   cd ai-ml
   cp .env.example .env
   # Edit .env with your API keys
   
   # Data Ingestion
   cd ../data-ingestion
   cp .env.example .env
   # Edit .env with Reddit/Twitter credentials
   
   # Repeat for other modules
   ```

5. **Start the system**
   ```bash
   # Option 1: Run complete system
   ./run-complete-system.sh
   
   # Option 2: Run real-time system only
   ./run-realtime-system.sh
   ```

### Verify Installation

```bash
# Check if services are running
ps aux | grep -E "(python.*main|uvicorn)" | grep -v grep

# Test AI/ML API
curl http://localhost:8001/health

# Test Backend API
curl http://localhost:8000/health
```

## 📦 Module Overview

### 🔄 Data Ingestion (`data-ingestion/`)
**Responsibilities**: Real-time data collection from multiple sources

- Reddit API integration for citizen reports
- Twitter stream monitoring (optional)
- Mock data generation for testing
- Real-time event publishing to Firebase
- Rate limiting and error handling

**Key Files**:
- `main_realtime.py` - Real-time data collector
- `connectors/reddit_connector.py` - Reddit API integration
- `config/config.yaml` - Data source configuration

[📖 Full Documentation](data-ingestion/README.md)

### ⚙️ Data Processing (`data-processing/`)
**Responsibilities**: Stream processing and data transformation

- Firebase stream consumer
- Data cleaning and validation
- Event enrichment and categorization
- Storage management
- Real-time analytics aggregation

**Key Files**:
- `main.py` - Stream processor
- `consumers/firebase_consumer.py` - Firebase integration
- `processors/data_processor.py` - Event processing

[📖 Full Documentation](data-processing/README.md)

### 🤖 AI/ML Engine (`ai-ml/`)
**Responsibilities**: Intelligent analysis and predictions

#### Text Intelligence (Member B1)
- 📝 **Text Summarization**: LLM-powered (Gemini/GPT) report summarization
- 💭 **Sentiment Analysis**: BERT-based sentiment detection
- 🗺️ **Mood Mapping**: Location-based sentiment aggregation

#### Vision & Predictive (Member B2)
- 🖼️ **Vision Intelligence**: YOLOv8-based event detection from images/videos
- 🔮 **Predictive Analytics**: Anomaly detection with Isolation Forest
- 📈 **Forecasting**: Time-series prediction with Prophet

**Models Deployed**:
- Google Gemini 1.5 Flash (text summarization)
- OpenAI GPT-4 Turbo (fallback summarization)
- DistilBERT SST-2 (sentiment analysis)
- YOLOv8 nano (object detection)
- Isolation Forest (anomaly detection)
- Prophet (time-series forecasting)

**API Endpoints**: 10 REST endpoints

[📖 Full Documentation](ai-ml/README.md)

### 🌐 Backend API (`backend/`)
**Responsibilities**: REST API and service orchestration

- FastAPI-based REST API
- Request routing and validation
- Authentication and authorization
- WebSocket support for real-time updates
- Integration layer for all services

**Key Features**:
- Comprehensive API documentation (Swagger/ReDoc)
- CORS configuration
- Rate limiting
- Error handling

[📖 Full Documentation](backend/README.md)

### 💻 Frontend Dashboard (`frontend/`)
**Responsibilities**: User interface and visualization

- React-based single-page application
- Interactive map with event markers
- Real-time event feed
- Analytics dashboards
- Sentiment visualization
- Responsive design

**Tech Stack**:
- React 18
- Material-UI
- Leaflet for maps
- Chart.js for analytics
- Axios for API calls

[📖 Full Documentation](frontend/README.md)

## 🛠️ Development

### Project Structure

```
SmartCitySense/
├── data-ingestion/          # Data collection module
│   ├── connectors/          # API connectors
│   ├── pipelines/           # Data pipelines
│   ├── config/              # Configuration
│   └── tests/               # Unit tests
│
├── data-processing/         # Stream processing module
│   ├── consumers/           # Data consumers
│   ├── processors/          # Event processors
│   ├── storage/             # Storage layer
│   └── tests/               # Unit tests
│
├── ai-ml/                   # AI/ML intelligence module
│   ├── text/                # Text processing (B1)
│   ├── vision/              # Computer vision (B2)
│   ├── predictive/          # Predictive models (B2)
│   ├── utils/               # Shared utilities
│   ├── models/              # Trained models
│   └── tests/               # Unit tests
│
├── backend/                 # Backend API module
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── models/          # Data models
│   │   ├── services/        # Business logic
│   │   └── core/            # Core utilities
│   └── tests/               # Unit tests
│
├── frontend/                # Frontend dashboard
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── utils/           # Utilities
│   └── public/              # Static assets
│
├── papers_citypulse/        # Research papers & references
│
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
├── README.md                # This file
├── setup_complete.sh        # Complete setup script
├── run-complete-system.sh   # Run all services
├── run-realtime-system.sh   # Run real-time only
└── stop-all.sh              # Stop all services
```

### Running Tests

```bash
# Test all modules
./test_all.sh

# Test specific module
cd ai-ml && pytest tests/ -v
cd data-ingestion && python -m pytest tests/ -v
cd data-processing && python -m pytest tests/ -v

# Test with coverage
pytest tests/ --cov=. --cov-report=html
```

### Development Scripts

```bash
# Complete setup (first time)
./setup_complete.sh

# Start all services
./run-complete-system.sh

# Stop all services
./stop-all.sh

# Test with 1000 events
./test-1000-events.sh

# Test Reddit API
./validate-reddit-api.sh
```

## 📊 API Documentation

### AI/ML API (Port 8001)

**Base URL**: `http://localhost:8001`

**Text Intelligence**:
- `POST /ai/summarize` - Summarize multiple reports
- `POST /ai/sentiment` - Analyze sentiment
- `POST /ai/mood-map` - Generate city mood map

**Vision Intelligence**:
- `POST /ai/vision/image` - Analyze image
- `POST /ai/vision/video` - Analyze video

**Predictive Analytics**:
- `POST /ai/predict/anomaly` - Detect anomalies
- `POST /ai/predict/forecast` - Forecast events

**Interactive Docs**: http://localhost:8001/docs

### Backend API (Port 8000)

**Base URL**: `http://localhost:8000`

- Integrated API combining all services
- WebSocket support for real-time updates
- Authentication endpoints

**Interactive Docs**: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Each module requires specific environment variables. See `.env.example` in each module directory:

**AI/ML (`ai-ml/.env`)**:
```bash
# LLM Configuration
SUMMARIZATION_LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# Model Settings
YOLO_MODEL_SIZE=n
VISION_CONFIDENCE_THRESHOLD=0.65
SENTIMENT_MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english

# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

**Data Ingestion (`data-ingestion/.env`)**:
```bash
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=SmartCitySense/1.0

# Twitter API (Optional)
TWITTER_BEARER_TOKEN=your_bearer_token
```

## 🚨 Troubleshooting

### Common Issues

**1. Firebase Connection Failed**
```bash
# Ensure firebase-credentials.json exists in module directory
ls -la */firebase-credentials.json

# Check Firebase project ID in credentials file
cat ai-ml/firebase-credentials.json | grep project_id
```

**2. API Key Not Found**
```bash
# Check .env file
cat ai-ml/.env | grep API_KEY

# Ensure no trailing spaces
```

**3. Port Already in Use**
```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>
```

**4. Module Import Errors**
```bash
# Activate virtual environment
source .venv/bin/activate  # or specific module venv

# Reinstall dependencies
pip install -r requirements.txt
```

## 📈 Performance

- **Data Ingestion**: Handles 100+ events/minute
- **AI Processing**: 
  - Text Summarization: ~1.2s per summary
  - Sentiment Analysis: ~0.15s per text
  - Vision Analysis: ~2s per image (CPU), ~0.5s (GPU)
- **API Response Time**: <500ms average
- **Concurrent Users**: Supports 100+ simultaneous connections

## 🔒 Security

- ✅ Sensitive credentials excluded via `.gitignore`
- ✅ Environment variables for all secrets
- ✅ Firebase security rules configured
- ⚠️ **Important**: Never commit `.env` or `firebase-credentials.json` files
- ⚠️ Add authentication before production deployment

## 📝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**SmartCitySense** is developed by a team of students as part of a smart city monitoring project:

- **Member A**: Data Ingestion & Processing
- **Member B1**: Text Intelligence (Summarization & Sentiment)
- **Member B2**: Vision & Predictive Analytics — [harini032424 (Harini J)](https://github.com/harini032424)
- **Member C**: Frontend Dashboard
- **Member D**: Backend API Integration

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- DistilBERT by Hugging Face
- Google Gemini AI
- Firebase by Google
- FastAPI framework
- React community

## 📚 References

Research papers and references can be found in the [`papers_citypulse/`](papers_citypulse/) directory.

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for making cities smarter** 🏙️🤖
