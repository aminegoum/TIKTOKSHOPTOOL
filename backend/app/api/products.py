"""
Product and Brand Analytics API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from collections import defaultdict
import json
from ..database import get_db
from ..models import Order

router = APIRouter(prefix="/api/products", tags=["products"])


def extract_brand_from_product_name(product_name: str) -> str:
    """
    Extract brand name from product name
    Common patterns: "Brand Name Product Description"
    """
    if not product_name:
        return "Unknown"
    
    # Common brand names in LookFantastic
    known_brands = [
        "Sol de Janeiro", "Coco & Eve", "brushworks", "The Ordinary",
        "CeraVe", "La Roche-Posay", "Nuxe", "Medik8", "ESPA",
        "Elemis", "Dermalogica", "Kiehl's", "Clinique", "Estée Lauder",
        "MAC", "NARS", "Urban Decay", "Benefit", "Too Faced",
        "Anastasia Beverly Hills", "Huda Beauty", "Charlotte Tilbury",
        "Fenty Beauty", "Rare Beauty", "Olaplex", "K18", "Living Proof",
        "Moroccanoil", "Ouai", "Christophe Robin", "Bumble and bumble",
        "ghd", "Dyson", "Foreo", "NuFACE", "PMD", "Dr. Dennis Gross"
    ]
    
    # Check for known brands
    product_lower = product_name.lower()
    for brand in known_brands:
        if brand.lower() in product_lower:
            return brand
    
    # Fallback: take first word/phrase before common separators
    separators = [' - ', ' | ', ' (', ' /', ' with ']
    for sep in separators:
        if sep in product_name:
            return product_name.split(sep)[0].strip()
    
    # Take first 2-3 words as brand
    words = product_name.split()
    if len(words) >= 2:
        return ' '.join(words[:2])
    
    return words[0] if words else "Unknown"


@router.get("/analytics")
async def get_product_analytics(db: Session = Depends(get_db)):
    """
    Get product and brand analytics from orders
    
    Returns:
        Product performance metrics, brand breakdown, top products
    """
    # Get all orders with raw_data
    orders = db.query(Order).filter(Order.raw_data.isnot(None)).all()
    
    # Analytics data structures
    brand_stats = defaultdict(lambda: {"orders": 0, "revenue": 0, "units": 0, "products": set()})
    product_stats = defaultdict(lambda: {"orders": 0, "revenue": 0, "units": 0, "brand": ""})
    payment_methods = defaultdict(int)
    
    total_products_sold = 0
    
    for order in orders:
        raw_data = order.raw_data or {}
        line_items = raw_data.get('line_items', [])
        payment_method = raw_data.get('payment_method_name', 'Unknown')
        
        payment_methods[payment_method] += 1
        
        for item in line_items:
            product_name = item.get('product_name', 'Unknown Product')
            product_id = item.get('product_id', 'unknown')
            sale_price = float(item.get('sale_price', 0))
            
            # Extract brand
            brand = extract_brand_from_product_name(product_name)
            
            # Update brand stats
            brand_stats[brand]["orders"] += 1
            brand_stats[brand]["revenue"] += sale_price
            brand_stats[brand]["units"] += 1
            brand_stats[brand]["products"].add(product_name)
            
            # Update product stats
            product_key = f"{product_id}:{product_name}"
            product_stats[product_key]["orders"] += 1
            product_stats[product_key]["revenue"] += sale_price
            product_stats[product_key]["units"] += 1
            product_stats[product_key]["brand"] = brand
            
            total_products_sold += 1
    
    # Format brand stats
    brands = []
    for brand, stats in brand_stats.items():
        brands.append({
            "brand": brand,
            "orders": stats["orders"],
            "revenue": round(stats["revenue"], 2),
            "units": stats["units"],
            "unique_products": len(stats["products"]),
            "avg_order_value": round(stats["revenue"] / stats["orders"], 2) if stats["orders"] > 0 else 0
        })
    
    # Sort by revenue
    brands.sort(key=lambda x: x["revenue"], reverse=True)
    
    # Format product stats
    products = []
    for product_key, stats in product_stats.items():
        product_id, product_name = product_key.split(':', 1)
        products.append({
            "product_id": product_id,
            "product_name": product_name,
            "brand": stats["brand"],
            "orders": stats["orders"],
            "revenue": round(stats["revenue"], 2),
            "units": stats["units"],
            "avg_price": round(stats["revenue"] / stats["units"], 2) if stats["units"] > 0 else 0
        })
    
    # Sort by revenue
    products.sort(key=lambda x: x["revenue"], reverse=True)
    
    # Format payment methods
    payment_breakdown = [
        {"method": method, "count": count}
        for method, count in sorted(payment_methods.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return {
        "summary": {
            "total_brands": len(brands),
            "total_unique_products": len(products),
            "total_units_sold": total_products_sold
        },
        "top_brands": brands[:20],  # Top 20 brands
        "top_products": products[:50],  # Top 50 products
        "payment_methods": payment_breakdown,
        "all_brands": brands  # Full list for filtering
    }


@router.get("/brands")
async def get_brands_list(db: Session = Depends(get_db)):
    """
    Get list of all brands for filtering
    
    Returns:
        List of unique brands
    """
    orders = db.query(Order).filter(Order.raw_data.isnot(None)).limit(1000).all()
    
    brands = set()
    for order in orders:
        raw_data = order.raw_data or {}
        line_items = raw_data.get('line_items', [])
        
        for item in line_items:
            product_name = item.get('product_name', '')
            brand = extract_brand_from_product_name(product_name)
            brands.add(brand)
    
    return {
        "brands": sorted(list(brands))
    }
