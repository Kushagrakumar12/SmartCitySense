#!/bin/bash
# Backend Verification Script
# Checks if backend setup is complete and working

echo "🔍 SmartCitySense Backend - Setup Verification"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track issues
ISSUES=0

# Check Python
echo -n "Checking Python installation... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    ISSUES=$((ISSUES + 1))
fi

# Check virtual environment
echo -n "Checking virtual environment... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
else
    echo -e "${YELLOW}⚠${NC} Virtual environment not found (run ./setup.sh)"
    ISSUES=$((ISSUES + 1))
fi

# Check .env file
echo -n "Checking .env configuration... "
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check critical variables
    if grep -q "FIREBASE_CREDENTIALS_PATH" .env; then
        echo "  ├─ Firebase credentials path configured"
    else
        echo -e "  ${YELLOW}├─ Warning: FIREBASE_CREDENTIALS_PATH not set${NC}"
    fi
    
    if grep -q "AI_ML_SERVICE_URL" .env; then
        echo "  ├─ AI/ML service URL configured"
    else
        echo -e "  ${YELLOW}├─ Warning: AI_ML_SERVICE_URL not set${NC}"
    fi
    
    if grep -q "FCM_SERVER_KEY" .env; then
        echo "  └─ FCM server key configured"
    else
        echo -e "  ${YELLOW}└─ Warning: FCM_SERVER_KEY not set${NC}"
    fi
else
    echo -e "${RED}✗${NC} .env file not found (copy from .env.example)"
    ISSUES=$((ISSUES + 1))
fi

# Check Firebase credentials
echo -n "Checking Firebase credentials... "
FIREBASE_CRED_PATH="../data-ingestion/firebase-credentials.json"
if [ -f "$FIREBASE_CRED_PATH" ]; then
    echo -e "${GREEN}✓${NC} Firebase credentials found"
else
    echo -e "${RED}✗${NC} Firebase credentials not found at $FIREBASE_CRED_PATH"
    ISSUES=$((ISSUES + 1))
fi

# Check directory structure
echo -n "Checking directory structure... "
if [ -d "app/routes" ] && [ -d "app/services" ] && [ -d "app/models" ] && [ -d "app/utils" ]; then
    echo -e "${GREEN}✓${NC} All required directories exist"
else
    echo -e "${RED}✗${NC} Missing required directories"
    ISSUES=$((ISSUES + 1))
fi

# Check main files
echo -n "Checking core files... "
MISSING_FILES=()
for file in "app/main.py" "app/config.py" "requirements.txt"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All core files present"
else
    echo -e "${RED}✗${NC} Missing files: ${MISSING_FILES[*]}"
    ISSUES=$((ISSUES + 1))
fi

# Check if dependencies are installed
if [ -d "venv" ]; then
    echo -n "Checking installed packages... "
    source venv/bin/activate
    
    if python -c "import fastapi" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} FastAPI installed"
    else
        echo -e "${RED}✗${NC} FastAPI not installed (run pip install -r requirements.txt)"
        ISSUES=$((ISSUES + 1))
    fi
    
    if python -c "import firebase_admin" 2>/dev/null; then
        echo "  ├─ Firebase Admin SDK installed"
    else
        echo -e "  ${RED}├─ Firebase Admin SDK not installed${NC}"
        ISSUES=$((ISSUES + 1))
    fi
    
    if python -c "import pydantic" 2>/dev/null; then
        echo "  └─ Pydantic installed"
    else
        echo -e "  ${RED}└─ Pydantic not installed${NC}"
        ISSUES=$((ISSUES + 1))
    fi
    
    deactivate
fi

echo ""
echo "=============================================="

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Backend is ready to run.${NC}"
    echo ""
    echo "Start the backend with:"
    echo "  ./run.sh"
    echo ""
    echo "Or manually:"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload --port 8000"
    echo ""
    echo "API documentation will be at:"
    echo "  http://localhost:8000/docs"
else
    echo -e "${RED}✗ Found $ISSUES issue(s). Please fix them before running.${NC}"
    echo ""
    echo "Quick fix:"
    echo "  1. Run ./setup.sh"
    echo "  2. Copy .env.example to .env and configure"
    echo "  3. Ensure Firebase credentials are in place"
fi

echo ""
