"""
Token encryption and management service
"""
from __future__ import annotations
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import OAuthToken
from ..config import settings


class TokenManager:
    """Manage OAuth token encryption and storage"""
    
    def __init__(self):
        self.cipher = Fernet(settings.encryption_key.encode())
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token string"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token string"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def save_tokens(
        self,
        db: Session,
        access_token: str,
        refresh_token: str,
        expires_in: int,
        shop_id: str,
        shop_name: str = None
    ) -> OAuthToken:
        """
        Save encrypted tokens to database
        
        Args:
            db: Database session
            access_token: Access token from TikTok
            refresh_token: Refresh token from TikTok
            expires_in: Token expiry time in seconds
            shop_id: TikTok shop ID
            shop_name: Shop name (optional)
        
        Returns:
            OAuthToken: Saved token record
        """
        # Encrypt tokens
        encrypted_access = self.encrypt_token(access_token)
        encrypted_refresh = self.encrypt_token(refresh_token)
        
        # Calculate expiry time
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Check if token already exists for this shop
        existing_token = db.query(OAuthToken).filter(
            OAuthToken.shop_id == shop_id
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = encrypted_access
            existing_token.refresh_token = encrypted_refresh
            existing_token.expires_at = expires_at
            existing_token.shop_name = shop_name
            existing_token.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_token)
            return existing_token
        else:
            # Create new token
            new_token = OAuthToken(
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=expires_at,
                shop_id=shop_id,
                shop_name=shop_name
            )
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            return new_token
    
    def get_valid_token(self, db: Session, shop_id: str = None) -> Optional[Tuple[str, str]]:
        """
        Get valid access token (decrypt and check expiry)
        
        Args:
            db: Database session
            shop_id: Shop ID (optional, uses first token if not provided)
        
        Returns:
            Tuple of (access_token, shop_id) or None if no valid token
        """
        query = db.query(OAuthToken)
        
        if shop_id:
            query = query.filter(OAuthToken.shop_id == shop_id)
        
        token_record = query.first()
        
        if not token_record:
            return None
        
        # Check if token is expired (with 5 minute buffer)
        if token_record.expires_at <= datetime.utcnow() + timedelta(minutes=5):
            return None
        
        # Decrypt and return
        access_token = self.decrypt_token(token_record.access_token)
        return (access_token, token_record.shop_id)
    
    def get_refresh_token(self, db: Session, shop_id: str) -> Optional[str]:
        """Get decrypted refresh token"""
        token_record = db.query(OAuthToken).filter(
            OAuthToken.shop_id == shop_id
        ).first()
        
        if not token_record:
            return None
        
        return self.decrypt_token(token_record.refresh_token)


# Global instance
token_manager = TokenManager()
