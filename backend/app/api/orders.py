"""
Orders API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models import Order

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("/list")
async def get_orders_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by order ID"),
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of orders
    
    Args:
        page: Page number (starts at 1)
        page_size: Number of items per page (max 100)
        status: Filter by order status
        search: Search by order ID
        brand: Filter by brand name (case-insensitive partial match)
        db: Database session
    
    Returns:
        Paginated orders list with metadata
    """
    # Build query
    query = db.query(Order)
    
    # Apply filters
    if status:
        query = query.filter(Order.status == status)
    
    if search:
        query = query.filter(Order.id.contains(search))
    
    # Get all orders for brand filtering (since brand is extracted from raw_data)
    # We need to filter in Python since brand is not a direct column
    all_orders = query.order_by(desc(Order.created_time)).all()
    
    # Filter by brand if specified
    if brand:
        filtered_orders = []
        brand_lower = brand.lower().strip()
        print(f"\n🔍 Filtering by brand: '{brand_lower}' from {len(all_orders)} total orders")
        
        for order in all_orders:
            raw_data = order.raw_data or {}
            line_items = raw_data.get('line_items', [])
            
            # Check if any product name contains the brand filter
            for item in line_items:
                product_name = item.get('product_name', '').lower()
                if brand_lower in product_name:
                    filtered_orders.append(order)
                    break  # Found a match, no need to check other items in this order
        
        print(f"📊 Result: {len(filtered_orders)} orders match the filter\n")
        all_orders = filtered_orders
    
    # Get total count after filtering
    total_count = len(all_orders)
    
    # Apply pagination
    offset = (page - 1) * page_size
    orders = all_orders[offset:offset + page_size]
    
    # Calculate pagination metadata
    total_pages = (total_count + page_size - 1) // page_size
    
    # Convert to dict
    orders_data = []
    for order in orders:
        # Extract brands from products
        raw_data = order.raw_data or {}
        line_items = raw_data.get('line_items', [])
        brands = set()
        for item in line_items:
            product_name = item.get('product_name', '')
            # Extract brand from product name (first word/phrase)
            if product_name:
                brand = product_name.split()[0] if product_name.split() else 'Unknown'
                brands.add(brand)
        
        orders_data.append({
            "id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "created_time": order.created_time.isoformat() if order.created_time else None,
            "total_amount": float(order.total_amount) if order.total_amount else 0,
            "currency": order.currency,
            "item_count": order.item_count,
            "customer_id": order.customer_id,
            "shipping_provider": order.shipping_provider,
            "tracking_number": order.tracking_number,
            "brands": ', '.join(sorted(brands)) if brands else 'N/A',
            "creator": None  # Placeholder for future creator data
        })
    
    return {
        "orders": orders_data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


@router.get("/stats")
async def get_orders_stats(db: Session = Depends(get_db)):
    """
    Get order statistics
    
    Returns:
        Order statistics and KPIs
    """
    # Get status breakdown
    status_counts = db.query(
        Order.status,
        func.count(Order.id).label('count'),
        func.sum(Order.total_amount).label('total_amount')
    ).group_by(Order.status).all()
    
    # Get total stats
    total_stats = db.query(
        func.count(Order.id).label('total_orders'),
        func.sum(Order.total_amount).label('total_gmv'),
        func.avg(Order.total_amount).label('avg_order_value'),
        func.sum(Order.item_count).label('total_items')
    ).first()
    
    # Format status breakdown
    status_breakdown = {}
    for status, count, amount in status_counts:
        status_breakdown[status] = {
            "count": count,
            "total_amount": float(amount) if amount else 0
        }
    
    return {
        "total_orders": total_stats.total_orders or 0,
        "total_gmv": float(total_stats.total_gmv) if total_stats.total_gmv else 0,
        "avg_order_value": float(total_stats.avg_order_value) if total_stats.avg_order_value else 0,
        "total_items": total_stats.total_items or 0,
        "status_breakdown": status_breakdown
    }


@router.get("/{order_id}")
async def get_order_detail(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific order including line items
    
    Args:
        order_id: TikTok order ID
        db: Database session
    
    Returns:
        Complete order details with products, payment, and shipping
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        return {"error": "Order not found"}
    
    # Extract line items from raw_data
    raw_data = order.raw_data or {}
    line_items = raw_data.get('line_items', [])
    payment = raw_data.get('payment', {})
    recipient = raw_data.get('recipient_address', {})
    
    # Format line items with product details
    products = []
    for item in line_items:
        products.append({
            "product_id": item.get('product_id'),
            "product_name": item.get('product_name'),
            "sku_id": item.get('sku_id'),
            "sku_name": item.get('sku_name'),
            "seller_sku": item.get('seller_sku'),
            "quantity": 1,  # TikTok API doesn't provide quantity directly
            "sale_price": float(item.get('sale_price', 0)),
            "original_price": float(item.get('original_price', 0)),
            "currency": item.get('currency', 'GBP'),
            "sku_image": item.get('sku_image'),
            "platform_discount": float(item.get('platform_discount', 0)),
            "seller_discount": float(item.get('seller_discount', 0))
        })
    
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "created_time": order.created_time.isoformat() if order.created_time else None,
        "paid_time": order.paid_time.isoformat() if order.paid_time else None,
        "shipped_time": order.shipped_time.isoformat() if order.shipped_time else None,
        "delivered_time": order.delivered_time.isoformat() if order.delivered_time else None,
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "currency": order.currency,
        "item_count": order.item_count,
        "customer_id": order.customer_id,
        "shipping_provider": order.shipping_provider,
        "tracking_number": order.tracking_number,
        "products": products,
        "payment_details": {
            "subtotal": float(payment.get('sub_total', 0)),
            "shipping_fee": float(payment.get('shipping_fee', 0)),
            "tax": float(payment.get('tax', 0)),
            "platform_discount": float(payment.get('platform_discount', 0)),
            "seller_discount": float(payment.get('seller_discount', 0)),
            "total": float(payment.get('total_amount', 0))
        },
        "payment_method": raw_data.get('payment_method_name'),
        "shipping_address": {
            "name": recipient.get('first_name'),
            "address": recipient.get('full_address'),
            "postcode": recipient.get('postal_code')
        } if recipient else None
    }
