#!/bin/bash

################################################################################
# SmartCitySense - Complete Data Engineering Setup Script
# Sets up both data-ingestion (Person 1) and data-processing (Person 2)
################################################################################

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                   ║"
echo "║     🚀 SmartCitySense - Data Engineering Complete Setup 🚀        ║"
echo "║                                                                   ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="/Users/kushagrakumar/Desktop/citypulseAI"

echo "📁 Project Root: $PROJECT_ROOT"
echo

################################################################################
# STEP 1: Setup Data-Ingestion (Person 1)
################################################################################

echo "═══════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 1: Setting up Data-Ingestion (Person 1)${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo

cd "$PROJECT_ROOT/data-ingestion"

# Check if venv exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing data-ingestion dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}✗${NC} requirements.txt not found!"
    exit 1
fi

# Check .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}⚠${NC}  .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠${NC}  Please edit .env with your credentials"
    fi
fi

# Create logs directory
mkdir -p logs
mkdir -p data/mock
echo -e "${GREEN}✓${NC} Directories created"

echo
echo -e "${GREEN}✅ Data-Ingestion setup complete!${NC}"
echo

################################################################################
# STEP 2: Setup Data-Processing (Person 2)
################################################################################

echo "═══════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 2: Setting up Data-Processing (Person 2)${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo

cd "$PROJECT_ROOT/data-processing"

# Check if venv exists
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing data-processing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${RED}✗${NC} requirements.txt not found!"
    exit 1
fi

# Check .env file
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}⚠${NC}  .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠${NC}  Please edit .env with your credentials"
    fi
fi

# Create directories
mkdir -p logs
mkdir -p cache
echo -e "${GREEN}✓${NC} Directories created"

echo
echo -e "${GREEN}✅ Data-Processing setup complete!${NC}"
echo

################################################################################
# STEP 3: Verify Python and Dependencies
################################################################################

echo "═══════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 3: Verifying Installation${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo

cd "$PROJECT_ROOT/data-ingestion"
source venv/bin/activate

echo "📌 Data-Ingestion:"
echo "   Python: $(python3 --version)"
echo "   Pip: $(pip --version | cut -d' ' -f2)"
echo "   Installed packages: $(pip list --format=freeze | wc -l | xargs)"

cd "$PROJECT_ROOT/data-processing"
source venv/bin/activate

echo
echo "📌 Data-Processing:"
echo "   Python: $(python3 --version)"
echo "   Pip: $(pip --version | cut -d' ' -f2)"
echo "   Installed packages: $(pip list --format=freeze | wc -l | xargs)"

echo

################################################################################
# STEP 4: Summary
################################################################################

echo "═══════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo
echo "📋 Next Steps:"
echo
echo "1️⃣  Configure Data-Ingestion:"
echo "   cd $PROJECT_ROOT/data-ingestion"
echo "   nano .env  # Add your API keys"
echo
echo "2️⃣  Configure Data-Processing:"
echo "   cd $PROJECT_ROOT/data-processing"
echo "   nano .env  # Add Firebase credentials"
echo
echo "3️⃣  Generate Mock Data (100+ events):"
echo "   cd $PROJECT_ROOT/data-ingestion"
echo "   source venv/bin/activate"
echo "   python3 utils/generate_mock_data.py"
echo
echo "4️⃣  Test Data-Ingestion:"
echo "   cd $PROJECT_ROOT/data-ingestion"
echo "   source venv/bin/activate"
echo "   python3 main.py --mode mock --events 50"
echo
echo "5️⃣  Test Data-Processing:"
echo "   cd $PROJECT_ROOT/data-processing"
echo "   source venv/bin/activate"
echo "   python3 test_pipeline.py"
echo
echo "6️⃣  Run Complete Pipeline:"
echo "   Terminal 1: cd data-ingestion && source venv/bin/activate && python3 main.py --mode mock --events 100"
echo "   Terminal 2: cd data-processing && source venv/bin/activate && python3 main.py batch"
echo
echo "═══════════════════════════════════════════════════════════════════"
echo
echo -e "${GREEN}🎉 You're all set! Happy coding! 🎉${NC}"
echo
