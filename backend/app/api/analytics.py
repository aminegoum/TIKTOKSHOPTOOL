"""
Analytics API endpoints - Comprehensive TikTok Shop Analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Optional
from ..database import get_db
from ..services import TikTokShopClient, token_manager
from ..config import settings
from ..models.order import Order
from ..models.product import Product
import json
import re

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_access_token(db: Session) -> str:
    """Helper to get access token"""
    access_token = settings.tiktok_access_token
    
    if not access_token:
        token_info = token_manager.get_valid_token(db)
        if token_info:
            access_token, _ = token_info
    
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No access token found. Please add TIKTOK_ACCESS_TOKEN to .env"
        )
    
    return access_token


@router.get("/shop/performance")
async def get_shop_performance(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive shop performance metrics
    
    API: /analytics/202509/shop/performance
    
    Returns detailed metrics including:
    - GMV (Gross Merchandise Value)
    - Orders count
    - Items sold
    - Conversion rates
    - Traffic metrics
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_performance_metrics(
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shop performance: {str(e)}")


# REMOVED: This endpoint doesn't exist in TikTok Shop API
# @router.get("/shop/performance/overview")
# The /analytics/202510/shop/performance/overview endpoint returns 404 from TikTok
# Use /shop/performance instead for performance metrics


@router.get("/shop/performance/{date}/hourly")
async def get_hourly_performance(
    date: str,
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get hourly performance breakdown for a specific date
    
    API: /analytics/202510/shop/performance/{date}/performance_per_hour
    
    Returns hour-by-hour metrics:
    - GMV per hour
    - Orders per hour
    - Items sold per hour
    - Visitors per hour
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_performance_per_hour(
            date=date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hourly performance: {str(e)}")


@router.get("/videos/performance")
async def get_video_performance_list(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    page_size: int = Query(20, description="Number of videos per page"),
    page_token: str = Query(None, description="Page token for pagination"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop Video Performance List
    
    API: /analytics/202509/shop_videos/performance
    
    Returns performance metrics for shoppable videos:
    - GMV from videos
    - Video views
    - Click-through rates
    - Conversion from videos
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_video_performance_list(
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            page_token=page_token,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video performances: {str(e)}")


@router.get("/videos/overview")
async def get_video_performance_overview(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop Video Performance Overview
    
    API: /analytics/202509/shop_videos/overview_performance
    
    Returns overview of video performance
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_video_performance_overview(
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video overview: {str(e)}")


@router.get("/videos/{video_id}/performance")
async def get_video_performance_details(
    video_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop Video Performance Details
    
    API: /analytics/202509/shop_videos/{video_id}/performance
    
    Returns detailed performance for a specific video
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_video_performance_details(
            video_id=video_id,
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video details: {str(e)}")


@router.get("/videos/{video_id}/products/performance")
async def get_video_product_performance(
    video_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    page_size: int = Query(20, description="Number of products per page"),
    page_token: str = Query(None, description="Page token for pagination"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop Video Product Performance List
    
    API: /analytics/202509/shop_videos/{video_id}/products/performance
    
    Returns product performance for a specific video
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_video_product_performance_list(
            video_id=video_id,
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            page_token=page_token,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching video product performance: {str(e)}")


@router.get("/lives/performance")
async def get_live_performance_list(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    page_size: int = Query(20, description="Number of LIVE streams per page"),
    page_token: str = Query(None, description="Page token for pagination"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop LIVE Performance List
    
    API: /analytics/202509/shop_lives/performance
    
    Returns performance metrics for LIVE streams
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_live_performance_list(
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            page_token=page_token,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LIVE performance list: {str(e)}")


@router.get("/lives/overview")
async def get_live_performance_overview(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop LIVE Performance Overview
    
    API: /analytics/202509/shop_lives/overview_performance
    
    Returns overview of LIVE stream performance
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_live_performance_overview(
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LIVE overview: {str(e)}")


@router.get("/lives/{live_id}/performance_per_minutes")
async def get_live_performance_per_minutes(
    live_id: str,
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop LIVE Performance Per Minutes
    
    API: /analytics/202510/shop_lives/{live_id}/performance_per_minutes
    
    Returns minute-by-minute metrics for a LIVE stream:
    - GMV per minute
    - Viewers per minute
    - Peak viewership
    - Sales during LIVE
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_live_performance_per_minutes(
            live_id=live_id,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LIVE performance per minutes: {str(e)}")


@router.get("/lives/{live_id}/products/performance")
async def get_live_products_performance(
    live_id: str,
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop LIVE Products Performance List
    
    API: /analytics/202512/shop/{live_id}/products_performance
    
    Returns product performance for a specific LIVE stream
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_live_products_performance(
            live_id=live_id,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LIVE products performance: {str(e)}")


@router.get("/products/performance")
async def get_product_performance_list(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    page_size: int = Query(20, description="Number of products per page"),
    page_token: str = Query(None, description="Page token for pagination"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop Product Performance List
    
    API: /analytics/202509/shop_products/performance
    
    Returns performance for all products
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_product_performance_list(
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            page_token=page_token,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product performance list: {str(e)}")


@router.get("/products/{product_id}/performance")
async def get_product_performance_detail(
    product_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop Product Performance Detail
    
    API: /analytics/202509/shop_products/{product_id}/performance
    
    Returns metrics for a specific product:
    - Product GMV
    - Units sold
    - Views
    - Conversion rate
    - Traffic sources
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_product_performance(
            product_id=product_id,
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching product performance: {str(e)}")


@router.get("/skus/performance")
async def get_sku_performance_list(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    page_size: int = Query(20, description="Number of SKUs per page"),
    page_token: str = Query(None, description="Page token for pagination"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop SKU Performance List
    
    API: /analytics/202509/shop_skus/performance
    
    Returns performance for all SKUs:
    - SKU GMV
    - Units sold per SKU
    - Stock levels
    - Best performing variants
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_sku_performance_list(
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
            page_token=page_token,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching SKU performances: {str(e)}")


@router.get("/skus/{sku_id}/performance")
async def get_sku_performance_detail(
    sku_id: str,
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get Shop SKU Performance
    
    API: /analytics/202509/shop_skus/{sku_id}/performance
    
    Returns metrics for a specific SKU
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_sku_performance(
            sku_id=sku_id,
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching SKU performance: {str(e)}")


@router.get("/comprehensive")
async def get_comprehensive_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics from all sources
    
    Fetches data from multiple endpoints:
    - Shop performance overview
    - Shop detailed metrics
    - Video performances
    - SKU performances
    
    Returns combined analytics for dashboard display
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    analytics_data = {}
    
    try:
        # Fetch detailed shop metrics
        try:
            metrics = await client.get_shop_performance_metrics(
                start_date=start_date,
                end_date=end_date,
                currency=currency
            )
            analytics_data["shop_metrics"] = metrics
        except Exception as e:
            analytics_data["shop_metrics"] = {"error": str(e)}
        
        # Fetch video performances
        try:
            videos = await client.get_shop_video_performance_list(
                start_date=start_date,
                end_date=end_date,
                page_size=10,
                currency=currency
            )
            analytics_data["video_performances"] = videos
        except Exception as e:
            analytics_data["video_performances"] = {"error": str(e)}
        
        # Fetch SKU performances
        try:
            skus = await client.get_shop_sku_performance_list(
                start_date=start_date,
                end_date=end_date,
                page_size=20,
                currency=currency
            )
            analytics_data["sku_performances"] = skus
        except Exception as e:
            analytics_data["sku_performances"] = {"error": str(e)}
        
        return {
            "success": True,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "currency": currency,
            "data": analytics_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching comprehensive analytics: {str(e)}")


@router.get("/shop/trends")
async def get_shop_trends(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    granularity: str = Query("daily", description="Time granularity (daily, weekly, monthly)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get shop performance trends over time
    
    API: /api/shop/202309/analytics/trends
    
    Returns trend data with time series metrics
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_shop_trends(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shop trends: {str(e)}")


@router.get("/orders/statistics")
async def get_order_statistics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    status: str = Query(None, description="Optional order status filter"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated order statistics and metrics
    
    API: /api/order/202309/analytics/statistics
    
    Returns order statistics including counts and revenue
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_order_statistics(
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order statistics: {str(e)}")


@router.get("/orders/trends")
async def get_order_trends(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    granularity: str = Query("daily", description="Time granularity (hourly, daily, weekly)"),
    db: Session = Depends(get_db)
):
    """
    Get order trends over time
    
    API: /api/order/202309/analytics/trends
    
    Returns order trend data with time series
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_order_trends(
            start_date=start_date,
            end_date=end_date,
            granularity=granularity
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching order trends: {str(e)}")


@router.get("/traffic/overview")
async def get_traffic_overview(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get traffic and visitor metrics for the shop
    
    API: /api/shop/202309/analytics/traffic
    
    Returns traffic metrics including visitors and page views
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_traffic_overview(
            start_date=start_date,
            end_date=end_date
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching traffic overview: {str(e)}")


@router.get("/traffic/sources")
async def get_traffic_sources(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get breakdown of traffic by source
    
    API: /api/shop/202309/analytics/traffic_sources
    
    Returns traffic source breakdown
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_traffic_sources(
            start_date=start_date,
            end_date=end_date
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching traffic sources: {str(e)}")


@router.get("/finance/revenue")
async def get_revenue_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    currency: str = Query("LOCAL", description="Currency code (LOCAL or USD)"),
    db: Session = Depends(get_db)
):
    """
    Get detailed revenue breakdown and financial metrics
    
    API: /api/finance/202309/analytics/revenue
    
    Returns revenue breakdown including gross, net, refunds, fees
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_revenue_report(
            start_date=start_date,
            end_date=end_date,
            currency=currency
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching revenue report: {str(e)}")


@router.get("/finance/settlements")
async def get_settlement_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    status: str = Query(None, description="Settlement status (pending, completed, failed)"),
    db: Session = Depends(get_db)
):
    """
    Get settlement and payout information
    
    API: /api/finance/202309/analytics/settlements
    
    Returns settlement data with payout information
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_settlement_report(
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching settlement report: {str(e)}")


@router.get("/products/top")
async def get_top_products(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    metric: str = Query("sales", description="Metric to sort by (sales, revenue, views, conversion_rate)"),
    limit: int = Query(10, description="Number of products to return (max 50)"),
    db: Session = Depends(get_db)
):
    """
    Get top performing products by various metrics
    
    API: /api/product/202309/analytics/top_products
    
    Returns top products ranked by specified metric
    """
    access_token = get_access_token(db)
    client = TikTokShopClient(access_token=access_token)
    
    try:
        response = await client.get_top_products(
            start_date=start_date,
            end_date=end_date,
            metric=metric,
            limit=limit
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top products: {str(e)}")


def extract_brand_from_product_name(product_name: str) -> str:
    """
    Extract brand name from product name
    Common patterns: "Brand Name Product Description"
    """
    if not product_name:
        return "Unknown"
    
    # Common brand names in LookFantastic/beauty products
    known_brands = [
        "Sol de Janeiro", "Coco & Eve", "brushworks", "The Ordinary",
        "CeraVe", "La Roche-Posay", "Nuxe", "Medik8", "ESPA",
        "Elemis", "Dermalogica", "Kiehl's", "Clinique", "Estée Lauder",
        "MAC", "NARS", "Urban Decay", "Benefit", "Too Faced",
        "Anastasia Beverly Hills", "Huda Beauty", "Charlotte Tilbury",
        "Fenty Beauty", "Rare Beauty", "Olaplex", "K18", "Living Proof",
        "Moroccanoil", "Ouai", "Christophe Robin", "Bumble and bumble",
        "ghd", "Dyson", "Foreo", "NuFACE", "PMD", "Dr. Dennis Gross",
        "By Terry", "Hourglass", "Natasha Denona", "Pat McGrath Labs",
        "Drunk Elephant", "Sunday Riley", "Tatcha", "Fresh", "Glow Recipe",
        "The INKEY List", "Paula's Choice", "Pixi", "REN", "Origins"
    ]
    
    # Check for known brands (case-insensitive)
    product_lower = product_name.lower()
    for brand in known_brands:
        if brand.lower() in product_lower:
            return brand
    
    # Fallback: split by common separators
    separators = [' - ', ' | ', ' (', ' /', ' with ']
    for sep in separators:
        if sep in product_name:
            return product_name.split(sep)[0].strip()
    
    # Take first 2-3 words as brand (handles multi-word brands)
    words = product_name.split()
    if len(words) >= 3:
        # Check if first 3 words might be a brand
        potential_brand = ' '.join(words[:3])
        if any(char.isupper() for char in potential_brand):
            return potential_brand
    if len(words) >= 2:
        return ' '.join(words[:2])
    
    return words[0] if words else "Unknown"


@router.get("/brands/performance")
async def get_brand_performance(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get brand performance analytics from local database
    
    Analyzes orders and products to provide:
    - GMV per brand
    - Order count per brand
    - Items sold per brand
    - Average order value per brand
    - Top performing brands
    """
    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        end = end.replace(hour=23, minute=59, second=59)
        
        # Get all orders in date range
        orders = db.query(Order).filter(
            and_(
                Order.created_time >= start,
                Order.created_time <= end
            )
        ).all()
        
        # Aggregate by brand
        brand_stats = {}
        
        for order in orders:
            # Extract products from raw_data
            if order.raw_data and 'line_items' in order.raw_data:
                for item in order.raw_data['line_items']:
                    product_name = item.get('product_name', '')
                    brand = extract_brand_from_product_name(product_name)
                    
                    if brand not in brand_stats:
                        brand_stats[brand] = {
                            'brand': brand,
                            'gmv': 0,
                            'orders': 0,
                            'items_sold': 0,
                            'order_ids': set()
                        }
                    
                    # Add item value
                    item_price = float(item.get('sale_price', 0))
                    quantity = int(item.get('quantity', 1))
                    
                    brand_stats[brand]['gmv'] += item_price * quantity
                    brand_stats[brand]['items_sold'] += quantity
                    
                    # Count unique orders per brand
                    if order.id not in brand_stats[brand]['order_ids']:
                        brand_stats[brand]['order_ids'].add(order.id)
                        brand_stats[brand]['orders'] += 1
        
        # Convert to list and calculate averages
        brands = []
        for brand, stats in brand_stats.items():
            brands.append({
                'brand': brand,
                'gmv': round(stats['gmv'], 2),
                'orders': stats['orders'],
                'items_sold': stats['items_sold'],
                'avg_order_value': round(stats['gmv'] / stats['orders'], 2) if stats['orders'] > 0 else 0
            })
        
        # Sort by GMV descending
        brands.sort(key=lambda x: x['gmv'], reverse=True)
        
        # Calculate totals
        total_gmv = sum(b['gmv'] for b in brands)
        total_orders = sum(b['orders'] for b in brands)
        total_items = sum(b['items_sold'] for b in brands)
        
        return {
            "success": True,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_brands": len(brands),
                "total_gmv": round(total_gmv, 2),
                "total_orders": total_orders,
                "total_items_sold": total_items
            },
            "brands": brands
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching brand performance: {str(e)}")


@router.get("/local/summary")
async def get_local_analytics_summary(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get analytics summary from local database
    
    Provides comprehensive metrics from synced data:
    - Total GMV, orders, items
    - Daily breakdown
    - Status distribution
    - Top products
    """
    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        end = end.replace(hour=23, minute=59, second=59)
        
        # Get orders in date range
        orders = db.query(Order).filter(
            and_(
                Order.created_time >= start,
                Order.created_time <= end
            )
        ).all()
        
        # Calculate metrics
        total_gmv = sum(float(order.total_amount or 0) for order in orders)
        total_orders = len(orders)
        total_items = sum(int(order.item_count or 0) for order in orders)
        
        # Status distribution
        status_counts = {}
        for order in orders:
            status = order.status or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Daily breakdown
        daily_stats = {}
        for order in orders:
            if order.created_time:
                date_key = order.created_time.strftime("%Y-%m-%d")
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        'date': date_key,
                        'gmv': 0,
                        'orders': 0,
                        'items': 0
                    }
                daily_stats[date_key]['gmv'] += float(order.total_amount or 0)
                daily_stats[date_key]['orders'] += 1
                daily_stats[date_key]['items'] += int(order.item_count or 0)
        
        # Convert to sorted list
        daily_breakdown = sorted(daily_stats.values(), key=lambda x: x['date'])
        
        # Round GMV values
        for day in daily_breakdown:
            day['gmv'] = round(day['gmv'], 2)
        
        return {
            "success": True,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_gmv": round(total_gmv, 2),
                "total_orders": total_orders,
                "total_items": total_items,
                "avg_order_value": round(total_gmv / total_orders, 2) if total_orders > 0 else 0
            },
            "status_distribution": status_counts,
            "daily_breakdown": daily_breakdown
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching local analytics: {str(e)}")
