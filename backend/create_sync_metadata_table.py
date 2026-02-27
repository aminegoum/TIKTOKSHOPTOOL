"""
Create sync_metadata table in the database
"""
from app.database import engine, Base
from app.models.sync_metadata import SyncMetadata

def create_sync_metadata_table():
    """Create the sync_metadata table"""
    print("Creating sync_metadata table...")
    
    # Create the table
    Base.metadata.create_all(bind=engine, tables=[SyncMetadata.__table__])
    
    print("✅ sync_metadata table created successfully!")

if __name__ == "__main__":
    create_sync_metadata_table()
