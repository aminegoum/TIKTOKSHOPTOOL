# TikTok Shop Dashboard - Backend

FastAPI backend for TikTok Shop performance tracking.

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Edit .env file with your credentials
nano .env
```

Required environment variables:
- `TIKTOK_APP_KEY` - Your TikTok Shop app key
- `TIKTOK_APP_SECRET` - Your TikTok Shop app secret
- `ENCRYPTION_KEY` - Generated Fernet key for token encryption
- `SECRET_KEY` - Random secret key for sessions

### 3. Run the Server

```bash
# Using the startup script (recommended)
chmod +x run.sh
./run.sh

# Or manually
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## API Endpoints

### Authentication
- `GET /api/auth/authorize-url` - Get TikTok OAuth URL
- `POST /api/auth/callback` - Handle OAuth callback
- `GET /api/auth/status` - Check authentication status

### Data Sync
- `POST /api/sync/trigger` - Manually trigger data sync
- `GET /api/sync/status` - Get sync status

### KPIs
- `GET /api/kpis/summary` - Get summary KPIs
- `GET /api/kpis/trends` - Get daily trends
- `GET /api/kpis/top-products` - Get top products

## Database

The application uses SQLite for local storage. The database file (`tiktok_shop.db`) will be created automatically on first run.

### Tables
- `oauth_tokens` - Encrypted TikTok Shop credentials
- `orders` - Order transactions
- `products` - Product catalog

## Development

### Run Tests
```bash
pytest
```

### Format Code
```bash
black app/
```

### Type Checking
```bash
mypy app/
```

## Troubleshooting

### "No .env file found"
Copy `.env.example` to `.env` and fill in your credentials.

### "Invalid encryption key"
Generate a new key with:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### "TikTok API error"
Check that your app key and secret are correct in the `.env` file.
