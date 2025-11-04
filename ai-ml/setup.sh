#!/bin/bash
# Setup script for AI/ML Module
# Run this script to set up the environment automatically

set -e  # Exit on error

echo "============================================================"
echo "🤖 SmartCitySense - AI/ML Module Setup"
echo "============================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies (this may take 5-10 minutes)..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p models logs logs/debug_images
echo "✅ Directories created"

# Copy environment template
echo ""
echo "Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "⚠️  Please edit .env with your configuration"
else
    echo "✅ .env file already exists"
fi

# Test configuration
echo ""
echo "Testing configuration..."
python config/config.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Configuration loaded successfully"
else
    echo "⚠️  Configuration test failed (this is normal if dependencies not fully installed)"
fi

# Download YOLO model
echo ""
echo "Downloading YOLO model (if not exists)..."
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ YOLO model ready"
else
    echo "⚠️  YOLO model download may have failed (will retry on first run)"
fi

# Run basic tests
echo ""
echo "Running basic tests..."
pytest tests/test_vision.py::TestImageClassifier::test_initialization -v -q 2>&1 | grep -q "PASSED"
if [ $? -eq 0 ]; then
    echo "✅ Tests passed"
else
    echo "⚠️  Some tests failed (may need configuration)"
fi

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env file: nano .env"
echo "  2. Add Firebase credentials (optional): firebase-credentials.json"
echo "  3. Start API server: python main.py"
echo "  4. Test API: curl http://localhost:8001/health"
echo "  5. View docs: http://localhost:8001/docs"
echo ""
echo "For detailed instructions, see QUICKSTART.md"
echo ""
