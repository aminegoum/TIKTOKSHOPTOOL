#!/bin/bash

# TikTok Shop Dashboard - Single Startup Script
# This script starts both backend and frontend in a single terminal

set -euo pipefail

echo "🚀 Starting TikTok Shop Dashboard..."
echo ""

# Store the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

kill_by_pattern() {
    local pattern="$1"
    if pgrep -f "$pattern" >/dev/null 2>&1; then
        pkill -TERM -f "$pattern" 2>/dev/null || true
        sleep 1
        pkill -KILL -f "$pattern" 2>/dev/null || true
    fi
}

kill_port() {
    local port="$1"
    local pids
    pids=$(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs -r kill -TERM 2>/dev/null || true
        sleep 1
        echo "$pids" | xargs -r kill -KILL 2>/dev/null || true
    fi
}

cleanup_existing_instances() {
    echo "🧹 Cleaning up any existing instances..."

    # Kill known backend/frontend processes first
    kill_by_pattern "uvicorn app.main:app"
    kill_by_pattern "python -m uvicorn app.main:app"
    kill_by_pattern "vite"

    # Ensure ports are clear, even if process command line changed
    kill_port 8000
    kill_port 3000

    sleep 1
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down TikTok Shop Dashboard..."
    # Kill all child processes
    pkill -P $$ 2>/dev/null || true

    # Also kill by name/ports to be sure
    kill_by_pattern "uvicorn app.main:app"
    kill_by_pattern "python -m uvicorn app.main:app"
    kill_by_pattern "vite"
    kill_port 8000
    kill_port 3000

    exit 0
}

# Initial cleanup before startup
cleanup_existing_instances

# Set up trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Start backend in background
echo "📡 Starting backend server..."
cd "$SCRIPT_DIR/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and start backend
source venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd "$SCRIPT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Dashboard is starting up!"
echo ""
echo "📊 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
