#!/bin/bash

# SmartCitySense Frontend Setup Script
# This script creates all necessary frontend files and structure

set -e

echo "🚀 Setting up SmartCitySense Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Add missing tailwindcss-animate package
npm install tailwindcss-animate

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p src/app/\(auth\)
mkdir -p src/app/\(dashboard\)
mkdir -p src/app/api
mkdir -p src/components/auth
mkdir -p src/components/dashboard
mkdir -p src/components/map
mkdir -p src/components/reports
mkdir -p src/components/alerts
mkdir -p src/components/analytics
mkdir -p src/components/subscriptions
mkdir -p src/components/ui
mkdir -p src/hooks
mkdir -p src/lib
mkdir -p src/store
mkdir -p src/types
mkdir -p public/animations

echo "✅ Basic setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env.local and fill in your values"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
