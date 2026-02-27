"""
OAuth Token model for storing TikTok Shop credentials
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base


class OAuthToken(Base):
    """Store encrypted TikTok Shop OAuth tokens"""
    
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)  # Encrypted
    refresh_token = Column(String, nullable=False)  # Encrypted
    expires_at = Column(DateTime, nullable=False)
    shop_id = Column(String, nullable=False)
    shop_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<OAuthToken(shop_id='{self.shop_id}', expires_at='{self.expires_at}')>"
