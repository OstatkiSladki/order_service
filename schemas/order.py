from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    created = "created"
    paid = "paid"
    picked_up = "picked_up"
    cancelled = "cancelled"

class OrderItem(BaseModel):
    offer_id: int
    product_name_snapshot: str
    price_snapshot: float
    quantity: int
    subtotal: float

class Order(BaseModel):
    id: int
    user_id: int
    venue_id: int
    status: OrderStatus
    total_amount: float
    discount_amount: float = 0.0
    service_fee: float
    venue_payout: float
    final_amount: float
    promo_code_id: Optional[int] = None
    pickup_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

class OrderListResponse(BaseModel):
    items: List[Order] = []
    total_count: int
    page: int
    limit: int

class PickupCode(BaseModel):
    code: str = Field(..., pattern=r"^\d{6}$")
    expires_at: datetime
