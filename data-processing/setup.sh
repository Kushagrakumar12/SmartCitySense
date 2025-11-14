#!/bin/bash

# Person 2 - Data Processing Pipeline Setup Script
# Sets up the complete environment for data processing

echo "================================================="
echo "🚀 SmartCitySense - Person 2 Setup"
echo "   Data Processing Pipeline"
echo "================================================="
echo

# Check Python version
echo "📌 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi
echo "✓ Python OK"
echo

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - Firebase credentials"
    echo "   - Google Maps API key"
    echo "   - Kafka settings (if using)"
    echo
else
    echo "✓ .env file already exists"
    echo
fi

# Create logs directory
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p cache
echo "✓ Directories created"
echo

# Test imports
echo "🧪 Testing imports..."
python3 -c "
import sys
try:
    from config import Config
    from utils import setup_logger
    from processors import EventDeduplicator, GeoNormalizer, EventCategorizer
    from storage import FirebaseStorage
    print('✓ Core imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
echo

# Print next steps
echo "================================================="
echo "✅ Setup Complete!"
echo "================================================="
echo
echo "📋 Next Steps:"
echo
echo "1. Configure your environment:"
echo "   nano .env"
echo
echo "2. Add your credentials:"
echo "   - Firebase Project ID & credentials"
echo "   - Google Maps API key"
echo "   - Kafka broker (optional)"
echo
echo "3. Test the configuration:"
echo "   python3 config/config.py"
echo
echo "4. Run in batch mode:"
echo "   python3 main.py batch"
echo
echo "5. Or run in stream mode (continuous):"
echo "   python3 main.py stream"
echo
echo "6. Monitor performance:"
echo "   python3 monitoring.py"
echo
echo "================================================="
echo "📚 Documentation:"
echo "   - README.md - Overview and architecture"
echo "   - docs/ - Detailed documentation"
echo "================================================="
echo

echo "Happy processing! 🎉"
