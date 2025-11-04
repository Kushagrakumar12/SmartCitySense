#!/bin/bash
# Run Backend Server

echo "🚀 Starting SmartCitySense Backend..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Using defaults."
fi

# Start server
echo "🌐 Server starting on http://localhost:8000"
echo "📚 API docs available at http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
