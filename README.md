# TikTok Shop Dashboard

A comprehensive dashboard for tracking TikTok Shop performance metrics for LookFantastic.

## 🚀 Quick Start

### Option 1: Double-Click (Easiest)
Simply **double-click** the `Start Dashboard.command` file in Finder.

### Option 2: Terminal
```bash
cd tiktok-shop-dashboard
./start.sh
```

This will:
- ✅ Automatically kill any existing instances
- ✅ Start both backend and frontend in one terminal
- ✅ Open the dashboard at http://localhost:3000

## 🛑 Stopping the Dashboard

Press `Ctrl+C` in the terminal - it will automatically shut down everything.

## 📊 Access Points

- **Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔧 Configuration

All credentials are stored in `backend/.env`:
- TikTok App Key & Secret
- Shop ID & Cipher
- Access & Refresh Tokens

The dashboard uses **App Authorization** mode, so no OAuth flow is needed.

## 📁 Project Structure

```
tiktok-shop-dashboard/
├── Start Dashboard.command  # Double-click to start (macOS)
├── start.sh                 # Startup script
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── .env               # Configuration (credentials)
│   └── requirements.txt   # Python dependencies
└── frontend/               # React frontend
    ├── src/               # Source code
    └── package.json       # Node dependencies
```

## 🔍 Features

- 📊 Real-time KPI tracking
- 📦 Order management
- 🏷️ Product & brand analytics
- 📈 Trend analysis
- 🔄 Automatic data synchronization

## 🐛 Troubleshooting

### Port Already in Use
The startup script automatically kills existing instances. If you still see errors:
```bash
pkill -f "uvicorn app.main:app"
pkill -f "vite"
```

### Backend Not Starting
Check that `.env` file exists in `backend/` directory with all required credentials.

### Frontend Not Loading
Make sure Node.js is installed:
```bash
node --version  # Should be v16 or higher
```

## 📝 Notes

- The dashboard automatically syncs data from TikTok Shop API
- First sync may take several minutes for historical data
- Data is stored in SQLite database (`backend/tiktok_shop.db`)
