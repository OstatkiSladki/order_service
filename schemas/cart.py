from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class CartItemBase(BaseModel):
    offer_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CartBase(BaseModel):
    venue_id: Optional[int] = None

class Cart(CartBase):
    id: int
    items: List[CartItem] = []
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
