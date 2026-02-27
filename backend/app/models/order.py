"""
Order model for storing TikTok Shop orders
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, JSON, Index
from datetime import datetime
from ..database import Base


class Order(Base):
    """Store TikTok Shop orders"""
    
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)  # TikTok order ID
    order_number = Column(String, unique=True, index=True)
    status = Column(String, index=True)
    
    # Timestamps
    created_time = Column(DateTime, index=True)
    paid_time = Column(DateTime, nullable=True)
    shipped_time = Column(DateTime, nullable=True)
    delivered_time = Column(DateTime, nullable=True)
    
    # Financial
    total_amount = Column(Numeric(10, 2))
    currency = Column(String, default="GBP")
    item_count = Column(Integer)
    
    # Customer & shipping
    customer_id = Column(String, nullable=True)
    shipping_provider = Column(String, nullable=True)
    tracking_number = Column(String, nullable=True)
    
    # Raw data from TikTok API
    raw_data = Column(JSON)
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Order(order_number='{self.order_number}', status='{self.status}', total={self.total_amount})>"


# Create indexes
Index('idx_order_created_time', Order.created_time)
Index('idx_order_status', Order.status)
