from pydantic import BaseModel

class CartItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class CartResponse(BaseModel):
    id: int
    user_id: int
    venue_id: int | None = None
    items: list[CartItem] = []
    total_price: float