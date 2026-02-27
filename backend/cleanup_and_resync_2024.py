#!/usr/bin/env python3
"""
Script to clean up pre-2024 orders and restart sync with 2024+ filter
"""
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = "sqlite:///./tiktok_shop.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def cleanup_pre_2024_orders():
    """Delete all orders created before January 1, 2024"""
    db = SessionLocal()
    try:
        # January 1, 2024 00:00:00 UTC as datetime string
        jan_1_2024 = '2024-01-01 00:00:00'
        
        print("🔍 Checking current order count...")
        result = db.execute(text("SELECT COUNT(*) FROM orders"))
        total_before = result.scalar()
        print(f"   Total orders before cleanup: {total_before:,}")
        
        # Count pre-2024 orders
        result = db.execute(text(
            "SELECT COUNT(*) FROM orders WHERE created_time < :cutoff"
        ), {"cutoff": jan_1_2024})
        pre_2024_count = result.scalar()
        print(f"   Orders before 2024: {pre_2024_count:,}")
        
        # Count 2024+ orders
        result = db.execute(text(
            "SELECT COUNT(*) FROM orders WHERE created_time >= :cutoff"
        ), {"cutoff": jan_1_2024})
        post_2024_count = result.scalar()
        print(f"   Orders from 2024+: {post_2024_count:,}")
        
        if pre_2024_count == 0:
            print("✅ No pre-2024 orders to delete!")
            return
        
        print(f"\n🗑️  Deleting {pre_2024_count:,} pre-2024 orders...")
        db.execute(text(
            "DELETE FROM orders WHERE created_time < :cutoff"
        ), {"cutoff": jan_1_2024})
        db.commit()
        
        # Verify deletion
        result = db.execute(text("SELECT COUNT(*) FROM orders"))
        total_after = result.scalar()
        print(f"✅ Cleanup complete!")
        print(f"   Orders remaining: {total_after:,}")
        print(f"   Orders deleted: {total_before - total_after:,}")
        
        # Show date range of remaining orders
        result = db.execute(text(
            "SELECT MIN(created_time), MAX(created_time) FROM orders"
        ))
        min_time, max_time = result.fetchone()
        if min_time and max_time:
            print(f"\n📅 Remaining orders date range:")
            print(f"   Oldest: {min_time}")
            print(f"   Newest: {max_time}")
        
        # Clean up sync metadata to force fresh sync
        print(f"\n🔄 Resetting sync metadata...")
        db.execute(text("DELETE FROM sync_metadata WHERE sync_type = 'orders'"))
        db.commit()
        print(f"✅ Sync metadata reset - next sync will be incremental from 2024+")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    print("=" * 60)
    print("🧹 TikTok Shop - Pre-2024 Order Cleanup")
    print("=" * 60)
    print()
    
    try:
        cleanup_pre_2024_orders()
        print()
        print("=" * 60)
        print("✅ Cleanup Complete!")
        print("=" * 60)
        print()
        print("📝 Next Steps:")
        print("1. The sync is still running - you can stop it (Ctrl+C in terminal)")
        print("2. Restart the sync with: POST /api/sync/orders")
        print("3. The incremental sync will now only fetch 2024+ orders")
        print()
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
