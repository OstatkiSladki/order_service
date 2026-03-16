from fastapi import APIRouter, Depends, Query, Path, status
from typing import Optional
from schemas.order import Order, OrderListResponse, OrderStatus, PickupCode, OrderItem
from core.security import get_current_user_id
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])

@router.get("", response_model=OrderListResponse, summary="История заказов пользователя")
async def list_orders(
    status: Optional[OrderStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id)
):
    return OrderListResponse(items=[], total_count=0, page=page, limit=limit)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Order, summary="Создать заказ из текущей корзины")
async def create_order(user_id: str = Depends(get_current_user_id)):
    return Order(
        id=1, user_id=int(user_id), venue_id=1, status=OrderStatus.created, 
        total_amount=100.0, discount_amount=0.0, service_fee=10.0, 
        venue_payout=90.0, final_amount=110.0, created_at=datetime.now(timezone.utc), 
        updated_at=datetime.now(timezone.utc), items=[]
    )

@router.get("/{order_id}", response_model=Order, summary="Детали конкретного заказа")
async def get_order(order_id: int = Path(...), user_id: str = Depends(get_current_user_id)):
    return Order(
        id=order_id, user_id=int(user_id), venue_id=1, status=OrderStatus.created, 
        total_amount=100.0, discount_amount=0.0, service_fee=10.0, 
        venue_payout=90.0, final_amount=110.0, created_at=datetime.now(timezone.utc), 
        updated_at=datetime.now(timezone.utc), items=[]
    )

@router.get("/{order_id}/pickup-code", response_model=PickupCode, summary="Получить код для получения заказа")
async def get_pickup_code(order_id: int = Path(...), user_id: str = Depends(get_current_user_id)):
    return PickupCode(code="111111", expires_at=datetime.now(timezone.utc))
