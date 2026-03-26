from fastapi import APIRouter

from api import health
from api.v1 import v1_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(v1_router)
