import grpc
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.cart import CartItem
from repositories.cart import CartRepository
from rpc.catalog_client import CatalogGrpcError, CatalogInventoryClient, CircuitBreakerOpenError
from schemas.cart import CartItemCreate


class CartService:
  def __init__(self, session: AsyncSession, catalog_client: CatalogInventoryClient):
    self.repo = CartRepository(session)
    self.session = session
    self.catalog_client = catalog_client

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
    cart = await self.repo.get_or_create(user_id)

    if item.quantity <= 0:
      existing_item = await self.repo.get_item(cart.id, item.offer_id)
      if existing_item is not None:
        await self.session.delete(existing_item)
      if not await self.repo.has_items(cart.id):
        cart.venue_id = None
      await self.session.commit()
      return {"message": "item removed"}

    try:
      offer_snapshot = await self.catalog_client.get_offer_snapshot(item.offer_id)
    except grpc.aio.AioRpcError as exc:
      if exc.code() == grpc.StatusCode.NOT_FOUND:
        raise HTTPException(status_code=404, detail="Offer not found") from exc
      raise HTTPException(status_code=503, detail="Catalog service is unavailable") from exc
    except (CatalogGrpcError, CircuitBreakerOpenError) as exc:
      raise HTTPException(status_code=503, detail="Catalog service is unavailable") from exc

    if not offer_snapshot.is_active:
      raise HTTPException(status_code=400, detail="Offer is not available")

    if cart.venue_id is not None and cart.venue_id != offer_snapshot.venue_id:
      if await self.repo.has_items(cart.id):
        raise HTTPException(
          status_code=400,
          detail="Одна корзина может содержать товары только из одного заведения",
        )
      cart.venue_id = offer_snapshot.venue_id
    elif cart.venue_id is None:
      cart.venue_id = offer_snapshot.venue_id

    existing_item = await self.repo.get_item(cart.id, item.offer_id)
    if existing_item is not None:
      existing_item.quantity = item.quantity
    else:
      self.session.add(CartItem(cart_id=cart.id, offer_id=item.offer_id, quantity=item.quantity))

    await self.session.commit()
    return {"message": "item added/updated"}
