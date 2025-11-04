# 🚀 AI-ML Quick Reference

**Server:** http://localhost:8001  
**Status:** ✅ RUNNING

---

## Quick Commands

### Start Server
```bash
cd /Users/kushagrakumar/Desktop/SmartCitySense/ai-ml
nohup venv/bin/python3 main.py > server.log 2>&1 &
```

### Check Status
```bash
curl http://localhost:8001/health
```

### View Logs
```bash
tail -f logs/ai_ml_20251027.log
tail -f server.log
```

### Stop Server
```bash
pkill -f "python3 main.py"
```

---

## Test Endpoints

### Anomaly Detection
```bash
curl -X POST http://localhost:8001/ai/predict/anomaly \
  -H "Content-Type: application/json" \
  -d '{"location": "MG Road", "time_window_minutes": 60}'
```

### Summarization
```bash
curl -X POST http://localhost:8001/ai/summarize \
  -H "Content-Type: application/json" \
  -d '{"reports": ["Traffic jam on MG Road"], "event_type": "traffic"}'
```

---

## Key Info

**Port:** 8001  
**Data Source:** Firebase `processed_events` collection  
**Models:** YOLOv8, BERT, Isolation Forest  
**Docs:** http://localhost:8001/docs
