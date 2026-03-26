from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependency import CurrentUser, get_current_user, get_db_session
from schemas.cart import Cart, CartItemCreate
from services.cart import CartService

router = APIRouter()


@router.get("", response_model=Cart)
async def get_cart(
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = CartService(db)
  return await service.get_cart(current_user.user_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = CartService(db)
  await service.clear_cart(current_user.user_id)
  return None


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_cart_item(
  item: CartItemCreate,
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = CartService(db)
  return await service.add_item(current_user.user_id, item)
