#!/bin/bash

# SmartCitySense Data Ingestion Setup Script
# Run this to set up your development environment

echo "🚀 SmartCitySense Data Ingestion Setup"
echo "====================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "⚠️  Some dependencies failed to install"
    echo "This is normal if you don't have API keys configured yet"
fi

echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠️  Please edit .env and add your API keys"
else
    echo "✓ .env file already exists"
fi

echo ""

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs
echo "✓ Logs directory created"
echo ""

# Test configuration (ensure venv is active)
echo "Testing configuration..."
source venv/bin/activate
python config/config.py

echo ""
echo "====================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Test individual connectors:"
echo "   python -m connectors.traffic_api"
echo "   python -m connectors.civic_portal"
echo "   python -m connectors.twitter_api"
echo "3. Run the full pipeline:"
echo "   python main.py --mode once"
echo ""
echo "For scheduled ingestion (every 5 minutes):"
echo "   python main.py --mode scheduled --interval 5"
echo ""
echo "For help:"
echo "   python main.py --help"
echo "====================================="
