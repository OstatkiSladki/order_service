from fastapi import APIRouter, Depends, Path, HTTPException, status
from schemas.management import OrderStatusUpdate
from core.security import get_user_role, get_user_venue_id

# Подключаем тот же самый сервис
from api.orders import order_service

router = APIRouter(prefix="/api/v1/management/orders", tags=["Management"])

@router.patch("/{order_id}/status", summary="Изменить статус заказа")
async def update_order_status(
    status_update: OrderStatusUpdate,
    order_id: int = Path(...),
    user_role: str = Depends(get_user_role),
    venue_id: int = Depends(get_user_venue_id)
):
    try:
        if status_update.status.value == "picked_up":
            order_service.update_to_picked_up(order_id, status_update.pickup_code)
            return {"message": f"Статус заказа {order_id} обновлен на picked_up"}
        else:
            # Если просто отмена
            order = order_service.repo.update_status(order_id, status_update.status.value)
            if not order:
                raise KeyError("Заказ не найден")
            return {"message": f"Статус заказа {order_id} обновлен на {status_update.status.value}"}
            
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
