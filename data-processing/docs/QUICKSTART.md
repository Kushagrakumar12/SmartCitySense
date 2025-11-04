# Quick Start Guide
## Person 2 - Data Processing Pipeline

Get up and running in 5 minutes!

---

## Prerequisites

- Python 3.8 or higher
- Firebase account (for storage)
- Google Maps API key (for geocoding)
- Access to Person 1's output (Kafka or Firebase)

---

## Installation

### Step 1: Clone and Navigate
```bash
cd data-processing
```

### Step 2: Run Setup Script
```bash
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create .env file template
- Set up directories

---

## Configuration

### Step 3: Edit .env File
```bash
nano .env
```

**Required Settings:**
```env
# Firebase (Required for output)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_PATH=/path/to/serviceAccountKey.json

# Google Maps (Required for geocoding)
GOOGLE_MAPS_API_KEY=your-api-key

# Input Source (Choose one)
# Option 1: Kafka
KAFKA_BROKER=localhost:9092
KAFKA_TOPIC=smartcitysense_events

# Option 2: Firebase Input
FIREBASE_INPUT_COLLECTION=events
```

**Optional Settings:**
```env
# Processing Tuning
BATCH_SIZE=50
SIMILARITY_THRESHOLD=0.85
TIME_WINDOW_MINUTES=60
DISTANCE_THRESHOLD_KM=2

# Performance
ENABLE_CACHING=true
PARALLEL_PROCESSING=true
NUM_WORKERS=4
```

---

## Get Firebase Credentials

### Step 1: Go to Firebase Console
https://console.firebase.google.com

### Step 2: Select Your Project

### Step 3: Project Settings → Service Accounts

### Step 4: Generate New Private Key
- Click "Generate new private key"
- Save the JSON file
- Update `FIREBASE_PRIVATE_KEY_PATH` in .env

### Step 5: Create Firestore Database
- Go to Firestore Database
- Click "Create database"
- Start in **production mode**
- Choose location closest to your users

### Step 6: Create Collection
- Collection ID: `processed_events`
- Add a dummy document (will be replaced)

---

## Get Google Maps API Key

### Step 1: Go to Google Cloud Console
https://console.cloud.google.com

### Step 2: Enable APIs
- Geocoding API
- Places API (optional)

### Step 3: Create Credentials
- APIs & Services → Credentials
- Create Credentials → API Key
- Copy the API key
- Update `GOOGLE_MAPS_API_KEY` in .env

### Step 4: Restrict API Key (Recommended)
- API restrictions: Select only Geocoding API
- Application restrictions: IP addresses (add your server IP)

---

## Testing

### Test Configuration
```bash
python3 config/config.py
```

Expected output:
```
📋 Person 2 - Data Processing Configuration
============================================
🔌 INPUT SOURCES:
  Kafka: ✓ Configured
  Firebase Input: ✓ Configured

💾 OUTPUT STORAGE:
  Firebase: ✓ Configured

🗺️  GEOCODING:
  Google Maps: ✓ Configured
```

### Test Components

**Test Deduplicator:**
```bash
python3 processors/deduplicator.py
```

**Test Geo-Normalizer:**
```bash
python3 processors/geo_normalizer.py
```

**Test Categorizer:**
```bash
python3 processors/event_categorizer.py
```

**Test Full Pipeline:**
```bash
python3 test_pipeline.py
```

---

## Running

### Mode 1: Batch Processing
Process a batch of events once:
```bash
python3 main.py batch
```

With options:
```bash
python3 main.py batch --max-events 100 --input kafka
```

### Mode 2: Stream Processing (Recommended)
Continuously process new events:
```bash
python3 main.py stream
```

**Note**: This runs indefinitely. Press `Ctrl+C` to stop.

### Mode 3: Backfill
Reprocess historical events:
```bash
python3 main.py backfill --hours 24
```

---

## Monitoring

### Real-time Stats
The pipeline prints statistics periodically during processing.

### Generate Report
```bash
python3 monitoring.py
```

### Check Logs
```bash
tail -f logs/data_processing.log
```

---

## Common Issues

### Issue: "Firebase not initialized"
**Solution**: Check that `FIREBASE_PROJECT_ID` is set in .env

### Issue: "Kafka connection failed"
**Solution**: 
1. Check that Kafka is running: `systemctl status kafka`
2. Verify `KAFKA_BROKER` address in .env

### Issue: "Geocoding API error"
**Solution**:
1. Check API key is valid
2. Verify APIs are enabled in Google Cloud Console
3. Check for rate limit errors (upgrade plan if needed)

### Issue: "No events to process"
**Solution**:
1. Verify Person 1 is running and publishing events
2. Check input collection/topic exists
3. Check permissions on Firebase

### Issue: "Import errors"
**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Production Deployment

### Using systemd (Linux)

Create service file: `/etc/systemd/system/smartcitysense-processor.service`

```ini
[Unit]
Description=SmartCitySense Data Processor (Person 2)
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/data-processing
ExecStart=/path/to/data-processing/venv/bin/python3 main.py stream
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable smartcitysense-processor
sudo systemctl start smartcitysense-processor
sudo systemctl status smartcitysense-processor
```

View logs:
```bash
sudo journalctl -u smartcitysense-processor -f
```

---

## Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py", "stream"]
```

Build and run:
```bash
docker build -t smartcitysense-processor .
docker run -d --name processor \
  --env-file .env \
  smartcitysense-processor
```

---

## Performance Tuning

### High Volume (>100 events/sec)
```env
BATCH_SIZE=100
PARALLEL_PROCESSING=true
NUM_WORKERS=8
ENABLE_CACHING=true
```

### Low Resources (Small server)
```env
BATCH_SIZE=20
PARALLEL_PROCESSING=false
NUM_WORKERS=2
ENABLE_CACHING=true
```

### Better Deduplication
```env
SIMILARITY_THRESHOLD=0.80  # More aggressive (finds more duplicates)
TIME_WINDOW_MINUTES=90     # Longer window
DISTANCE_THRESHOLD_KM=3    # Larger area
```

### Stricter Deduplication
```env
SIMILARITY_THRESHOLD=0.90  # More conservative
TIME_WINDOW_MINUTES=30     # Shorter window
DISTANCE_THRESHOLD_KM=1    # Smaller area
```

---

## Next Steps

1. ✅ Set up environment
2. ✅ Configure credentials
3. ✅ Test components
4. ✅ Run pipeline
5. 📖 Read [EXPLANATION.md](EXPLANATION.md) for deep dive
6. 🏗️ Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
7. 👥 Coordinate with Member B (AI/ML) and Member C (Frontend)

---

## Support

- Check logs: `logs/data_processing.log`
- Run tests: `python3 test_pipeline.py`
- Review docs: `docs/` directory
- Monitor metrics: `python3 monitoring.py`

---

**Happy Processing! 🚀**
