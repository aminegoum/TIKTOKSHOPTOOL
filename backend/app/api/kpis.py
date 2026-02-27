"""
KPI and analytics API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from ..database import get_db
from ..services import KPICalculator

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("/summary")
async def get_kpi_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get summary KPIs for a date range
    
    Args:
        start_date: Start date (defaults to 30 days ago)
        end_date: End date (defaults to today)
        db: Database session
    
    Returns:
        Summary KPI metrics
    """
    # Parse dates or use defaults
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = datetime.utcnow()
    
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = end - timedelta(days=30)
    
    # Calculate KPIs
    calculator = KPICalculator()
    kpis = calculator.calculate_summary_kpis(db, start, end)
    
    return kpis


@router.get("/today")
async def get_todays_metrics(db: Session = Depends(get_db)):
    """
    Get today's performance metrics
    
    Matches TikTok Shop Analytics "Today's data" section:
    - GMV
    - Items sold
    - Customers
    - Visitors (requires analytics API)
    
    Args:
        db: Database session
    
    Returns:
        Today's metrics with yesterday comparison
    """
    calculator = KPICalculator()
    metrics = calculator.get_todays_metrics(db)
    
    return metrics


@router.get("/trends")
async def get_kpi_trends(
    days: int = Query(30, description="Number of days to include"),
    db: Session = Depends(get_db)
):
    """
    Get daily KPI trends
    
    Args:
        days: Number of days to include (default 30)
        db: Database session
    
    Returns:
        List of daily KPI data points
    """
    calculator = KPICalculator()
    trends = calculator.calculate_daily_trends(db, days=days)
    
    return {
        "trends": trends,
        "days": days
    }


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(10, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """
    Get top performing products
    
    Args:
        limit: Number of products to return
        db: Database session
    
    Returns:
        List of top products
    """
    calculator = KPICalculator()
    products = calculator.get_top_products(db, limit=limit)
    
    return {
        "products": products,
        "count": len(products)
    }
