from __future__ import annotations

from decimal import Decimal

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

from core.config import get_settings
from core.database import get_session_maker
from models.order import Order, OrderStatus
from repositories.order import OrderRepository
from rpc.generated import order_query_pb2, order_query_pb2_grpc

_SERVICE_NAME = "ostatki.grpc.v1.OrderQueryService"


def _to_money(value: float | Decimal | None) -> str:
  if value is None:
    return "0.00"
  return f"{Decimal(str(value)):.2f}"


def _to_order_response(order: Order) -> order_query_pb2.GetOrderByIdResponse:
  items = [
    order_query_pb2.OrderItem(
      offer_id=int(item.offer_id),
      product_name=str(item.product_name_snapshot),
      price=_to_money(item.price_snapshot),
      quantity=int(item.quantity),
      subtotal=_to_money(item.subtotal),
    )
    for item in order.items
  ]
  return order_query_pb2.GetOrderByIdResponse(
    order_id=int(order.id),
    user_id=int(order.user_id),
    venue_id=int(order.venue_id),
    amount=_to_money(order.total_amount),
    discount_amount=_to_money(order.discount_amount),
    final_amount=_to_money(order.final_amount),
    currency="RUB",
    status=str(order.status.value),
    items=items,
  )


class OrderQueryGrpcService(order_query_pb2_grpc.OrderQueryServiceServicer):
  async def ValidateOrder(
    self,
    request: order_query_pb2.ValidateOrderRequest,
    context: grpc.aio.ServicerContext,
  ) -> order_query_pb2.ValidateOrderResponse:
    session_maker = get_session_maker()
    async with session_maker() as session:
      repository = OrderRepository(session)
      order = await repository.get_by_id(int(request.order_id))
      if order is None:
        await context.abort(grpc.StatusCode.NOT_FOUND, "Order not found")

      if int(order.user_id) != int(request.user_id):
        return order_query_pb2.ValidateOrderResponse(
          is_valid=False,
          order_status=str(order.status.value),
          error_code="ORDER_OWNER_MISMATCH",
          error_message="Order does not belong to the user",
        )

      if order.status == OrderStatus.cancelled:
        return order_query_pb2.ValidateOrderResponse(
          is_valid=False,
          order_status=str(order.status.value),
          error_code="ORDER_CANCELLED",
          error_message="Order is cancelled",
        )

      return order_query_pb2.ValidateOrderResponse(
        is_valid=True,
        order_status=str(order.status.value),
      )

  async def GetOrderById(
    self,
    request: order_query_pb2.GetOrderByIdRequest,
    context: grpc.aio.ServicerContext,
  ) -> order_query_pb2.GetOrderByIdResponse:
    session_maker = get_session_maker()
    async with session_maker() as session:
      repository = OrderRepository(session)
      order = await repository.get_by_id(int(request.order_id))
      if order is None:
        await context.abort(grpc.StatusCode.NOT_FOUND, "Order not found")
      return _to_order_response(order)

  async def GetOrderDetails(
    self,
    request: order_query_pb2.GetOrderDetailsRequest,
    context: grpc.aio.ServicerContext,
  ) -> order_query_pb2.GetOrderDetailsResponse:
    response = await self.GetOrderById(
      order_query_pb2.GetOrderByIdRequest(order_id=request.order_id),
      context,
    )
    return order_query_pb2.GetOrderDetailsResponse(
      order_id=response.order_id,
      user_id=response.user_id,
      venue_id=response.venue_id,
      amount=response.amount,
      discount_amount=response.discount_amount,
      final_amount=response.final_amount,
      currency=response.currency,
      status=response.status,
      items=response.items,
    )


async def start_grpc_server() -> tuple[grpc.aio.Server, health.HealthServicer]:
  settings = get_settings()
  server = grpc.aio.server()
  health_servicer = health.aio.HealthServicer()

  order_query_pb2_grpc.add_OrderQueryServiceServicer_to_server(OrderQueryGrpcService(), server)
  health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

  server.add_insecure_port(f"{settings.grpc_host}:{settings.grpc_port}")
  await server.start()

  await health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
  await health_servicer.set(_SERVICE_NAME, health_pb2.HealthCheckResponse.SERVING)
  return server, health_servicer


async def stop_grpc_server(
  server: grpc.aio.Server,
  health_servicer: health.HealthServicer,
) -> None:
  await health_servicer.set(_SERVICE_NAME, health_pb2.HealthCheckResponse.NOT_SERVING)
  await health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)
  await server.stop(grace=5)
