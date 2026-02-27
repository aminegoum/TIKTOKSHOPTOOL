# Incremental Sync Implementation Plan

## Current Status
- Full sync running: 276K+ orders synced
- Current sync.py does NOT use time filters
- SyncMetadata model created but not yet used
- Need to implement incremental logic

## Implementation Steps

### 1. Update sync_orders_task() Function
**Location**: `backend/app/api/sync.py` lines 31-114

**Changes Needed**:
```python
async def sync_orders_task(
    db: Session, 
    access_token: str, 
    days_back: int = 30, 
    max_orders: int = None,
    force_full_sync: bool = False  # NEW PARAMETER
):
    from ..models import SyncMetadata
    from datetime import datetime, timedelta
    
    # Check for last sync metadata
    last_sync = db.query(SyncMetadata).filter(
        SyncMetadata.sync_type == "orders"
    ).first()
    
    # Determine sync mode
    start_time = None
    end_time = None
    is_incremental = False
    
    if last_sync and not force_full_sync:
        # INCREMENTAL SYNC: Only fetch orders since last sync
        # Add 5-minute overlap to catch any late-arriving orders
        start_time = last_sync.last_sync_time - timedelta(minutes=5)
        end_time = datetime.utcnow()
        is_incremental = True
        print(f"🔄 Incremental sync from {start_time} to {end_time}")
    else:
        # FULL SYNC: Fetch all orders
        print(f"📥 Full sync - fetching all orders")
    
    # ... rest of sync logic with start_time/end_time passed to client.get_orders()
    
    # After successful sync, update metadata
    sync_meta = SyncMetadata(
        sync_type="orders",
        last_sync_time=datetime.utcnow(),
        last_record_time=most_recent_order_time,  # Track newest order
        records_synced=synced_count,
        is_full_sync=0 if is_incremental else 1
    )
    db.merge(sync_meta)  # Insert or update
    db.commit()
```

### 2. Add Full Resync Endpoint
**Location**: `backend/app/api/sync.py` after line 345

**New Endpoint**:
```python
@router.post("/orders/full")
async def sync_orders_full_endpoint(
    max_records: int = None,
    db: Session = Depends(get_db)
):
    """
    Full resync of ALL orders - bypasses incremental sync
    
    Use this when:
    - Initial setup
    - Data corruption detected
    - Manual refresh needed
    
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
    
    # Force full sync by passing force_full_sync=True
    records = await sync_orders_task(
        db, 
        access_token, 
        max_orders=max_records,
        force_full_sync=True  # KEY PARAMETER
    )
    
    return SyncResponse(
        success=True,
        message=f"Successfully completed full resync of {records} orders",
        records_synced=records,
        sync_type="orders_full"
    )
```

### 3. Update Existing /orders Endpoint
**Location**: `backend/app/api/sync.py` lines 313-345

**Change**:
```python
@router.post("/orders")
async def sync_orders_endpoint(
    max_records: int = None,
    force_full: bool = False,  # NEW PARAMETER
    db: Session = Depends(get_db)
):
    """
    Sync orders - uses incremental sync by default
    
    Args:
        max_records: Maximum number of orders to sync (None = unlimited)
        force_full: Force full resync instead of incremental (default: False)
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
    
    records = await sync_orders_task(
        db, 
        access_token, 
        max_orders=max_records,
        force_full_sync=force_full  # Pass through
    )
    
    sync_type = "orders_full" if force_full else "orders_incremental"
    
    return SyncResponse(
        success=True,
        message=f"Successfully synced {records} orders",
        records_synced=records,
        sync_type=sync_type
    )
```

### 4. Update /status Endpoint
**Location**: `backend/app/api/sync.py` lines 414-439

**Enhancement**:
```python
@router.get("/status")
async def get_sync_status(db: Session = Depends(get_db)):
    """
    Get synchronization status including metadata
    
    Returns:
        Last sync times, record counts, and sync metadata
    """
    from ..models import SyncMetadata
    
    # Count records in database
    order_count = db.query(Order).count()
    product_count = db.query(Product).count()
    
    # Get last sync times from orders/products
    last_order = db.query(Order).order_by(Order.synced_at.desc()).first()
    last_product = db.query(Product).order_by(Product.synced_at.desc()).first()
    
    # Get sync metadata
    order_sync_meta = db.query(SyncMetadata).filter(
        SyncMetadata.sync_type == "orders"
    ).first()
    
    product_sync_meta = db.query(SyncMetadata).filter(
        SyncMetadata.sync_type == "products"
    ).first()
    
    return {
        "orders": {
            "count": order_count,
            "last_synced": last_order.synced_at.isoformat() if last_order else None,
            "metadata": {
                "last_sync_time": order_sync_meta.last_sync_time.isoformat() if order_sync_meta else None,
                "last_record_time": order_sync_meta.last_record_time.isoformat() if order_sync_meta and order_sync_meta.last_record_time else None,
                "records_synced": order_sync_meta.records_synced if order_sync_meta else 0,
                "is_full_sync": bool(order_sync_meta.is_full_sync) if order_sync_meta else None
            } if order_sync_meta else None
        },
        "products": {
            "count": product_count,
            "last_synced": last_product.synced_at.isoformat() if last_product else None,
            "metadata": {
                "last_sync_time": product_sync_meta.last_sync_time.isoformat() if product_sync_meta else None,
                "records_synced": product_sync_meta.records_synced if product_sync_meta else 0,
                "is_full_sync": bool(product_sync_meta.is_full_sync) if product_sync_meta else None
            } if product_sync_meta else None
        }
    }
```

## Testing Plan

### After Current Sync Completes

1. **Test Incremental Sync**:
   ```bash
   curl -X POST http://localhost:8000/api/sync/orders
   # Should only fetch orders since last sync (very fast!)
   ```

2. **Test Full Resync**:
   ```bash
   curl -X POST http://localhost:8000/api/sync/orders/full
   # Should fetch ALL orders (slow, but comprehensive)
   ```

3. **Check Status**:
   ```bash
   curl http://localhost:8000/api/sync/status
   # Should show metadata with last sync times
   ```

4. **Verify Incremental Works**:
   - Wait a few minutes
   - Run incremental sync again
   - Should only fetch new orders (< 1 minute)

## Expected Results

### Before Implementation
- Every sync fetches ALL 276K+ orders
- Takes hours to complete
- Wastes API calls and resources

### After Implementation
- **First sync**: Full sync (one-time, gets all historical data)
- **Subsequent syncs**: Incremental (only new orders, < 1 minute)
- **Manual full resync**: Available when needed via `/orders/full`

## Performance Improvement

| Metric | Before | After (Incremental) | Improvement |
|--------|--------|---------------------|-------------|
| Sync Time | 2-3 hours | 5-30 seconds | **99%+ faster** |
| API Calls | 5,500+ | 1-10 | **99%+ reduction** |
| Orders Fetched | 276,000+ | 10-100 | **99%+ reduction** |
| User Experience | Blocked | Instant | **Seamless** |

## Safety Features

1. **5-Minute Overlap**: Ensures no orders are missed
2. **Upsert Logic**: Prevents duplicates even with overlap
3. **Fallback**: If no metadata exists, automatically does full sync
4. **Manual Override**: `/orders/full` endpoint for forced full resync

## Next Steps

1. ✅ Let current sync complete (276K+ orders)
2. ⏳ Implement changes to sync.py
3. ⏳ Test incremental sync
4. ⏳ Verify performance improvements
5. ⏳ Update frontend to show sync type
6. ⏳ Document for users
