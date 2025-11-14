#!/bin/bash
# SmartCitySense/ML Module - Quick Test Script
# Run this to verify everything is working

echo "🧪 SmartCitySense/ML Test Runner"
echo "=============================="
echo ""

# Check if in correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Not in ai-ml directory!"
    echo "Please run: cd /Users/kushagrakumar/Desktop/citypulseAI/ai-ml"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Run tests
echo "🧪 Running all tests..."
echo ""

pytest tests/ -v --tb=short --disable-warnings

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ ALL TESTS PASSED! 🎉"
    echo "================================"
    echo ""
    echo "Your AI/ML module is ready to use!"
    echo ""
    echo "Next steps:"
    echo "  1. Start the server: python3 main.py"
    echo "  2. Open API docs: http://localhost:8001/docs"
    echo "  3. Test endpoints: curl http://localhost:8001/health"
    echo ""
else
    echo ""
    echo "================================"
    echo "❌ Some tests failed"
    echo "================================"
    echo ""
    echo "Check the output above for details."
    echo "Run with more details: pytest tests/ -v"
    echo ""
fi
