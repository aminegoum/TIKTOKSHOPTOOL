"""
Product model for storing TikTok Shop products
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, JSON, Index
from datetime import datetime
from ..database import Base


class Product(Base):
    """Store TikTok Shop products"""
    
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)  # TikTok product ID
    name = Column(String, nullable=False)
    sku = Column(String, index=True)
    status = Column(String, index=True)
    
    # Pricing & inventory
    price = Column(Numeric(10, 2))
    stock_quantity = Column(Integer)
    
    # Categorization
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    
    # Media
    image_url = Column(String, nullable=True)
    
    # Link to LookFantastic catalog
    lookfantastic_sku = Column(String, nullable=True, index=True)
    
    # Raw data from TikTok API
    raw_data = Column(JSON)
    
    # Metadata
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Product(name='{self.name}', sku='{self.sku}', price={self.price})>"


# Create indexes
Index('idx_product_sku', Product.sku)
Index('idx_product_status', Product.status)
