"""
Configuration settings for the TikTok Shop Dashboard API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # TikTok API
    tiktok_app_key: str
    tiktok_app_secret: str
    tiktok_shop_cipher: Optional[str] = None
    tiktok_shop_id: Optional[str] = None
    tiktok_access_token: Optional[str] = None  # Optional: use existing token
    tiktok_refresh_token: Optional[str] = None  # Optional: for auto-refresh
    
    # Security
    encryption_key: str
    secret_key: str
    
    # Database
    database_url: str = "sqlite:///./tiktok_shop.db"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # TikTok API URLs
    tiktok_api_base_url: str = "https://open-api.tiktokglobalshop.com"
    tiktok_auth_url: str = "https://services.tiktokshop.com/open/authorize"
    tiktok_token_url: str = "https://auth.tiktok-shops.com/api/token/getAccessToken"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
