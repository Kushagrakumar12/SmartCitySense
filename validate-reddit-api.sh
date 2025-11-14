#!/bin/bash

# Validate Reddit API Credentials
# Quick script to check if Reddit API is properly configured

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════"
echo "    🔍 Reddit API Credentials Validator"
echo "═══════════════════════════════════════════════════════════"
echo -e "${NC}\n"

PROJECT_ROOT="/Users/kushagrakumar/Desktop/citypulseAI"
cd "$PROJECT_ROOT/data-ingestion"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ .env file not found in data-ingestion/${NC}"
    echo -e "${YELLOW}Please create .env file from .env.example${NC}"
    exit 1
fi

echo -e "${GREEN}✓ .env file found${NC}\n"

# Read credentials
REDDIT_CLIENT_ID=$(grep REDDIT_CLIENT_ID .env | cut -d '=' -f2 | tr -d ' "'"'"'')
REDDIT_CLIENT_SECRET=$(grep REDDIT_CLIENT_SECRET .env | cut -d '=' -f2 | tr -d ' "'"'"'')
REDDIT_USER_AGENT=$(grep REDDIT_USER_AGENT .env | cut -d '=' -f2 | tr -d ' "'"'"'')

echo -e "${BLUE}Checking Reddit API credentials...${NC}\n"

# Validate Client ID
if [ -z "$REDDIT_CLIENT_ID" ] || [ "$REDDIT_CLIENT_ID" == "your_reddit_client_id" ]; then
    echo -e "${RED}✗ Reddit Client ID not set${NC}"
    REDDIT_VALID=false
else
    echo -e "${GREEN}✓ Reddit Client ID: ${REDDIT_CLIENT_ID:0:6}...${NC}"
    REDDIT_VALID=true
fi

# Validate Client Secret
if [ -z "$REDDIT_CLIENT_SECRET" ] || [ "$REDDIT_CLIENT_SECRET" == "your_reddit_client_secret" ]; then
    echo -e "${RED}✗ Reddit Client Secret not set${NC}"
    REDDIT_VALID=false
else
    echo -e "${GREEN}✓ Reddit Client Secret: ${REDDIT_CLIENT_SECRET:0:6}...${NC}"
fi

# User Agent
if [ -z "$REDDIT_USER_AGENT" ]; then
    echo -e "${YELLOW}⚠️  Reddit User Agent not set (will use default)${NC}"
else
    echo -e "${GREEN}✓ Reddit User Agent: $REDDIT_USER_AGENT${NC}"
fi

echo ""

# Test connection if credentials are valid
if [ "$REDDIT_VALID" = true ]; then
    echo -e "${BLUE}Testing Reddit API connection...${NC}\n"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        
        # Test with Python
        python -c "
import praw
import sys
from config import Config

try:
    reddit = praw.Reddit(
        client_id=Config.REDDIT_CLIENT_ID,
        client_secret=Config.REDDIT_CLIENT_SECRET,
        user_agent=Config.REDDIT_USER_AGENT
    )
    
    # Try to fetch one post
    subreddit = reddit.subreddit('bangalore')
    post = next(subreddit.hot(limit=1))
    
    print('${GREEN}✓ Reddit API connection successful!${NC}')
    print('${GREEN}✓ Successfully accessed r/bangalore${NC}')
    print(f'${YELLOW}Latest post: {post.title[:60]}...${NC}')
    sys.exit(0)
except Exception as e:
    print(f'${RED}✗ Reddit API connection failed: {str(e)}${NC}')
    sys.exit(1)
" 2>&1
        
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
            echo -e "${GREEN}    ✅ Reddit API is properly configured! ✅${NC}"
            echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
            echo ""
            echo -e "${YELLOW}You can now run the real-time system:${NC}"
            echo -e "  ${BLUE}./run-realtime-system.sh${NC}"
            echo ""
            exit 0
        else
            echo ""
            echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
            echo -e "${RED}    ❌ Reddit API configuration failed${NC}"
            echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
        fi
    else
        echo -e "${RED}✗ Virtual environment not found${NC}"
        echo -e "${YELLOW}Please run: cd data-ingestion && ./setup.sh${NC}"
    fi
else
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}    ❌ Reddit API credentials not configured${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
fi

echo ""
echo -e "${YELLOW}To set up Reddit API credentials:${NC}"
echo ""
echo -e "${BLUE}1. Go to: ${GREEN}https://www.reddit.com/prefs/apps${NC}"
echo -e "${BLUE}2. Click 'Create App' or 'Create Another App'${NC}"
echo -e "${BLUE}3. Fill in the form:${NC}"
echo "   - Name: CityPulse"
echo "   - Type: Select 'script'"
echo "   - Description: City event monitoring"
echo "   - About URL: (leave blank)"
echo "   - Redirect URI: http://localhost:8080"
echo ""
echo -e "${BLUE}4. Click 'Create app'${NC}"
echo ""
echo -e "${BLUE}5. Copy credentials to data-ingestion/.env:${NC}"
echo "   REDDIT_CLIENT_ID=<client id under app name>"
echo "   REDDIT_CLIENT_SECRET=<secret>"
echo "   REDDIT_USER_AGENT=CityPulseAI/1.0"
echo ""
echo -e "${BLUE}6. Run this script again to validate${NC}"
echo ""

exit 1
