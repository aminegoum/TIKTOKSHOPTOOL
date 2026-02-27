"""
API routes
"""
from .auth import router as auth_router
from .sync import router as sync_router
from .kpis import router as kpis_router
from .analytics import router as analytics_router
from .orders import router as orders_router
from .products import router as products_router

__all__ = ["auth_router", "sync_router", "kpis_router", "analytics_router", "orders_router", "products_router"]
