# 📖 Comprehensive Explanation - Member B2 Tasks

## What This Module Does

The AI/ML module is the **intelligence layer** of SmartCitySense. It takes raw visual data (images and videos) from citizens and automatically understands what's happening, then uses historical patterns to predict future problems.

Think of it as having two superpowers:
1. **Vision** 👁️ - Can "see" and understand city events from photos/videos
2. **Prediction** 🔮 - Can detect unusual patterns and forecast future issues

---

## Part 1: Vision Intelligence (Multimodal Event Analysis)

### What Problem Does It Solve?

**Problem**: Citizens upload photos/videos of city issues (fallen tree, traffic jam, flooding). Manually reviewing thousands of images is impossible.

**Solution**: Automatically detect what's in the image, classify the event type, and generate a description.

### How It Works - Step by Step

#### Image Classification

1. **User Uploads Image**
   ```
   User takes photo of fallen tree blocking road
   → Uploads to CityPulse app
   ```

2. **Image Preprocessing**
   ```python
   # Load image
   image = load_image("fallen_tree.jpg")
   
   # Resize to 640x640 (YOLO input size)
   image = resize(image, (640, 640))
   
   # Convert to RGB tensor
   image_tensor = to_tensor(image)
   ```

3. **YOLO Detection**
   ```python
   # Run YOLO model
   results = model.predict(image_tensor)
   
   # Output: List of detected objects
   # [
   #   {"class": "tree", "confidence": 0.92, "bbox": [120, 340, 580, 720]},
   #   {"class": "road", "confidence": 0.88, "bbox": [0, 600, 640, 640]},
   #   {"class": "car", "confidence": 0.75, "bbox": [400, 450, 520, 580]}
   # ]
   ```

4. **Event Classification**
   ```python
   # Map detected objects to event types
   if "tree" detected AND "road" detected:
       event_type = "obstruction"
       severity = "high"
   ```

5. **Description Generation**
   ```python
   # Generate human-readable description
   description = f"Road obstruction - {objects[0]} blocking path"
   # → "Road obstruction - tree blocking path"
   ```

6. **Save to Database**
   ```python
   # Save to Firebase
   firebase.save_event({
       "event_type": "obstruction",
       "description": "Road obstruction - tree blocking path",
       "confidence": 0.92,
       "location": "MG Road",
       "timestamp": "2025-10-11T14:30:00Z"
   })
   ```

#### Video Analysis

Videos are just sequences of images:

1. **Extract Key Frames**
   ```python
   # Instead of analyzing all 900 frames (30 FPS × 30 sec)
   # Sample every 10th frame → 90 frames
   frames = extract_frames(video, sample_rate=10)
   ```

2. **Analyze Each Frame**
   ```python
   results = []
   for frame in frames:
       result = classify_image(frame)
       results.append(result)
   ```

3. **Aggregate Results**
   ```python
   # Vote for most common event type
   event_type = most_common([r.event_type for r in results])
   
   # Average confidence
   confidence = mean([r.confidence for r in results])
   
   # Take highest severity
   severity = max([r.severity for r in results])
   ```

### Technologies Used

**YOLOv8 (You Only Look Once v8)**:
- State-of-the-art object detection model
- Can detect 80 different object classes
- Fast: 45 FPS on GPU, 5 FPS on CPU
- Accurate: 37.3 mAP (mean Average Precision)

**Why YOLO?**
- Single-stage detector (fast)
- Real-time performance
- Pre-trained on millions of images
- Easy to fine-tune for custom objects

**How YOLO Works** (Simplified):
```
Image → Divide into 7×7 grid → Each cell predicts:
  - Object presence (yes/no)
  - Object class (car, tree, person, etc.)
  - Bounding box coordinates (where is it?)
  - Confidence score (how sure am I?)
```

---

## Part 2: Predictive Modeling

### What Problem Does It Solve?

**Problem**: How do we know if a sudden spike in reports indicates a real emergency vs. normal variation? How can we warn citizens before problems escalate?

**Solution**: 
1. **Anomaly Detection** - Identify unusual patterns
2. **Forecasting** - Predict future event counts

### Anomaly Detection

#### Real-World Example

```
Normal day in Whitefield:
- 10 AM: 2 traffic reports
- 11 AM: 3 traffic reports
- 12 PM: 2 traffic reports

Anomalous day:
- 10 AM: 2 traffic reports
- 11 AM: 15 traffic reports ← ANOMALY!
- 12 PM: 12 traffic reports
```

#### How It Works

1. **Calculate Baseline**
   ```python
   # Get last 7 days of data
   historical = get_events(days=7, event_type="traffic", location="Whitefield")
   
   # Calculate average reports per 15-minute window
   baseline = mean(historical) = 2.5 reports / 15 min
   ```

2. **Check Current Window**
   ```python
   # Count events in last 15 minutes
   current_count = get_recent_events(minutes=15, ...).count()
   # → 12 reports
   ```

