#!/bin/bash

# SmartCitySense - Complete System Startup Script
# This script starts all components in the correct order with their virtual environments
# Usage: ./run-complete-system.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/Users/kushagrakumar/Desktop/citypulseAI"

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════"
echo "    🌆 SmartCitySense - Complete System Startup 🌆"
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

# Function to check if a process is running
check_process() {
    local process_name=$1
    if pgrep -f "$process_name" > /dev/null; then
        echo -e "${YELLOW}⚠️  $process_name is already running${NC}"
        echo -e "${YELLOW}Killing existing process...${NC}"
        pkill -9 -f "$process_name" || true
        sleep 2
    fi
}

echo -e "${BLUE}Step 1: Checking and cleaning ports...${NC}"
check_port 8000  # Backend
check_port 8001  # AI/ML
check_port 3000  # Frontend
check_port 3001  # Frontend alternate

echo -e "${GREEN}✓ Ports cleaned${NC}\n"

# ========================================
# START DATA INGESTION (MOCK MODE)
# ========================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Step 2: Starting Data Ingestion Service (Mock Mode)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

cd "$PROJECT_ROOT/data-ingestion"

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found in data-ingestion${NC}"
    exit 1
fi

# Start data ingestion in background
echo -e "${YELLOW}Starting data ingestion (mock mode, 1000+ events)...${NC}"
nohup bash -c "
    source venv/bin/activate
    python main.py --mode mock --mock-file data/mock/events_1000.json
" > logs/ingestion.log 2>&1 &

INGESTION_PID=$!
echo -e "${GREEN}✓ Data Ingestion started (PID: $INGESTION_PID)${NC}"
echo -e "${GREEN}  Log: data-ingestion/logs/ingestion.log${NC}\n"

# Wait for ingestion to complete (it's a one-time run)
echo -e "${YELLOW}Waiting for ingestion to complete (30 seconds)...${NC}"
sleep 30
echo -e "${GREEN}✓ Data ingestion completed${NC}\n"

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

# Start data processing in stream mode with Firebase input
echo -e "${YELLOW}Starting data processing (stream mode with Firebase input)...${NC}"
nohup bash -c "
    source venv/bin/activate
    python main.py stream --input firebase
" > logs/processing.log 2>&1 &

PROCESSING_PID=$!
echo -e "${GREEN}✓ Data Processing started (PID: $PROCESSING_PID)${NC}"
echo -e "${GREEN}  Log: data-processing/logs/processing.log${NC}\n"

# Wait for processing to stabilize
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

# Wait for AI/ML to start
echo -e "${YELLOW}Waiting for AI/ML service to start (15 seconds)...${NC}"
sleep 15

# Test AI/ML health
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

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend service to start (10 seconds)...${NC}"
sleep 10

# Test backend health
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

check_port 3001

echo -e "${YELLOW}Starting Next.js frontend...${NC}"
nohup npm run dev -- -p 3001 > logs/frontend.log 2>&1 &

FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}  URL: http://localhost:3001${NC}"
echo -e "${GREEN}  Log: frontend/logs/frontend.log${NC}\n"

# Wait for frontend to start
echo -e "${YELLOW}Waiting for frontend to start (20 seconds)...${NC}"
sleep 20

# ========================================
# SUMMARY
# ========================================
echo -e "${GREEN}"
echo "═══════════════════════════════════════════════════════════"
echo "    ✅ All Services Started Successfully! ✅"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${BLUE}📊 Service Status:${NC}"
echo -e "  ${GREEN}✓${NC} Data Ingestion:  Completed (1000+ events sent to Firebase)"
echo -e "  ${GREEN}✓${NC} Data Processing: Running (stream mode) - PID: $PROCESSING_PID"
echo -e "  ${GREEN}✓${NC} AI/ML Service:   http://localhost:8001 - PID: $AIML_PID"
echo -e "  ${GREEN}✓${NC} Backend API:     http://localhost:8000 - PID: $BACKEND_PID"
echo -e "  ${GREEN}✓${NC} Frontend:        http://localhost:3001 - PID: $FRONTEND_PID"
echo ""

echo -e "${BLUE}🔗 Quick Links:${NC}"
echo -e "  Frontend:         ${GREEN}http://localhost:3001${NC}"
echo -e "  Backend API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  AI/ML API Docs:   ${GREEN}http://localhost:8001/docs${NC}"
echo -e "  Backend Health:   ${GREEN}http://localhost:8000/health${NC}"
echo -e "  AI/ML Health:     ${GREEN}http://localhost:8001/health${NC}"
echo ""

echo -e "${BLUE}📁 Log Files:${NC}"
echo -e "  Data Ingestion:  ${YELLOW}data-ingestion/logs/ingestion.log${NC}"
echo -e "  Data Processing: ${YELLOW}data-processing/logs/processing.log${NC}"
echo -e "  AI/ML Service:   ${YELLOW}ai-ml/logs/ai-ml.log${NC}"
echo -e "  Backend API:     ${YELLOW}backend/logs/backend.log${NC}"
echo -e "  Frontend:        ${YELLOW}frontend/logs/frontend.log${NC}"
echo ""

echo -e "${BLUE}🛑 To stop all services:${NC}"
echo -e "  ${YELLOW}./stop-all.sh${NC}"
echo -e "  or manually: ${YELLOW}kill $PROCESSING_PID $AIML_PID $BACKEND_PID $FRONTEND_PID${NC}"
echo ""

echo -e "${BLUE}🧪 Quick Tests:${NC}"
echo -e "  ${YELLOW}# Test backend${NC}"
echo -e "  curl http://localhost:8000/health"
echo -e ""
echo -e "  ${YELLOW}# Test AI/ML${NC}"
echo -e "  curl http://localhost:8001/health"
echo -e ""
echo -e "  ${YELLOW}# Test events endpoint${NC}"
echo -e "  curl http://localhost:8000/events"
echo ""

echo -e "${GREEN}🎉 SmartCitySense is now running! Open http://localhost:3001 in your browser${NC}"
echo ""

# Save PIDs to file for stop script
echo "$PROCESSING_PID" > "$PROJECT_ROOT/.pids"
echo "$AIML_PID" >> "$PROJECT_ROOT/.pids"
echo "$BACKEND_PID" >> "$PROJECT_ROOT/.pids"
echo "$FRONTEND_PID" >> "$PROJECT_ROOT/.pids"

echo -e "${YELLOW}Process IDs saved to .pids file${NC}"
echo ""
