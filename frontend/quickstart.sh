#!/bin/bash

# SmartCitySense Frontend - Quick Start Script
# This script helps you get the frontend running quickly

set -e

echo "🎨 SmartCitySense Frontend - Quick Start"
echo "======================================"
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local not found!"
    echo ""
    echo "Creating .env.local from .env.example..."
    cp .env.example .env.local
    echo ""
    echo "📝 Please edit .env.local and add your API keys:"
    echo "   - Mapbox token"
    echo "   - Firebase configuration"
    echo "   - Backend API URL"
    echo ""
    echo "After updating .env.local, run this script again."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed!"
    echo ""
fi

# Check if components are generated
if [ ! -f "src/components/dashboard/header.tsx" ]; then
    echo "🔨 Generating components..."
    
    if [ -f "./generate-components-part1.sh" ]; then
        chmod +x ./generate-components-part1.sh
        ./generate-components-part1.sh
    fi
    
    if [ -f "./generate-components-part2.sh" ]; then
        chmod +x ./generate-components-part2.sh
        ./generate-components-part2.sh
    fi
    
    if [ -f "./generate-components-final.sh" ]; then
        chmod +x ./generate-components-final.sh
        ./generate-components-final.sh
    fi
    
    echo "✅ Components generated!"
    echo ""
fi

echo "✨ Setup complete!"
echo ""
echo "🚀 Starting development server..."
echo ""
echo "Your SmartCitySense dashboard will be available at:"
echo "   http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
