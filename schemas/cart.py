from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CartItem(BaseModel):
    offer_id: int
    quantity: int

class Cart(BaseModel):
    id: int
    venue_id: Optional[int] = None
    items: List[CartItem] = []
    updated_at: datetime
