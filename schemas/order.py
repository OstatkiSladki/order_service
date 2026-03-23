from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from models.order import OrderStatus

class OrderItemBase(BaseModel):
    offer_id: int
    product_name_snapshot: str
    price_snapshot: float
    quantity: int
    subtotal: float

class OrderItem(OrderItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class OrderBase(BaseModel):
    venue_id: int
    status: OrderStatus
    total_amount: float
    discount_amount: float = 0.0
    service_fee: float
    venue_payout: float
    final_amount: float
    promo_code_id: Optional[int] = None
    pickup_time: Optional[datetime] = None

class Order(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []
    model_config = ConfigDict(from_attributes=True)

class OrderListResponse(BaseModel):
    items: List[Order]
    total_count: int
    page: int
    limit: int

class PickupCode(BaseModel):
    code: str = Field(..., pattern=r'^[0-9]{6}$')
    expires_at: datetime
