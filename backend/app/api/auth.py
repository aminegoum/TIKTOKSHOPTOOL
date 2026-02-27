"""
Authentication API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..services import TikTokShopClient, token_manager
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class AuthCallbackRequest(BaseModel):
    """Request model for OAuth callback"""
    code: str
    state: str = None


class AuthStatusResponse(BaseModel):
    """Response model for auth status"""
    authenticated: bool
    shop_id: Optional[str] = None
    shop_name: Optional[str] = None
    expires_at: Optional[str] = None


@router.get("/authorize-url")
async def get_authorize_url():
    """
    Get TikTok OAuth authorization URL
    
    Returns:
        Authorization URL to redirect user to
    """
    # Use the registered callback URL
    redirect_uri = "https://localhost:3000/tiktok/callback"
    auth_url = TikTokShopClient.get_authorization_url(
        redirect_uri=redirect_uri,
        state="tiktok_shop_auth"
    )
    
    return {
        "authorization_url": auth_url,
        "state": "tiktok_shop_auth",
        "redirect_uri": redirect_uri
    }


@router.post("/callback")
async def handle_callback(
    request: AuthCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback and exchange code for tokens
    
    Args:
        request: Callback request with authorization code
        db: Database session
    
    Returns:
        Success message with shop info
    """
    try:
        # Exchange code for tokens
        token_response = await TikTokShopClient.exchange_code_for_token(request.code)
        
        # Check if successful
        if token_response.get("code") != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Token exchange failed: {token_response.get('message')}"
            )
        
        data = token_response.get("data", {})
        
        # Save tokens to database
        token_manager.save_tokens(
            db=db,
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expires_in=data.get("access_token_expire_in", 3600),
            shop_id=data.get("seller_base_info", {}).get("shop_id", "unknown"),
            shop_name=data.get("seller_base_info", {}).get("shop_name")
        )
        
        return {
            "success": True,
            "message": "Successfully connected to TikTok Shop",
            "shop_id": data.get("seller_base_info", {}).get("shop_id"),
            "shop_name": data.get("seller_base_info", {}).get("shop_name")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(db: Session = Depends(get_db)):
    """
    Check if user is authenticated with TikTok Shop
    
    For App Authorization (not OAuth), we check if app credentials are configured
    
    Returns:
        Authentication status and shop info
    """
    # Check if using App Authorization (app_key and app_secret configured)
    if settings.tiktok_app_key and settings.tiktok_app_secret:
        # App Authorization mode - no OAuth tokens needed
        # The app is already authorized via the service authorization link
        return AuthStatusResponse(
            authenticated=True,
            shop_id=settings.tiktok_shop_id or "configured",
            shop_name="LookFantastic (App Authorized)",
            expires_at=None  # App authorization doesn't expire
        )
    
    # Otherwise check for OAuth tokens
    token_info = token_manager.get_valid_token(db)
    
    if not token_info:
        return AuthStatusResponse(authenticated=False)
    
    access_token, shop_id = token_info
    
    # Get token record for additional info
    from ..models import OAuthToken
    token_record = db.query(OAuthToken).filter(
        OAuthToken.shop_id == shop_id
    ).first()
    
    return AuthStatusResponse(
        authenticated=True,
        shop_id=shop_id,
        shop_name=token_record.shop_name if token_record else None,
        expires_at=token_record.expires_at.isoformat() if token_record else None
    )


@router.post("/skip-oauth")
async def skip_oauth_for_app_auth():
    """
    Endpoint to confirm app authorization mode
    Used when app is already authorized via service link
    """
    if not settings.tiktok_app_key or not settings.tiktok_app_secret:
        raise HTTPException(
            status_code=400,
            detail="App credentials not configured in .env file"
        )
    
    return {
        "success": True,
        "message": "App Authorization mode - OAuth not required",
        "shop_id": settings.tiktok_shop_id or "configured",
        "auth_type": "app_authorization"
    }
