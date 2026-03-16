from fastapi import APIRouter, Depends, status
from schemas.cart import Cart, CartItem
from core.security import get_current_user_id
from datetime import datetime, timezone
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/cart", tags=["Carts"])

# Временная in-memory "база данных"
FAKEDB_CARTS: Dict[str, Dict[str, Any]] = {}

def get_or_create_cart(user_id: str) -> dict:
    if user_id not in FAKEDB_CARTS:
        FAKEDB_CARTS[user_id] = {
            "id": len(FAKEDB_CARTS) + 1,
            "venue_id": None,
            "items": [],
            "updated_at": datetime.now(timezone.utc)
        }
    return FAKEDB_CARTS[user_id]

@router.get("", response_model=Cart, summary="Получить текущую корзину")
async def get_cart(user_id: str = Depends(get_current_user_id)):
    cart_data = get_or_create_cart(user_id)
    return cart_data

@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Очистить корзину")
async def clear_cart(user_id: str = Depends(get_current_user_id)):
    if user_id in FAKEDB_CARTS:
        del FAKEDB_CARTS[user_id]
    return {"message": "Корзина очищена"}

@router.post("/items", status_code=status.HTTP_201_CREATED, summary="Добавить или обновить товар в корзине")
async def add_item_to_cart(item: CartItem, user_id: str = Depends(get_current_user_id)):
    cart_data = get_or_create_cart(user_id)
    existing_item = next((i for i in cart_data["items"] if i["offer_id"] == item.offer_id), None)
    if existing_item:
        existing_item["quantity"] += item.quantity
    else:
        cart_data["items"].append(item.model_dump())
    cart_data["updated_at"] = datetime.now(timezone.utc)
    return {"message": "Товар добавлен"}
