# TikTok Shop Dashboard - Frontend

React dashboard for TikTok Shop performance tracking.

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### 3. Build for Production

```bash
npm run build
npm run preview
```

## Features

- **Authentication**: Connect to TikTok Shop via OAuth
- **KPI Cards**: View key metrics (GMV, Orders, AOV, Items Sold)
- **Manual Sync**: Trigger data synchronization with buttons
- **Trends Chart**: Visualize daily performance over 30 days
- **Order Status**: Breakdown of completed, pending, and cancelled orders

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Axios** - HTTP client

## Project Structure

```
src/
├── components/
│   ├── KPICard.jsx          # Metric display card
│   ├── SyncButton.jsx       # Manual sync controls
│   └── TrendsChart.jsx      # Line chart for trends
├── services/
│   └── api.js               # API client
├── App.jsx                  # Main application
├── main.jsx                 # Entry point
└── index.css                # Global styles
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`.

Make sure the backend is running before starting the frontend.

## Development

### Hot Reload
Changes to source files will automatically reload the browser.

### Proxy Configuration
API requests are proxied through Vite to avoid CORS issues during development.

## Troubleshooting

### "Cannot connect to backend"
Ensure the FastAPI server is running on port 8000.

### "Authentication failed"
Check that your TikTok Shop credentials are correctly configured in the backend `.env` file.
