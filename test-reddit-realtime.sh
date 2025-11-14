#!/bin/bash

# Quick Test Script for Real-Time Reddit Connector
# Tests if Reddit API is working without starting the full system

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════"
echo "    🧪 Reddit Real-Time Connector Test"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}\n"

cd /Users/kushagrakumar/Desktop/citypulseAI/data-ingestion

if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

echo -e "${YELLOW}Testing Reddit connector...${NC}\n"

python connectors/reddit_realtime.py

echo -e "\n${BLUE}Test complete!${NC}"
