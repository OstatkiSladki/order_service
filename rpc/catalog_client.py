from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from grpc_health.v1 import health_pb2, health_pb2_grpc

from core.config import get_settings
from rpc.generated import catalog_inventory_pb2, catalog_inventory_pb2_grpc

_SERVICE_CONFIG = json.dumps(
  {
    "methodConfig": [
      {
        "name": [{}],
        "retryPolicy": {
          "maxAttempts": 4,
          "initialBackoff": "0.2s",
          "maxBackoff": "2s",
          "backoffMultiplier": 2,
          "retryableStatusCodes": ["UNAVAILABLE"],
        },
      }
    ]
  }
)
_CHANNEL_OPTIONS = (
  ("grpc.enable_retries", 1),
  ("grpc.service_config", _SERVICE_CONFIG),
)
_SERVICE_NAME = "ostatki.grpc.v1.CatalogInventoryService"


class CircuitBreakerOpenError(RuntimeError):
  pass


class CatalogGrpcError(RuntimeError):
  pass


class _CircuitBreaker:
  def __init__(self, failure_threshold: int, reset_timeout: float) -> None:
    self._failure_threshold = failure_threshold
    self._reset_timeout = reset_timeout
    self._consecutive_failures = 0
    self._opened_at: float | None = None
    self._state = "closed"

  def before_call(self) -> None:
    if self._state != "open":
      return
    if self._opened_at is not None and (time.monotonic() - self._opened_at) >= self._reset_timeout:
      self._state = "half-open"
      return
    raise CircuitBreakerOpenError("Catalog gRPC circuit breaker is open")

  def record_success(self) -> None:
    self._consecutive_failures = 0
    self._opened_at = None
    self._state = "closed"

  def record_failure(self) -> None:
    if self._state == "half-open":
      self._open()
      return
    self._consecutive_failures += 1
    if self._consecutive_failures >= self._failure_threshold:
      self._open()

  def _open(self) -> None:
    self._state = "open"
    self._opened_at = time.monotonic()
    self._consecutive_failures = 0


@dataclass(slots=True)
class OfferSnapshot:
  offer_id: int
  venue_id: int
  product_name: str
  price: Decimal
  is_active: bool


@dataclass(slots=True)
class Reservation:
  reservation_id: str
  expires_at: datetime


class CatalogInventoryClient:
  def __init__(self) -> None:
    settings = get_settings()
    self._timeout = settings.grpc_startup_check_timeout
    self._breaker = _CircuitBreaker(
      settings.grpc_circuit_breaker_failure_threshold,
      settings.grpc_circuit_breaker_reset_timeout,
    )
    target = f"{settings.grpc_catalog_service_host}:{settings.grpc_catalog_service_port}"
    self._channel = grpc.aio.insecure_channel(target, options=_CHANNEL_OPTIONS)
    self._stub = catalog_inventory_pb2_grpc.CatalogInventoryServiceStub(self._channel)
    self._health_stub = health_pb2_grpc.HealthStub(self._channel)

  async def close(self) -> None:
    await self._channel.close()

  async def wait_until_serving(self) -> None:
    try:
      response = await self._health_stub.Check(
        health_pb2.HealthCheckRequest(service=_SERVICE_NAME),
        timeout=self._timeout,
        wait_for_ready=True,
      )
    except grpc.RpcError as exc:
      raise CatalogGrpcError("Catalog gRPC health check failed") from exc
    if response.status != health_pb2.HealthCheckResponse.SERVING:
      raise CatalogGrpcError("Catalog gRPC service is not serving")

  async def get_offer_snapshot(self, offer_id: int) -> OfferSnapshot:
    response = await self._call(
      self._stub.GetOfferSnapshot,
      catalog_inventory_pb2.GetOfferSnapshotRequest(offer_id=offer_id),
    )
    return OfferSnapshot(
      offer_id=int(response.offer_id),
      venue_id=int(response.venue_id),
      product_name=str(response.product_name),
      price=Decimal(response.price),
      is_active=bool(response.is_active),
    )

  async def reserve_items(self, offer_id: int, quantity: int, reservation_owner: int) -> Reservation:
    response = await self._call(
      self._stub.ReserveItems,
      catalog_inventory_pb2.ReserveItemsRequest(
        offer_id=offer_id,
        quantity=quantity,
        reservation_owner=reservation_owner,
      ),
    )
    expires_at = response.expires_at.ToDatetime()
    return Reservation(reservation_id=response.reservation_id, expires_at=expires_at)

  async def confirm_reservation(self, reservation_id: str) -> bool:
    response = await self._call(
      self._stub.ConfirmReservation,
      catalog_inventory_pb2.ConfirmReservationRequest(reservation_id=reservation_id),
    )
    return bool(response.success)

  async def cancel_reservation(self, reservation_id: str) -> bool:
    response = await self._call(
      self._stub.CancelReservation,
      catalog_inventory_pb2.CancelReservationRequest(reservation_id=reservation_id),
    )
    return bool(response.success)

  async def _call(self, func, request):
    self._breaker.before_call()
    try:
      response = await func(request, timeout=self._timeout, wait_for_ready=True)
    except grpc.RpcError as exc:
      self._breaker.record_failure()
      raise exc
    self._breaker.record_success()
    return response
