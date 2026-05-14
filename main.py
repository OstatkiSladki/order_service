import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import api_router
from core.config import get_settings
from core.database import close_engine
from rpc.catalog_client import CatalogInventoryClient
from rpc.server import start_grpc_server, stop_grpc_server

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
  catalog_inventory_client = CatalogInventoryClient()
  app.state.catalog_inventory_client = catalog_inventory_client

  grpc_server, grpc_health = await start_grpc_server()
  app.state.grpc_server = grpc_server
  app.state.grpc_health = grpc_health

  if settings.grpc_startup_checks_enabled:
    try:
      await catalog_inventory_client.wait_until_serving()
    except Exception as exc:
      logger.warning(
        "gRPC startup health check failed for catalog-inventory: %s; continuing with lazy reconnect",
        exc,
      )
  try:
    yield
  finally:
    await stop_grpc_server(grpc_server, grpc_health)
    await catalog_inventory_client.close()
    await close_engine()


def create_app() -> FastAPI:
  app = FastAPI(
    title="Order Service",
    version="1.0.0",
    debug=settings.app_debug,
    root_path=settings.app_root_path,
    lifespan=lifespan,
  )
  app.include_router(api_router)
  return app


app = create_app()

if __name__ == "__main__":
  uvicorn.run(
    app,
    host=settings.app_host,
    port=settings.app_port,
    log_level=settings.log_level.lower(),
  )
