import uvicorn
from fastapi import FastAPI
from core.config import settings

from api.health import router as health_router
from api.cart import router as cart_router
from api.orders import router as orders_router
from api.management import router as management_router

def get_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="Order Service API - Сервис управления заказами"
    )

    app.include_router(health_router)
    app.include_router(cart_router)
    app.include_router(orders_router)
    app.include_router(management_router)

    return app

app = get_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
