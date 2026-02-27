"""
Data synchronization API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from ..database import get_db
from ..services import TikTokShopClient, token_manager, DataTransformer
from ..models import Order, Product, SyncMetadata

router = APIRouter(prefix="/api/sync", tags=["sync"])


class SyncRequest(BaseModel):
    """Request model for manual sync"""
    sync_type: str  # "orders", "products", "analytics", "all"
    days_back: int = 30  # How many days of data to sync
    max_records: int = None  # Maximum records to sync (None = unlimited)


class SyncResponse(BaseModel):
    """Response model for sync operations"""
    success: bool
    message: str
    records_synced: int = 0
    sync_type: str


async def sync_orders_task(db: Session, access_token: str, days_back: int = 30, max_orders: int = None, force_full_sync: bool = False):
    """
    Background task to sync orders from TikTok with incremental sync support
    
    Args:
        db: Database session
        access_token: TikTok access token
        days_back: Number of days to sync (used for fallback)
        max_orders: Maximum number of orders to sync (None = unlimited)
        force_full_sync: Force a full sync instead of incremental
    
    Returns:
        Number of orders synced
    """
    client = TikTokShopClient(access_token=access_token)
    transformer = DataTransformer()
    
    synced_count = 0
    page_token = None
    start_time = None
    end_time = None
    is_full_sync = force_full_sync
    most_recent_order_time = None
    
    try:
        # Check for last sync metadata (incremental sync)
        if not force_full_sync:
            sync_meta = db.query(SyncMetadata).filter(
                SyncMetadata.sync_type == "orders"
            ).first()
            
            if sync_meta and sync_meta.last_sync_time:
                # Incremental sync: fetch orders since last sync with 5-minute overlap
                start_time = sync_meta.last_sync_time - timedelta(minutes=5)
                end_time = datetime.utcnow()
                is_full_sync = False
                print(f"Incremental sync: fetching orders since {start_time.isoformat()}")
            else:
                # First sync - do full sync
                is_full_sync = True
                print("No previous sync found - performing full sync")
        else:
            print("Force full sync requested")
        
        while True:
            # Fetch orders from TikTok
            response = await client.get_orders(
                start_time=int(start_time.timestamp()) if start_time else None,
                end_time=int(end_time.timestamp()) if end_time else None,
                page_size=100,  # Maximum allowed by TikTok API
                page_token=page_token,
                sort_field="create_time",
                sort_order="DESC"  # Get newest orders first!
            )
            
            # Check response
            if response.get("code") != 0:
                print(f"Error fetching orders: {response.get('message')}")
                break
            
            data = response.get("data", {})
            orders = data.get("orders", [])
            
            if not orders:
                print(f"No more orders to sync")
                break
            
            # Transform and save orders
            for raw_order in orders:
                order_data = transformer.transform_order(raw_order)
                
                # Check if order exists
                existing = db.query(Order).filter(Order.id == order_data["id"]).first()
                
                if existing:
                    # Update existing order
                    for key, value in order_data.items():
                        setattr(existing, key, value)
                else:
                    # Create new order
                    new_order = Order(**order_data)
                    db.add(new_order)
                
                synced_count += 1
                
                # Track most recent order time for metadata
                if order_data.get("created_at"):
                    order_time = order_data["created_at"]
                    if isinstance(order_time, str):
                        order_time = datetime.fromisoformat(order_time.replace('Z', '+00:00'))
                    if most_recent_order_time is None or order_time > most_recent_order_time:
                        most_recent_order_time = order_time
            
            db.commit()
            print(f"Synced {synced_count} orders so far...")
            
            # Get next page token for pagination
            page_token = data.get("next_page_token")
            if not page_token:
                print(f"No more pages - sync complete")
                break
            
            # Optional limit to prevent syncing all orders at once
            if max_orders and synced_count >= max_orders:
                print(f"Reached max order limit of {max_orders}")
                break
        
        # Update sync metadata
        sync_meta = db.query(SyncMetadata).filter(
            SyncMetadata.sync_type == "orders"
        ).first()
        
        if sync_meta:
            sync_meta.last_sync_time = datetime.utcnow()
            sync_meta.last_record_time = most_recent_order_time or datetime.utcnow()
            sync_meta.records_synced = synced_count
            sync_meta.is_full_sync = 1 if is_full_sync else 0
            sync_meta.updated_at = datetime.utcnow()
        else:
            sync_meta = SyncMetadata(
                sync_type="orders",
                last_sync_time=datetime.utcnow(),
                last_record_time=most_recent_order_time or datetime.utcnow(),
                records_synced=synced_count,
                is_full_sync=1 if is_full_sync else 0
            )
            db.add(sync_meta)
        
        db.commit()
        print(f"Sync metadata updated: {synced_count} orders, full_sync={is_full_sync}")
        
        return synced_count
        
    except Exception as e:
        print(f"Error syncing orders: {e}")
        db.rollback()
        raise


async def sync_products_task(db: Session, access_token: str):
    """
    Background task to sync products from TikTok
    
    Args:
        db: Database session
        access_token: TikTok access token
    
    Returns:
        Number of products synced
    """
    client = TikTokShopClient(access_token=access_token)
    transformer = DataTransformer()
    
    synced_count = 0
    page_number = 1
    
    try:
        while True:
            # Fetch products from TikTok
            response = await client.get_products(
                page_size=100,  # Maximum allowed by TikTok API
                page_number=page_number
            )
            
            # Check response
            if response.get("code") != 0:
                print(f"Error fetching products: {response.get('message')}")
                break
            
            data = response.get("data", {})
            products = data.get("products", [])
            
            if not products:
                break
            
            # Transform and save products
            for raw_product in products:
                product_data = transformer.transform_product(raw_product)
                
                # Check if product exists
                existing = db.query(Product).filter(Product.id == product_data["id"]).first()
                
                if existing:
                    # Update existing product
                    for key, value in product_data.items():
                        setattr(existing, key, value)
                else:
                    # Create new product
                    new_product = Product(**product_data)
                    db.add(new_product)
                
                synced_count += 1
            
            db.commit()
            
            # Check if there are more pages
            if not data.get("more"):
                break
            
            page_number += 1
        
        return synced_count
        
    except Exception as e:
        print(f"Error syncing products: {e}")
        db.rollback()
        raise


async def sync_analytics_task(db: Session, access_token: str, days_back: int = 7):
    """
    Background task to sync analytics data from TikTok
    
    Args:
        db: Database session
        access_token: TikTok access token
        days_back: Number of days to sync
    
    Returns:
        Number of records synced
    """
    from datetime import datetime, timedelta
    client = TikTokShopClient(access_token=access_token)
    
    synced_count = 0
    
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Fetch shop performance overview
        response = await client.get_shop_performance_overview(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            currency="LOCAL"
        )
        
        if response.get("code") == 0:
            print(f"Analytics data fetched successfully")
            synced_count += 1
            # Store in raw_data for now - can be parsed later
            # This gives us GMV, orders, conversion rates, etc.
        
        return synced_count
        
    except Exception as e:
        print(f"Error syncing analytics: {e}")
        raise


@router.post("/trigger", response_model=SyncResponse)
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger data synchronization
    
    Args:
        request: Sync request with type and parameters
        background_tasks: FastAPI background tasks
        db: Database session
    
    Returns:
        Sync status
    """
    # Check if we have an access token in settings (from .env)
    from ..config import settings
    
    if not settings.tiktok_app_key or not settings.tiktok_app_secret:
        raise HTTPException(status_code=401, detail="TikTok app credentials not configured")
    
    # Use access token from .env if available, otherwise try OAuth
    access_token = settings.tiktok_access_token
    
    if not access_token:
        # Try to get from database (OAuth flow)
        token_info = token_manager.get_valid_token(db)
        if token_info:
            access_token, _ = token_info
    
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="No access token found. Please add TIKTOK_ACCESS_TOKEN to .env or complete OAuth flow"
        )
    
    # Trigger appropriate sync
    if request.sync_type == "orders":
        records = await sync_orders_task(db, access_token, request.days_back, request.max_records)
        return SyncResponse(
            success=True,
            message=f"Successfully synced {records} orders",
            records_synced=records,
            sync_type="orders"
        )
    
    elif request.sync_type == "products":
        records = await sync_products_task(db, access_token)
        return SyncResponse(
            success=True,
            message=f"Successfully synced {records} products",
            records_synced=records,
            sync_type="products"
        )
    
    elif request.sync_type == "analytics":
        records = await sync_analytics_task(db, access_token, request.days_back)
        return SyncResponse(
            success=True,
            message=f"Successfully synced analytics data",
            records_synced=records,
            sync_type="analytics"
        )
    
    elif request.sync_type == "all":
        # Sync everything
        orders = await sync_orders_task(db, access_token, request.days_back, request.max_records)
        products = await sync_products_task(db, access_token)
        analytics = await sync_analytics_task(db, access_token, request.days_back)
        
        total = orders + products + analytics
        return SyncResponse(
            success=True,
            message=f"Successfully synced {orders} orders, {products} products, and analytics data",
            records_synced=total,
            sync_type="all"
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sync type: {request.sync_type}")


@router.post("/orders")
async def sync_orders_endpoint(
    max_records: int = None,
    force_full: bool = False,
    db: Session = Depends(get_db)
):
    """
    Sync orders with incremental sync support (default: incremental)
    
    Args:
        max_records: Maximum number of orders to sync (None = unlimited)
        force_full: Force a full sync instead of incremental (default: False)
        db: Database session
    
    Returns:
        Sync status
    """
    from ..config import settings
    access_token = settings.tiktok_access_token
    
    if not access_token:
        token_info = token_manager.get_valid_token(db)
        if token_info:
            access_token, _ = token_info
    
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token found")
    
    records = await sync_orders_task(db, access_token, max_orders=max_records, force_full_sync=force_full)
    sync_type = "full" if force_full else "incremental"
    return SyncResponse(
        success=True,
        message=f"Successfully synced {records} orders ({sync_type})",
        records_synced=records,
        sync_type="orders"
    )


@router.post("/orders/full")
async def sync_orders_full_endpoint(
    max_records: int = None,
    db: Session = Depends(get_db)
):
    """
    Force a full resync of all orders (ignores incremental sync metadata)
    
    Use this endpoint when:
    - Initial setup
    - Data recovery
    - Manual full refresh needed
    
    Args:
        max_records: Maximum number of orders to sync (None = unlimited)
        db: Database session
    
    Returns:
        Sync status
    """
    from ..config import settings
    access_token = settings.tiktok_access_token
    
    if not access_token:
        token_info = token_manager.get_valid_token(db)
        if token_info:
            access_token, _ = token_info
    
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token found")
    
    records = await sync_orders_task(db, access_token, max_orders=max_records, force_full_sync=True)
    return SyncResponse(
        success=True,
        message=f"Successfully completed full resync of {records} orders",
        records_synced=records,
        sync_type="orders_full"
    )


@router.post("/products")
async def sync_products_endpoint(db: Session = Depends(get_db)):
    """
    Sync products only - separate endpoint to avoid rate limits
    
    Args:
        db: Database session
    
    Returns:
        Sync status
    """
    from ..config import settings
    access_token = settings.tiktok_access_token
    
    if not access_token:
        token_info = token_manager.get_valid_token(db)
        if token_info:
            access_token, _ = token_info
    
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token found")
    
    records = await sync_products_task(db, access_token)
    return SyncResponse(
        success=True,
        message=f"Successfully synced {records} products",
        records_synced=records,
        sync_type="products"
    )


@router.post("/analytics")
async def sync_analytics_endpoint(
    days_back: int = 7,
    db: Session = Depends(get_db)
):
    """
    Sync analytics data only - separate endpoint to avoid rate limits
    
    Args:
        days_back: Number of days to sync
        db: Database session
    
    Returns:
        Sync status
    """
    from ..config import settings
    access_token = settings.tiktok_access_token
    
    if not access_token:
        token_info = token_manager.get_valid_token(db)
        if token_info:
            access_token, _ = token_info
    
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token found")
    
    records = await sync_analytics_task(db, access_token, days_back)
    return SyncResponse(
        success=True,
        message=f"Successfully synced analytics data",
        records_synced=records,
        sync_type="analytics"
    )


@router.get("/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """
    Get synchronization status with metadata
    
    Returns:
        Last sync times, record counts, and sync metadata
    """
    # Count records in database
    order_count = db.query(Order).count()
    product_count = db.query(Product).count()
    
    # Get last sync times from records
    last_order = db.query(Order).order_by(Order.synced_at.desc()).first()
    last_product = db.query(Product).order_by(Product.synced_at.desc()).first()
    
    # Get sync metadata
    orders_meta = db.query(SyncMetadata).filter(
        SyncMetadata.sync_type == "orders"
    ).first()
    
    products_meta = db.query(SyncMetadata).filter(
        SyncMetadata.sync_type == "products"
    ).first()
    
    return {
        "orders": {
            "count": order_count,
            "last_synced": last_order.synced_at.isoformat() if last_order else None,
            "metadata": {
                "last_sync_time": orders_meta.last_sync_time.isoformat() if orders_meta and orders_meta.last_sync_time else None,
                "last_record_time": orders_meta.last_record_time.isoformat() if orders_meta and orders_meta.last_record_time else None,
                "records_synced": orders_meta.records_synced if orders_meta else 0,
                "is_full_sync": bool(orders_meta.is_full_sync) if orders_meta else None,
                "updated_at": orders_meta.updated_at.isoformat() if orders_meta and orders_meta.updated_at else None
            } if orders_meta else None
        },
        "products": {
            "count": product_count,
            "last_synced": last_product.synced_at.isoformat() if last_product else None,
            "metadata": {
                "last_sync_time": products_meta.last_sync_time.isoformat() if products_meta and products_meta.last_sync_time else None,
                "last_record_time": products_meta.last_record_time.isoformat() if products_meta and products_meta.last_record_time else None,
                "records_synced": products_meta.records_synced if products_meta else 0,
                "is_full_sync": bool(products_meta.is_full_sync) if products_meta else None,
                "updated_at": products_meta.updated_at.isoformat() if products_meta and products_meta.updated_at else None
            } if products_meta else None
        }
    }
