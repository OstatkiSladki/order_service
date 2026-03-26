from fastapi import APIRouter

from api import cart, management, orders

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(cart.router, prefix="/cart", tags=["Carts"])
v1_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
v1_router.include_router(management.router, prefix="/management", tags=["Management"])
