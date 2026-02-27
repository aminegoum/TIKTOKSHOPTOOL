"""
KPI calculation service
"""
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Order, Product


class KPICalculator:
    """Calculate business KPIs from order and product data"""
    
    @staticmethod
    def calculate_summary_kpis(db: Session, start_date: datetime, end_date: datetime) -> Dict:
        """
        Calculate summary KPIs for a date range
        
        Matches TikTok Shop Analytics dashboard metrics:
        - GMV (Gross Merchandise Value)
        - Est. Net Revenue
        - Items sold
        - Orders count
        - Average Order Value
        
        Args:
            db: Database session
            start_date: Start of date range
            end_date: End of date range
        
        Returns:
            Dictionary with KPI metrics
        """
        # Query orders in date range
        orders = db.query(Order).filter(
            Order.created_time >= start_date,
            Order.created_time <= end_date
        ).all()
        
        if not orders:
            return {
                "total_orders": 0,
                "total_gmv": 0,
                "estimated_net_revenue": 0,
                "total_items_sold": 0,
                "average_order_value": 0,
                "completed_orders": 0,
                "pending_orders": 0,
                "cancelled_orders": 0,
                "unique_customers": 0
            }
        
        # Calculate metrics
        total_orders = len(orders)
        total_gmv = sum(float(order.total_amount) for order in orders)
        total_items = sum(order.item_count for order in orders)
        avg_order_value = total_gmv / total_orders if total_orders > 0 else 0
        
        # Estimate net revenue (GMV minus estimated 15% TikTok fees)
        # This is an approximation - actual fees vary
        estimated_net_revenue = total_gmv * 0.85
        
        # Count by status
        completed = sum(1 for o in orders if o.status in ["COMPLETED", "DELIVERED"])
        pending = sum(1 for o in orders if o.status in ["PENDING", "AWAITING_SHIPMENT"])
        cancelled = sum(1 for o in orders if o.status == "CANCELLED")
        
        # Count unique customers
        unique_customers = len(set(o.customer_id for o in orders if o.customer_id))
        
        return {
            "total_orders": total_orders,
            "total_gmv": round(total_gmv, 2),
            "estimated_net_revenue": round(estimated_net_revenue, 2),
            "total_items_sold": total_items,
            "average_order_value": round(avg_order_value, 2),
            "completed_orders": completed,
            "pending_orders": pending,
            "cancelled_orders": cancelled,
            "unique_customers": unique_customers,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    
    @staticmethod
    def calculate_daily_trends(db: Session, days: int = 30) -> List[Dict]:
        """
        Calculate daily KPI trends
        
        Provides daily breakdown of:
        - GMV
        - Est. Net Revenue
        - Orders
        - Items sold
        - Unique customers
        
        Args:
            db: Database session
            days: Number of days to include
        
        Returns:
            List of daily KPI dictionaries
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query orders
        orders = db.query(Order).filter(
            Order.created_time >= start_date,
            Order.created_time <= end_date
        ).all()
        
        # Group by date
        daily_data = {}
        for order in orders:
            date_key = order.created_time.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "orders": 0,
                    "gmv": 0,
                    "estimated_net_revenue": 0,
                    "items": 0,
                    "customers": set()
                }
            
            daily_data[date_key]["orders"] += 1
            gmv_amount = float(order.total_amount)
            daily_data[date_key]["gmv"] += gmv_amount
            daily_data[date_key]["estimated_net_revenue"] += gmv_amount * 0.85
            daily_data[date_key]["items"] += order.item_count
            if order.customer_id:
                daily_data[date_key]["customers"].add(order.customer_id)
        
        # Convert to sorted list and format
        trends = []
        for date_key in sorted(daily_data.keys()):
            data = daily_data[date_key]
            trends.append({
                "date": data["date"],
                "orders": data["orders"],
                "gmv": round(data["gmv"], 2),
                "estimated_net_revenue": round(data["estimated_net_revenue"], 2),
                "items": data["items"],
                "unique_customers": len(data["customers"])
            })
        
        return trends
    
    @staticmethod
    def get_todays_metrics(db: Session) -> Dict:
        """
        Get today's performance metrics
        
        Matches the "Today's data" section in TikTok dashboard:
        - GMV
        - Items sold
        - Visitors (not available from orders - would need analytics API)
        - Customers
        
        Args:
            db: Database session
        
        Returns:
            Today's metrics
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.utcnow()
        
        # Get today's orders
        today_orders = db.query(Order).filter(
            Order.created_time >= today_start,
            Order.created_time <= today_end
        ).all()
        
        # Get yesterday's orders for comparison
        yesterday_start = today_start - timedelta(days=1)
        yesterday_orders = db.query(Order).filter(
            Order.created_time >= yesterday_start,
            Order.created_time < today_start
        ).all()
        
        # Calculate today's metrics
        today_gmv = sum(float(o.total_amount) for o in today_orders)
        today_items = sum(o.item_count for o in today_orders)
        today_customers = len(set(o.customer_id for o in today_orders if o.customer_id))
        
        # Calculate yesterday's metrics for comparison
        yesterday_gmv = sum(float(o.total_amount) for o in yesterday_orders)
        yesterday_items = sum(o.item_count for o in yesterday_orders)
        yesterday_customers = len(set(o.customer_id for o in yesterday_orders if o.customer_id))
        
        return {
            "gmv": round(today_gmv, 2),
            "gmv_yesterday": round(yesterday_gmv, 2),
            "items_sold": today_items,
            "items_sold_yesterday": yesterday_items,
            "customers": today_customers,
            "customers_yesterday": yesterday_customers,
            "visitors": 0,  # Would need analytics API
            "visitors_yesterday": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_top_products(db: Session, limit: int = 10, start_date: datetime = None) -> List[Dict]:
        """
        Get top performing products
        
        Args:
            db: Database session
            limit: Number of products to return
            start_date: Optional start date filter
        
        Returns:
            List of top products with sales data
        """
        # For MVP, return all products sorted by price
        # In production, this would join with order_items table
        products = db.query(Product).filter(
            Product.status == "ACTIVE"
        ).order_by(Product.price.desc()).limit(limit).all()
        
        return [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "price": float(p.price),
                "stock": p.stock_quantity,
                "image_url": p.image_url
            }
            for p in products
        ]
