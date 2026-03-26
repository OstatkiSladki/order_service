from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.cart import Cart, CartItem


class CartRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def get_by_user_id(self, user_id: int) -> Cart | None:
    result = await self.session.execute(
      select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user_id)
    )
    return result.scalar_one_or_none()

  async def get_or_create(self, user_id: int) -> Cart:
    cart = await self.get_by_user_id(user_id)
    if cart is not None:
      return cart

    cart = Cart(user_id=user_id)
    self.session.add(cart)
    await self.session.commit()
    await self.session.refresh(cart)
    return await self.get_or_create(user_id)

  async def clear_items(self, cart_id: int) -> None:
    await self.session.execute(delete(CartItem).where(CartItem.cart_id == cart_id))

  async def get_item(self, cart_id: int, offer_id: int) -> CartItem | None:
    result = await self.session.execute(
      select(CartItem).where(CartItem.cart_id == cart_id, CartItem.offer_id == offer_id)
    )
    return result.scalar_one_or_none()

  async def has_items(self, cart_id: int) -> bool:
    result = await self.session.execute(select(CartItem.id).where(CartItem.cart_id == cart_id).limit(1))
    return result.scalar_one_or_none() is not None
