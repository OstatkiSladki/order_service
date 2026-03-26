from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependency import CurrentUser, get_current_user, get_db_session
from schemas.order import Order, OrderListResponse, PickupCode
from services.order import OrderService

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def get_orders(
  status_filter: str | None = Query(None, alias="status"),
  page: int = Query(1, ge=1),
  limit: int = Query(20, ge=1, le=100),
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = OrderService(db)
  items, total_count = await service.get_orders(
    user_id=current_user.user_id,
    status=status_filter,
    page=page,
    limit=limit,
  )
  return OrderListResponse(items=items, total_count=total_count, page=page, limit=limit)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create_order(
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = OrderService(db)
  return await service.create_order(current_user.user_id)


@router.get("/{order_id}", response_model=Order)
async def get_order(
  order_id: int,
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = OrderService(db)
  return await service.get_order(order_id, current_user.user_id)


@router.get("/{order_id}/pickup-code", response_model=PickupCode)
async def get_pickup_code(
  order_id: int,
  current_user: CurrentUser = Depends(get_current_user),
  db: AsyncSession = Depends(get_db_session),
):
  service = OrderService(db)
  return await service.get_pickup_code(order_id, current_user.user_id)
