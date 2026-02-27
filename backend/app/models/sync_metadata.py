"""
Sync metadata model for tracking last sync times
"""
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
from ..database import Base


class SyncMetadata(Base):
    """Store sync metadata to enable incremental syncing"""
    
    __tablename__ = "sync_metadata"
    
    sync_type = Column(String, primary_key=True)  # "orders", "products", "analytics"
    last_sync_time = Column(DateTime, nullable=False)  # When the last sync completed
    last_record_time = Column(DateTime, nullable=True)  # Timestamp of the most recent record synced
    records_synced = Column(Integer, default=0)  # Total records synced in last sync
    is_full_sync = Column(Integer, default=0)  # 1 if last sync was a full sync, 0 if incremental
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SyncMetadata(type='{self.sync_type}', last_sync='{self.last_sync_time}', records={self.records_synced})>"
