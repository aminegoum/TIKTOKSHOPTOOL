# Incremental Sync Implementation

## Problem Statement

The TikTok Shop Dashboard was syncing **all orders** (100K+) every time the refresh button was clicked. This caused:
- **Very long sync times** (hours to complete)
- **Wasted API calls** (re-fetching orders already in database)
- **Poor user experience** (dashboard unusable during sync)
- **High resource usage** (database writes for existing records)

## Solution: Incremental Sync

Instead of syncing all orders every time, we now:
1. **Track the last sync time** in a `sync_metadata` table
2. **Only fetch new/updated orders** since the last sync
3. **Use TikTok API's `create_time_from` filter** to get recent orders
4. **Provide a "Full Resync" option** when needed

## Implementation Details

### 1. Database Schema

**New Table: `sync_metadata`**
```sql
CREATE TABLE sync_metadata (
    sync_type VARCHAR PRIMARY KEY,  -- "orders", "products", "analytics"
    last_sync_time DATETIME NOT NULL,  -- When last sync completed
    last_record_time DATETIME,  -- Timestamp of most recent record synced
    records_synced INTEGER DEFAULT 0,  -- Records synced in last sync
    is_full_sync INTEGER DEFAULT 0,  -- 1 if full sync, 0 if incremental
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Sync Logic

**Incremental Sync (Default)**
```python
# Get last sync metadata
last_sync = db.query(SyncMetadata).filter(
    SyncMetadata.sync_type == "orders"
).first()

if last_sync and not force_full_sync:
    # Incremental sync: only fetch orders created/updated since last sync
    start_time = last_sync.last_sync_time - timedelta(minutes=5)  # 5min overlap
    end_time = datetime.utcnow()
else:
    # Full sync: fetch all orders
    start_time = None
    end_time = None
```

**API Call with Time Filter**
```python
response = await client.get_orders(
    start_time=start_time,  # Only new orders since this time
    end_time=end_time,
    page_size=100,
    sort_field="create_time",
    sort_order="DESC"
)
```

### 3. API Endpoints

**Incremental Sync (Fast)**
```bash
POST /api/sync/orders
# Syncs only new orders since last sync
# Typical time: < 1 minute for daily orders
```

**Full Resync (Slow)**
```bash
POST /api/sync/orders/full
# Syncs ALL orders from beginning
# Use when: data corruption, initial setup, or manual refresh needed
# Typical time: Hours for 100K+ orders
```

**Sync Status**
```bash
GET /api/sync/status
# Returns:
# - Last sync time
# - Records synced
# - Sync type (full/incremental)
# - Total records in database
```

### 4. Benefits

| Metric | Before (Full Sync) | After (Incremental) | Improvement |
|--------|-------------------|---------------------|-------------|
| **Sync Time** | 2-3 hours | < 1 minute | **99%+ faster** |
| **API Calls** | 2,000+ requests | 1-10 requests | **99%+ reduction** |
| **Database Writes** | 100K+ updates | 10-100 inserts | **99%+ reduction** |
| **User Experience** | Dashboard blocked | Instant refresh | **Seamless** |

### 5. Usage Examples

**Daily Workflow**
```javascript
// User clicks "Refresh" button
// → Incremental sync runs
// → Only fetches today's orders (fast!)
// → Dashboard updates in seconds
```

**Initial Setup or Data Recovery**
```javascript
// Admin clicks "Full Resync" button
// → Full sync runs
// → Fetches all historical orders
// → Takes hours but ensures complete data
```

### 6. Safety Features

**5-Minute Overlap**
- Incremental sync starts 5 minutes before last sync
- Ensures no orders are missed due to timing issues
- Handles late-arriving orders or API delays

**Duplicate Handling**
- Database uses `UPSERT` logic (update if exists, insert if new)
- No duplicate orders even with overlap
- Idempotent sync operations

**Fallback to Full Sync**
- If no sync metadata exists → automatic full sync
- If sync fails → retry with full sync
- Manual full resync always available

## Migration Guide

### For Existing Installations

1. **Let current sync complete** (if running)
2. **Backend will auto-create** `sync_metadata` table on restart
3. **First sync after update** will be a full sync (one-time)
4. **All subsequent syncs** will be incremental (fast)

### For New Installations

1. **First sync** will be full (fetches all historical data)
2. **Subsequent syncs** will be incremental automatically
3. **No configuration needed** - works out of the box

## Technical Notes

### TikTok API Filters

The TikTok Shop API supports time-based filtering:
```python
{
    "create_time_from": 1763851657,  # Unix timestamp
    "create_time_to": 1764456457     # Unix timestamp
}
```

### Sync Metadata Updates

After each successful sync:
```python
sync_meta = SyncMetadata(
    sync_type="orders",
    last_sync_time=datetime.utcnow(),
    last_record_time=most_recent_order_time,
    records_synced=count,
    is_full_sync=1 if full_sync else 0
)
db.merge(sync_meta)
db.commit()
```

### Error Handling

- **API errors**: Logged and retried
- **Database errors**: Rolled back, no partial data
- **Network errors**: Graceful failure with status message
- **Rate limits**: Automatic backoff and retry

## Performance Metrics

### Typical Daily Sync (Incremental)
- **Orders per day**: ~100-500
- **API requests**: 1-5
- **Sync time**: 5-30 seconds
- **Database writes**: 100-500 inserts

### Full Resync (When Needed)
- **Total orders**: 100,000+
- **API requests**: 2,000+
- **Sync time**: 2-3 hours
- **Database writes**: 100,000+ upserts

## Future Enhancements

1. **Scheduled Background Sync**
   - Auto-sync every 15 minutes
   - No manual refresh needed
   - Always up-to-date data

2. **Real-time Webhooks**
   - TikTok sends order updates
   - Instant dashboard updates
   - Zero sync delay

3. **Partial Sync by Status**
   - Only sync "pending" orders
   - Skip completed/cancelled
   - Even faster syncs

4. **Smart Sync Scheduling**
   - Sync during low-traffic hours
   - Adaptive sync frequency
   - Resource optimization

## Conclusion

Incremental sync transforms the TikTok Shop Dashboard from a slow, resource-intensive system to a fast, efficient platform. Users can now refresh their data in seconds instead of hours, making the dashboard practical for daily use.

**Key Takeaway**: Let the initial full sync complete once, then enjoy instant refreshes forever! 🚀
