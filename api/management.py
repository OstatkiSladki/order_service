from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from dependency import ManagementUser, get_db_session, get_management_user
from schemas.management import OrderStatusUpdate
from services.management import ManagementService

router = APIRouter()


@router.patch("/orders/{order_id}/status")
async def update_status(
  body: OrderStatusUpdate,
  order_id: int = Path(...),
  current_user: ManagementUser = Depends(get_management_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = ManagementService(db)
  return await service.update_status(
    order_id=order_id,
    body=body,
    role=current_user.role,
    venue_id=current_user.venue_id,
  )
