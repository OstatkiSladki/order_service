from fastapi import APIRouter, Depends, Query, Path, status, HTTPException
from typing import Optional
from datetime import timedelta

from schemas.order import Order, OrderListResponse, OrderStatus, PickupCode
from core.security import get_current_user_id
from services.order import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

# Инициализируем сервис
order_service = OrderService()

@router.get("", response_model=OrderListResponse, summary="История заказов пользователя")
async def list_orders(
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id)
):
    try:
        uid = int(user_id)
    except ValueError:
        uid = 0
        
    user_orders = order_service.repo.get_by_user_id(uid, status_filter.value if status_filter else None)
    
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = user_orders[start:end]
    
    return OrderListResponse(
        items=paginated_orders,
        total_count=len(user_orders),
        page=page,
        limit=limit
    )

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Order, summary="Создать заказ из текущей корзины")
async def create_order(user_id: str = Depends(get_current_user_id)):
    try:
        new_order = order_service.checkout_cart(user_id)
        return Order(**new_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{order_id}", response_model=Order, summary="Детали конкретного заказа")
async def get_order(order_id: int = Path(...), user_id: str = Depends(get_current_user_id)):
    order = order_service.repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return Order(**order)

@router.get("/{order_id}/pickup-code", response_model=PickupCode, summary="Получить код для получения заказа")
async def get_pickup_code(order_id: int = Path(...), user_id: str = Depends(get_current_user_id)):
    order = order_service.repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
        
    return PickupCode(
        code=order["_pickup_code"],
        expires_at=order["created_at"] + timedelta(days=1)
    )
