from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.order import Order, OrderStatus


class OrderRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def get_by_id(self, order_id: int) -> Order | None:
    result = await self.session.execute(
      select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    return result.scalar_one_or_none()

  async def get_by_id_for_user(self, order_id: int, user_id: int) -> Order | None:
    result = await self.session.execute(
      select(Order)
      .options(selectinload(Order.items))
      .where(Order.id == order_id, Order.user_id == user_id)
    )
    return result.scalar_one_or_none()

  async def list_for_user(self, user_id: int, status: str | None, page: int, limit: int) -> tuple[list[Order], int]:
    base_stmt = select(Order).where(Order.user_id == user_id)
    if status:
      try:
        base_stmt = base_stmt.where(Order.status == OrderStatus[status])
      except KeyError:
        return [], 0

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total_count = (await self.session.execute(count_stmt)).scalar_one()

    paged_stmt = (
      base_stmt.options(selectinload(Order.items))
      .offset((page - 1) * limit)
      .limit(limit)
      .order_by(Order.id.desc())
    )
    result = await self.session.execute(paged_stmt)
    return result.scalars().all(), total_count
