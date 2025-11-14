#!/bin/bash

# SmartCitySense - Stop All Services
# This script stops all running SmartCitySense services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════"
echo "    🛑 SmartCitySense - Stopping All Services 🛑"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}"

# Project root
PROJECT_ROOT="/Users/kushagrakumar/Desktop/citypulseAI"

# Function to kill process by PID
kill_pid() {
    local pid=$1
    local name=$2
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping $name (PID: $pid)...${NC}"
        kill -9 $pid 2>/dev/null || true
        echo -e "${GREEN}✓ $name stopped${NC}"
    fi
}

# Function to kill process by port
kill_port() {
    local port=$1
    local name=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}Stopping process on port $port ($name)...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        echo -e "${GREEN}✓ Port $port freed${NC}"
    fi
}

# Stop by PIDs if available
if [ -f "$PROJECT_ROOT/.pids" ]; then
    echo -e "${BLUE}Stopping services by PID...${NC}"
    PROCESSING_PID=$(sed -n '1p' "$PROJECT_ROOT/.pids" 2>/dev/null)
    AIML_PID=$(sed -n '2p' "$PROJECT_ROOT/.pids" 2>/dev/null)
    BACKEND_PID=$(sed -n '3p' "$PROJECT_ROOT/.pids" 2>/dev/null)
    FRONTEND_PID=$(sed -n '4p' "$PROJECT_ROOT/.pids" 2>/dev/null)
    
    [ ! -z "$PROCESSING_PID" ] && kill_pid $PROCESSING_PID "Data Processing"
    [ ! -z "$AIML_PID" ] && kill_pid $AIML_PID "AI/ML Service"
    [ ! -z "$BACKEND_PID" ] && kill_pid $BACKEND_PID "Backend API"
    [ ! -z "$FRONTEND_PID" ] && kill_pid $FRONTEND_PID "Frontend"
    
    rm "$PROJECT_ROOT/.pids" 2>/dev/null || true
fi

# Stop by process name (backup method)
echo -e "\n${BLUE}Stopping remaining processes...${NC}"
pkill -9 -f "python.*main.py.*data-processing" 2>/dev/null || true
pkill -9 -f "python.*main.py.*ai-ml" 2>/dev/null || true
pkill -9 -f "uvicorn.*app.main:app" 2>/dev/null || true
pkill -9 -f "next dev" 2>/dev/null || true
pkill -9 -f "node.*next-server" 2>/dev/null || true

# Stop by port (final cleanup)
echo -e "\n${BLUE}Cleaning up ports...${NC}"
kill_port 8000 "Backend API"
kill_port 8001 "AI/ML Service"
kill_port 3000 "Frontend"
kill_port 3001 "Frontend"

echo -e "\n${GREEN}"
echo "═══════════════════════════════════════════════════════════"
echo "    ✅ All Services Stopped! ✅"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}\n"

echo -e "${BLUE}To start services again, run:${NC}"
echo -e "  ${YELLOW}./run-complete-system.sh${NC}\n"
