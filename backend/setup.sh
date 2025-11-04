#!/bin/bash
# Backend Setup Script

echo "🚀 Setting up SmartCitySense Backend..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration!"
fi

# Check Firebase credentials
if [ ! -f "../data-ingestion/firebase-credentials.json" ]; then
    echo "⚠️  Warning: Firebase credentials not found!"
    echo "Please place firebase-credentials.json in data-ingestion/ folder"
fi

echo "✅ Backend setup complete!"
echo ""
echo "To start the backend:"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
