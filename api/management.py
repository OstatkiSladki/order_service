from fastapi import APIRouter, Depends, Path
from schemas.management import OrderStatusUpdate
from core.security import get_user_role, get_user_venue_id

router = APIRouter(prefix="/api/v1/management/orders", tags=["Management"])

@router.patch("/{order_id}/status", summary="Изменить статус заказа")
async def update_order_status(
    status_update: OrderStatusUpdate,
    order_id: int = Path(...),
    user_role: str = Depends(get_user_role),
    venue_id: int = Depends(get_user_venue_id)
):
    return {"message": f"Статус заказа {order_id} обновлен на {status_update.status}"}