3. **Statistical Detection**
   ```python
   # Is current count unusually high?
   if current_count > baseline * 2.5:  # 2.5x normal
       is_statistical_anomaly = True
   # 12 > 2.5 * 2.5 = 6.25 → YES
   ```

4. **ML Detection (Isolation Forest)**
   ```python
   # Prepare features
   features = [
       current_count,           # 12
       hour_of_day,            # 11 (11 AM)
       day_of_week,            # 3 (Wednesday)
       location_encoded        # 15 (Whitefield)
   ]
   
   # Run model
   anomaly_score = model.predict([features])
   # → 0.94 (very anomalous, 0-1 scale)
   ```

5. **Generate Alert**
   ```python
   if is_statistical_anomaly OR anomaly_score > 0.85:
       alert = {
           "message": "Unusual traffic surge in Whitefield - 12 reports in 15 minutes",
           "severity": "high",
           "affected_areas": ["Whitefield", "ITPL"]
       }
       send_alert(alert)
   ```

#### Why Isolation Forest?

**Isolation Forest** works on a simple principle:
- **Anomalies** are rare and different → easy to isolate
- **Normal points** are common and similar → hard to isolate

**How it works**:
```
Build random trees that split data:

Normal point: Car, Tree, Person
├─ Many splits needed to isolate
└─ Deep in tree (path length = 10)

Anomaly: Sudden spike of 50 cars
├─ Few splits needed to isolate
└─ Shallow in tree (path length = 3)

→ Points with short paths = anomalies
```

### Time Series Forecasting

#### Real-World Example

```
Traffic patterns on MG Road:
Mon-Fri: High at 9 AM, 6 PM (office hours)
Weekend: Moderate throughout day
Special events: Spikes unpredictably

Goal: Predict next 24 hours of traffic
```

#### How It Works (Facebook Prophet)

1. **Prepare Historical Data**
   ```python
   # Fetch 30 days of traffic events
   events = get_events(days=30, event_type="traffic")
   
   # Resample to hourly counts
   hourly = events.resample('1H').count()
   
   # Prophet format: 'ds' (datetime), 'y' (value)
   df = pd.DataFrame({
       'ds': hourly.index,
       'y': hourly.values
   })
   ```

2. **Train Prophet Model**
   ```python
   model = Prophet(
       daily_seasonality=True,   # 24-hour patterns
       weekly_seasonality=True   # 7-day patterns
   )
   model.fit(df)
   ```

3. **Generate Forecast**
   ```python
   # Create future dates (next 24 hours)
   future = model.make_future_dataframe(periods=24, freq='H')
   
   # Predict
   forecast = model.predict(future)
   
   # Output for each hour:
   # {
   #   "timestamp": "2025-10-12 09:00",
   #   "predicted_value": 15.2,  # ~15 traffic events expected
   #   "lower_bound": 10.5,      # 95% confidence: could be as low as 10
   #   "upper_bound": 20.1       # 95% confidence: could be as high as 20
   # }
   ```

4. **Identify Peaks**
   ```python
   # Find hours with high predicted traffic
   peaks = [f for f in forecast if f.predicted_value > 20]
   
   # Generate recommendation
   if peaks:
       message = f"High traffic predicted at {peaks[0].timestamp}"
       notify_users(message)
   ```

#### Why Prophet?

**Prophet** is designed for business time series:
- Handles missing data
- Detects seasonality automatically
- Robust to outliers
- Provides confidence intervals
- Easy to use (no complex tuning)

**Components**:
```
y(t) = Trend + Seasonality + Holidays + Error

Trend: Overall direction (increasing/decreasing)
Seasonality: Repeating patterns (daily, weekly)
Holidays: Special events (not used here)
Error: Random noise
```

---

## How Everything Connects

### Complete Flow: User Upload to Alert

```
1. User uploads image of flooding
   ↓
2. Vision module detects "water on road"
   ↓
3. Event saved to Firebase as "flooding" event
   ↓
4. Predictive module queries recent flooding events
   ↓
5. Detects anomaly: 8 flooding reports in 15 minutes (normal: 0-1)
   ↓
6. Generates alert: "Flooding risk in HSR Layout"
   ↓
7. Backend sends push notification to users in area
   ↓
8. Frontend displays red zone on map
```

### Integration with Other Members

```
Member A (Data Ingestion)
  │
  ├─► Collects traffic data from Google Maps
  ├─► Collects social media posts
  └─► Saves to Firebase
        │
        ▼
Member B2 (You) - Vision & Predictive
  │
  ├─► Analyzes user images/videos
  ├─► Detects anomalies in A's data
  └─► Generates forecasts
        │
        ▼
Member D (Backend)
  │
  ├─► Exposes your API to frontend
  ├─► Sends notifications
  └─► Manages user authentication
        │
        ▼
Member C (Frontend)
  └─► Displays your results on map
```

---

## Key Concepts Explained

### 1. Confidence Score
- **Range**: 0.0 to 1.0
- **Meaning**: How sure the model is about its prediction
- **Example**: 0.92 = 92% confident this is a tree

