from fastapi import APIRouter, Depends, status
from schemas.cart import Cart, CartItem
from core.security import get_current_user_id
from services.cart import cart_service

router = APIRouter(prefix="/api/v1/cart", tags=["Carts"])

@router.get("", response_model=Cart, summary="Получить текущую корзину")
async def get_cart(user_id: str = Depends(get_current_user_id)):
    return cart_service.get_cart(user_id)

@router.delete("", status_code=status.HTTP_204_NO_CONTENT, summary="Очистить корзину")
async def clear_cart(user_id: str = Depends(get_current_user_id)):
    cart_service.clear_cart(user_id)
    return {"message": "Корзина очищена"}

@router.post("/items", status_code=status.HTTP_201_CREATED, summary="Добавить или обновить товар в корзине")
async def add_item_to_cart(item: CartItem, user_id: str = Depends(get_current_user_id)):
    cart_service.add_item(user_id, item)
    return {"message": "Товар добавлен"}
