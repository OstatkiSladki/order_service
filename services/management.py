from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import OrderStatus
from repositories.order import OrderRepository
from schemas.management import OrderStatusUpdate


class ManagementService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.order_repo = OrderRepository(session)

  async def update_status(self, order_id: int, body: OrderStatusUpdate, role: str, venue_id: int) -> dict[str, str]:
    if role not in {"staff", "admin"}:
      raise HTTPException(status_code=403, detail="Forbidden")

    order = await self.order_repo.get_by_id(order_id)
    if order is None:
      raise HTTPException(status_code=404, detail="Order not found")

    if role == "staff" and venue_id != order.venue_id:
      raise HTTPException(status_code=403, detail="Forbidden venue")

    if body.status == "picked_up":
      if not body.pickup_code or body.pickup_code != order.pickup_code:
        raise HTTPException(status_code=403, detail="Invalid pickup code")

    try:
      order.status = OrderStatus[body.status]
    except KeyError as exc:
      raise HTTPException(status_code=400, detail="Invalid status") from exc

    await self.session.commit()
    return {"message": "Status updated successfully"}
