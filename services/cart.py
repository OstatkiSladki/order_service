from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart import CartItem
from repositories.cart import CartRepository
from rpc.catalog_client import get_offer_info
from schemas.cart import CartItemCreate


class CartService:
  def __init__(self, session: AsyncSession):
    self.repo = CartRepository(session)
    self.session = session

  async def get_cart(self, user_id: int):
    return await self.repo.get_or_create(user_id)

  async def clear_cart(self, user_id: int) -> None:
    cart = await self.repo.get_by_user_id(user_id)
    if cart is None:
      return
    await self.repo.clear_items(cart.id)
    cart.venue_id = None
    await self.session.commit()

  async def add_item(self, user_id: int, item: CartItemCreate) -> dict[str, str]:
    offer_info = get_offer_info(item.offer_id)
    if not offer_info:
      raise HTTPException(status_code=404, detail="Offer not found")

    cart = await self.repo.get_or_create(user_id)

    if cart.venue_id is not None and cart.venue_id != offer_info["venue_id"]:
      if await self.repo.has_items(cart.id):
        raise HTTPException(
          status_code=400,
          detail="Одна корзина может содержать товары только из одного заведения",
        )
      cart.venue_id = offer_info["venue_id"]
    elif cart.venue_id is None:
      cart.venue_id = offer_info["venue_id"]

    if item.quantity <= 0:
      existing_item = await self.repo.get_item(cart.id, item.offer_id)
      if existing_item is not None:
        await self.session.delete(existing_item)
      await self.session.commit()
      return {"message": "item removed"}

    existing_item = await self.repo.get_item(cart.id, item.offer_id)
    if existing_item is not None:
      existing_item.quantity = item.quantity
    else:
      self.session.add(CartItem(cart_id=cart.id, offer_id=item.offer_id, quantity=item.quantity))

    await self.session.commit()
    return {"message": "item added/updated"}
