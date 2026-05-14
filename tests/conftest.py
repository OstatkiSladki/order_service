import asyncio
import os
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ.setdefault("GRPC_STARTUP_CHECKS_ENABLED", "false")

from dependency import get_db_session
from main import app
from core.database import Base

# Import models so Base.metadata knows about them
import models.cart
import models.order

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test_orders.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def _create_all() -> None:
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


async def _drop_all() -> None:
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)


async def override_get_db_session():
  async with TestingSessionLocal() as db:
    yield db


app.dependency_overrides[get_db_session] = override_get_db_session


class FakeCatalogInventoryClient:
  def __init__(self) -> None:
    self.cancelled_reservations: list[str] = []

  async def wait_until_serving(self) -> None:
    return None

  async def close(self) -> None:
    return None

  async def get_offer_snapshot(self, offer_id: int):
    venue_id = offer_id // 10 or 1
    return SimpleNamespace(
      offer_id=offer_id,
      venue_id=venue_id,
      product_name=f"Item {offer_id}",
      price=Decimal(str(offer_id * 100.0)),
      is_active=True,
    )

  async def reserve_items(self, offer_id: int, quantity: int, reservation_owner: int):
    return SimpleNamespace(
      reservation_id=f"reservation-{offer_id}-{reservation_owner}-{quantity}",
      expires_at=None,
    )

  async def confirm_reservation(self, reservation_id: str) -> bool:
    return True

  async def cancel_reservation(self, reservation_id: str) -> bool:
    self.cancelled_reservations.append(reservation_id)
    return True


@pytest.fixture(scope="session", autouse=True)
def setup_database():
  asyncio.run(_create_all())
  yield
  asyncio.run(_drop_all())


@pytest.fixture(scope="function", autouse=True)
def wipe_database():
  asyncio.run(_drop_all())
  asyncio.run(_create_all())
  yield


@pytest.fixture(scope="module")
def client() -> TestClient:
  with TestClient(app) as c:
    app.state.catalog_inventory_client = FakeCatalogInventoryClient()
    yield c


@pytest.fixture
def user_headers():
  return {
    "x-user-id": "1",
    "x-user-role": "customer",
  }


@pytest.fixture
def venue_headers():
  return {
    "x-user-id": "2",
    "x-user-role": "staff",
    "x-user-venue-id": "1",
  }