### 2. Bounding Box
- **Format**: [x1, y1, x2, y2]
- **Meaning**: Rectangle coordinates around detected object
- **Example**: [100, 200, 300, 400] = top-left (100,200), bottom-right (300,400)

### 3. Event Type Enum
- **Why**: Standardize event categories across system
- **List**: traffic, obstruction, flooding, fire, protest, civic_issue, etc.
- **Benefit**: Frontend can filter/color-code by type

### 4. Severity Level
- **Levels**: low, medium, high, critical
- **Purpose**: Help prioritize which events need immediate attention
- **Calculation**: Based on object types, event frequency, and context

### 5. Time Window
- **Definition**: Length of time to analyze (e.g., last 15 minutes)
- **Why**: Shorter = more real-time but noisier; Longer = more stable but slower

### 6. Seasonality
- **Daily**: Patterns that repeat every 24 hours (morning/evening rush)
- **Weekly**: Patterns that repeat every 7 days (weekday vs. weekend)

---

## Testing Your Understanding

### Scenario 1: Image Analysis
**Input**: User uploads image with 5 cars, 2 trucks, 1 bus
**Question**: What event type and why?

**Answer**: 
```python
# Count vehicles
vehicle_count = 5 + 2 + 1 = 8 vehicles

# Classification logic
if vehicle_count > 5:
    event_type = "traffic"
    if vehicle_count > 10:
        severity = "high"
    else:
        severity = "medium"

# Result: event_type="traffic", severity="medium"
```

### Scenario 2: Anomaly Detection
**Baseline**: 3 power outage reports/hour normally
**Current**: 15 reports in last 15 minutes (= 60 reports/hour)
**Question**: Is this an anomaly?

**Answer**:
```python
# Statistical check
current_rate = 60 reports/hour
baseline = 3 reports/hour
ratio = 60 / 3 = 20x normal

# Decision
if ratio > 2.5:  # More than 2.5x normal
    is_anomaly = True
    
# Severity
if ratio > 10:
    severity = "critical"
    
# Result: ANOMALY, severity="critical"
# Alert: "Possible grid failure - 15 outage reports"
```

### Scenario 3: Forecasting
**Historical Data**: Traffic peaks at 9 AM (20 events) and 6 PM (25 events)
**Current Time**: 8:30 AM
**Question**: What to forecast for next 2 hours?

**Answer**:
```python
# Prophet learns patterns
model.fit(historical_data)

# Forecast 8:30 AM to 10:30 AM
forecast = model.predict(periods=2)

# Expected output:
# 9:00 AM: 18-22 events (morning peak)
# 10:00 AM: 10-14 events (post-peak)

# Recommendation
if forecast[9_AM] > 20:
    alert = "High traffic expected at 9 AM on MG Road"
```

---

## Common Questions

### Q: What if YOLO detects wrong objects?
**A**: Use confidence threshold. Only trust detections with confidence > 0.65.

### Q: What if there's not enough historical data?
**A**: Anomaly detection falls back to simple statistics (count comparison). Forecasting requires minimum 10 days of data.

### Q: How often should we retrain models?
**A**: 
- Vision (YOLO): Pre-trained, no retraining needed unless custom objects
- Anomaly: Retrain weekly with new data
- Forecast: Retrain daily with rolling window

### Q: What if Firebase is down?
**A**: System operates in "mock mode" - still processes images but doesn't save to database.

### Q: How to handle multiple events in one image?
**A**: YOLO detects all objects. Classification logic picks the most severe:
```python
# Priority: fire > flooding > obstruction > traffic
severity_order = ["fire", "flooding", "obstruction", "traffic"]
event_type = max(detected_events, key=lambda e: severity_order.index(e))
```

---

## Performance Expectations

### Vision Processing Times
| Input | CPU | GPU |
|-------|-----|-----|
| 1 image (640×640) | 1-2 sec | 0.2-0.3 sec |
| 1 video (30 sec, 10 FPS sampling) | 30-60 sec | 5-10 sec |

### Predictive Processing Times
| Operation | Time |
|-----------|------|
| Anomaly detection (query + compute) | 0.5-1 sec |
| Forecast generation (24 hours) | 2-5 sec |
| Model training (30 days data) | 10-30 sec |

### Accuracy Expectations
| Metric | Value |
|--------|-------|
| YOLO detection accuracy (mAP) | 37-50% |
| Event classification accuracy | 70-85% |
| Anomaly detection precision | 60-80% |
| Forecast MAE (Mean Absolute Error) | ±20-30% |

---

## Next Steps for Learning

1. **Understand YOLO deeply**: https://github.com/ultralytics/ultralytics
2. **Learn Isolation Forest**: scikit-learn documentation
3. **Study Prophet**: https://facebook.github.io/prophet/
4. **FastAPI tutorial**: https://fastapi.tiangolo.com/tutorial/
5. **Read the code**: Start with `main.py`, trace through one request

---

**You now understand the complete AI/ML pipeline for CityPulse! 🎉**

This module is the "brain" that transforms raw citizen reports into actionable intelligence for the city.
