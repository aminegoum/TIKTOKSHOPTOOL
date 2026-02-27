#!/bin/bash

# TikTok Shop Dashboard - Frontend Startup Script

echo "🚀 Starting TikTok Shop Dashboard Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "✅ Starting Vite development server..."
npm run dev
