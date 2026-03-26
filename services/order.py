import secrets

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.order import Order, OrderItem, OrderStatus
from repositories.cart import CartRepository
from repositories.order import OrderRepository
from rpc.catalog_client import get_offer_info
from schemas.order import PickupCode


class OrderService:
  def __init__(self, session: AsyncSession):
    self.session = session
    self.cart_repo = CartRepository(session)
    self.order_repo = OrderRepository(session)

  @staticmethod
  def generate_pickup_code() -> str:
    return str(secrets.randbelow(900000) + 100000)

  async def get_orders(self, user_id: int, status: str | None, page: int, limit: int) -> tuple[list[Order], int]:
    return await self.order_repo.list_for_user(user_id=user_id, status=status, page=page, limit=limit)

  async def create_order(self, user_id: int) -> Order:
    cart = await self.cart_repo.get_by_user_id(user_id)
    if not cart or not cart.items:
      raise HTTPException(status_code=400, detail="Cart is empty")

    new_order = Order(
      user_id=user_id,
      venue_id=cart.venue_id,
      status=OrderStatus.created,
      pickup_code=self.generate_pickup_code(),
    )
    self.session.add(new_order)
    await self.session.flush()

    total_amount = 0.0
    for item in cart.items:
      offer_info = get_offer_info(item.offer_id)
      subtotal = item.quantity * offer_info["price"]
      total_amount += subtotal

      order_item = OrderItem(
        order_id=new_order.id,
        offer_id=item.offer_id,
        product_name_snapshot=offer_info["product_name"],
        price_snapshot=offer_info["price"],
        quantity=item.quantity,
        subtotal=subtotal,
      )
      self.session.add(order_item)

    new_order.total_amount = total_amount
    new_order.final_amount = total_amount
    new_order.service_fee = total_amount * 0.1
    new_order.venue_payout = total_amount * 0.9

    await self.cart_repo.clear_items(cart.id)
    cart.venue_id = None
    await self.session.commit()

    saved_order = await self.order_repo.get_by_id(new_order.id)
    if saved_order is None:
      raise HTTPException(status_code=500, detail="Failed to load created order")
    return saved_order

  async def get_order(self, order_id: int, user_id: int) -> Order:
    order = await self.order_repo.get_by_id_for_user(order_id, user_id)
    if order is None:
      raise HTTPException(status_code=404, detail="Order not found")
    return order

  async def get_pickup_code(self, order_id: int, user_id: int) -> PickupCode:
    order = await self.get_order(order_id=order_id, user_id=user_id)
    if order.status != OrderStatus.paid:
      raise HTTPException(status_code=403, detail="Order not paid yet")
    return PickupCode(code=order.pickup_code, expires_at=order.updated_at)
