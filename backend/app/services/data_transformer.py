"""
Data transformation service - converts TikTok API responses to database models
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List
from ..models import Order, Product


class DataTransformer:
    """Transform TikTok API responses to internal models"""
    
    @staticmethod
    def transform_order(raw_order: Dict) -> Dict:
        """
        Transform TikTok order data to Order model format
        
        TikTok API Response Structure:
        - id: Order ID
        - create_time: Unix timestamp
        - payment: { total_amount, currency, ... }
        - line_items: List of items in order
        - recipient_address: Shipping address
        - tracking_number: Shipment tracking
        
        Args:
            raw_order: Raw order data from TikTok API
        
        Returns:
            Dictionary ready for Order model creation
        """
        # Extract payment info
        payment = raw_order.get("payment", {})
        
        # Get item count from line_items or item_list
        items = raw_order.get("line_items", raw_order.get("item_list", []))
        item_count = len(items)
        
        # Extract shipping info
        shipping_provider = raw_order.get("shipping_provider_name") or raw_order.get("shipping_provider")
        tracking_number = raw_order.get("tracking_number")
        
        # Get status - TikTok uses different status fields
        status = raw_order.get("order_status") or raw_order.get("status", "UNKNOWN")
        
        return {
            "id": raw_order.get("id"),
            "order_number": raw_order.get("order_id") or raw_order.get("id"),
            "status": status,
            "created_time": datetime.fromtimestamp(raw_order.get("create_time", 0)),
            "paid_time": datetime.fromtimestamp(raw_order["paid_time"]) if raw_order.get("paid_time") else None,
            "shipped_time": datetime.fromtimestamp(raw_order["ship_time"]) if raw_order.get("ship_time") else None,
            "delivered_time": datetime.fromtimestamp(raw_order["delivery_time"]) if raw_order.get("delivery_time") else None,
            "total_amount": Decimal(str(payment.get("total_amount", 0))),
            "currency": payment.get("currency", "GBP"),
            "item_count": item_count,
            "customer_id": raw_order.get("buyer_uid") or raw_order.get("buyer_user_id"),
            "shipping_provider": shipping_provider,
            "tracking_number": tracking_number,
            "raw_data": raw_order
        }
    
    @staticmethod
    def transform_product(raw_product: Dict) -> Dict:
        """
        Transform TikTok product data to Product model format
        
        TikTok API Response Structure:
        - id: Product ID
        - title: Product name
        - skus: List of SKU variants with price and inventory
        - main_images: Product images
        - status: Product status
        
        Args:
            raw_product: Raw product data from TikTok API
        
        Returns:
            Dictionary ready for Product model creation
        """
        # Get images - try different field names
        images = raw_product.get("main_images", raw_product.get("images", []))
        if images and isinstance(images, list) and len(images) > 0:
            # Handle both string URLs and dict with 'url' key
            first_image = images[0]
            image_url = first_image if isinstance(first_image, str) else first_image.get("url")
        else:
            image_url = None
        
        # Get SKUs
        skus = raw_product.get("skus", [])
        
        # Get price from first SKU
        if skus and len(skus) > 0:
            first_sku = skus[0]
            price_info = first_sku.get("price", {})
            # Try different price field names
            price_value = (
                price_info.get("tax_exclusive_price") or
                price_info.get("amount") or
                price_info.get("original_price") or
                "0"
            )
            price = Decimal(str(price_value))
            seller_sku = first_sku.get("seller_sku")
        else:
            price = Decimal("0")
            seller_sku = None
        
        # Get stock quantity - sum across all SKUs and warehouses
        stock = 0
        for sku in skus:
            inventory_list = sku.get("inventory", sku.get("stock_infos", []))
            for inv in inventory_list:
                stock += inv.get("quantity", inv.get("available_stock", 0))
        
        # Get product name
        product_name = raw_product.get("title") or raw_product.get("product_name", "Unknown Product")
        
        # Get status - handle different status formats
        status = raw_product.get("status", "UNKNOWN")
        # TikTok might return status in audit object
        if "audit" in raw_product:
            audit_status = raw_product["audit"].get("status")
            if audit_status:
                status = audit_status
        
        return {
            "id": raw_product.get("id") or raw_product.get("product_id"),
            "name": product_name,
            "sku": seller_sku,
            "status": status,
            "price": price,
            "stock_quantity": stock,
            "category": raw_product.get("category_name") or raw_product.get("category", {}).get("name"),
            "brand": raw_product.get("brand", {}).get("name") if isinstance(raw_product.get("brand"), dict) else raw_product.get("brand"),
            "image_url": image_url,
            "lookfantastic_sku": None,  # To be mapped later
            "raw_data": raw_product
        }
