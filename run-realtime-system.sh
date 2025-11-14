#!/bin/bash

# CityPulse - Real-Time System Startup Script
# This script starts the system with real-time Reddit data + mock data
# Usage: ./run-realtime-system.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/Users/kushagrakumar/Desktop/citypulseAI"

echo -e "${MAGENTA}"
echo "═══════════════════════════════════════════════════════════"
echo "    🔴 CityPulse - REAL-TIME System Startup 🔴"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        echo -e "${YELLOW}Killing process on port $port...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

echo -e "${BLUE}Checking and cleaning ports...${NC}"
check_port 8000  # Backend
check_port 8001  # AI/ML
check_port 3000  # Frontend
check_port 3001  # Frontend alternate

echo -e "${GREEN}✓ Ports cleaned${NC}\n"

# ========================================
# VERIFY REDDIT API CREDENTIALS
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 1: Verifying Reddit API Credentials${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/data-ingestion"

if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found${NC}"
    echo -e "${YELLOW}Please create .env file with Reddit credentials${NC}"
    exit 1
fi

# Check if Reddit credentials are set
REDDIT_CLIENT_ID=$(grep REDDIT_CLIENT_ID .env | cut -d '=' -f2)
REDDIT_CLIENT_SECRET=$(grep REDDIT_CLIENT_SECRET .env | cut -d '=' -f2)

if [ "$REDDIT_CLIENT_ID" == "your_reddit_client_id" ] || [ -z "$REDDIT_CLIENT_ID" ]; then
    echo -e "${RED}✗ Reddit API credentials not configured!${NC}"
    echo ""
    echo -e "${YELLOW}Please set up Reddit API credentials in data-ingestion/.env:${NC}"
    echo "  REDDIT_CLIENT_ID=your_actual_client_id"
    echo "  REDDIT_CLIENT_SECRET=your_actual_client_secret"
    echo ""
    echo -e "${YELLOW}To get Reddit API credentials:${NC}"
    echo "  1. Go to https://www.reddit.com/prefs/apps"
    echo "  2. Click 'Create App' or 'Create Another App'"
    echo "  3. Choose 'script' type"
    echo "  4. Copy the client ID and secret"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Reddit API credentials found${NC}\n"

# ========================================
# START REAL-TIME DATA INGESTION
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 2: Starting Real-Time Data Ingestion${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/data-ingestion"

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found in data-ingestion${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start real-time data ingestion in background
echo -e "${YELLOW}Starting real-time data ingestion...${NC}"
echo -e "${YELLOW}  - Polling Reddit every 60 seconds${NC}"
echo -e "${YELLOW}  - Real-time data ONLY (no mock data)${NC}"
echo -e "${YELLOW}  - Streaming to Firebase${NC}"
nohup bash -c "
    source venv/bin/activate
    python main_realtime.py --mode polling --interval 60 --no-mock
" > logs/ingestion_realtime.log 2>&1 &

INGESTION_PID=$!
echo -e "${GREEN}✓ Real-Time Data Ingestion started (PID: $INGESTION_PID)${NC}"
echo -e "${GREEN}  Log: data-ingestion/logs/ingestion_realtime.log${NC}\n"

# Wait for first Reddit poll
echo -e "${YELLOW}Waiting for first Reddit poll (15 seconds)...${NC}"
sleep 15
echo -e "${GREEN}✓ Real-time ingestion active${NC}\n"

# ========================================
# START DATA PROCESSING
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 3: Starting Data Processing Service${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/data-processing"

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found in data-processing${NC}"
    exit 1
fi

mkdir -p logs

echo -e "${YELLOW}Starting data processing (stream mode with Firebase input)...${NC}"
nohup bash -c "
    source venv/bin/activate
    python main.py stream --input firebase
" > logs/processing.log 2>&1 &

PROCESSING_PID=$!
echo -e "${GREEN}✓ Data Processing started (PID: $PROCESSING_PID)${NC}"
echo -e "${GREEN}  Log: data-processing/logs/processing.log${NC}\n"

sleep 10

# ========================================
# START AI/ML SERVICE
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 4: Starting AI/ML Service (Port 8001)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/ai-ml"

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found in ai-ml${NC}"
    exit 1
fi

mkdir -p logs

check_port 8001

echo -e "${YELLOW}Starting AI/ML FastAPI service...${NC}"
nohup bash -c "
    source venv/bin/activate
    python main.py
" > logs/ai-ml.log 2>&1 &

AIML_PID=$!
echo -e "${GREEN}✓ AI/ML Service started (PID: $AIML_PID)${NC}"
echo -e "${GREEN}  URL: http://localhost:8001${NC}"
echo -e "${GREEN}  API Docs: http://localhost:8001/docs${NC}"
echo -e "${GREEN}  Log: ai-ml/logs/ai-ml.log${NC}\n"

echo -e "${YELLOW}Waiting for AI/ML service to start (15 seconds)...${NC}"
sleep 15

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ AI/ML service is responding${NC}\n"
else
    echo -e "${YELLOW}⚠️  AI/ML service might still be starting up${NC}\n"
fi

# ========================================
# START BACKEND API
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 5: Starting Backend API (Port 8000)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/backend"

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found in backend${NC}"
    exit 1
fi

mkdir -p logs

check_port 8000

echo -e "${YELLOW}Starting Backend FastAPI service...${NC}"
nohup bash -c "
    source venv/bin/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
" > logs/backend.log 2>&1 &

BACKEND_PID=$!
echo -e "${GREEN}✓ Backend API started (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}  URL: http://localhost:8000${NC}"
echo -e "${GREEN}  API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}  Log: backend/logs/backend.log${NC}\n"

echo -e "${YELLOW}Waiting for backend service to start (10 seconds)...${NC}"
sleep 10

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend service is responding${NC}\n"
else
    echo -e "${YELLOW}⚠️  Backend service might still be starting up${NC}\n"
fi

# ========================================
# START FRONTEND
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 6: Starting Frontend (Port 3001)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "${RED}✗ node_modules not found in frontend${NC}"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

mkdir -p logs

check_port 3001

echo -e "${YELLOW}Starting Next.js frontend...${NC}"
nohup npm run dev -- -p 3001 > logs/frontend.log 2>&1 &

FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}  URL: http://localhost:3001${NC}"
echo -e "${GREEN}  Log: frontend/logs/frontend.log${NC}\n"

echo -e "${YELLOW}Waiting for frontend to start (20 seconds)...${NC}"
sleep 20

# ========================================
# SUMMARY
# ========================================
echo -e "${GREEN}"
echo "═══════════════════════════════════════════════════════════"
echo "    ✅ Real-Time System Started Successfully! ✅"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${MAGENTA}🔴 REAL-TIME MODE ACTIVE (REDDIT ONLY)${NC}"
echo -e "${YELLOW}Reddit data is being fetched every 60 seconds${NC}"
echo -e "${YELLOW}Using ONLY real-time data (mock data preserved but not loaded)${NC}\n"

echo -e "${BLUE}📊 Service Status:${NC}"
echo -e "  ${GREEN}✓${NC} Real-Time Ingestion: Running (Reddit ONLY) - PID: $INGESTION_PID"
echo -e "  ${GREEN}✓${NC} Data Processing:    Running (stream mode) - PID: $PROCESSING_PID"
echo -e "  ${GREEN}✓${NC} AI/ML Service:      http://localhost:8001 - PID: $AIML_PID"
echo -e "  ${GREEN}✓${NC} Backend API:        http://localhost:8000 - PID: $BACKEND_PID"
echo -e "  ${GREEN}✓${NC} Frontend:           http://localhost:3001 - PID: $FRONTEND_PID"
echo ""

echo -e "${BLUE}🔗 Quick Links:${NC}"
echo -e "  Frontend:         ${GREEN}http://localhost:3001${NC}"
echo -e "  Backend API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  AI/ML API Docs:   ${GREEN}http://localhost:8001/docs${NC}"
echo ""

echo -e "${BLUE}📁 Log Files:${NC}"
echo -e "  Real-Time Ingestion: ${YELLOW}data-ingestion/logs/ingestion_realtime.log${NC}"
echo -e "  Data Processing:     ${YELLOW}data-processing/logs/processing.log${NC}"
echo -e "  AI/ML Service:       ${YELLOW}ai-ml/logs/ai-ml.log${NC}"
echo -e "  Backend API:         ${YELLOW}backend/logs/backend.log${NC}"
echo -e "  Frontend:            ${YELLOW}frontend/logs/frontend.log${NC}"
echo ""

echo -e "${BLUE}🛑 To stop all services:${NC}"
echo -e "  ${YELLOW}./stop-all.sh${NC}"
echo ""

echo -e "${BLUE}📊 Monitor real-time data:${NC}"
echo -e "  ${YELLOW}tail -f data-ingestion/logs/ingestion_realtime.log${NC}"
echo ""

echo -e "${GREEN}🎉 CityPulse Real-Time System is now running!${NC}"
echo -e "${GREEN}Open http://localhost:3001 to see live Reddit + mock data${NC}"
echo ""

# Save PIDs to file for stop script
echo "$INGESTION_PID" > "$PROJECT_ROOT/.pids"
echo "$PROCESSING_PID" >> "$PROJECT_ROOT/.pids"
echo "$AIML_PID" >> "$PROJECT_ROOT/.pids"
echo "$BACKEND_PID" >> "$PROJECT_ROOT/.pids"
echo "$FRONTEND_PID" >> "$PROJECT_ROOT/.pids"

echo -e "${YELLOW}Process IDs saved to .pids file${NC}"
echo ""
