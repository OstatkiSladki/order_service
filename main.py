from fastapi import FastAPI
from core.database import engine, Base

from api.health import router as health_router
from api.cart import router as cart_router
from api.orders import router as orders_router
from api.management import router as management_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Service",
    version="1.2.0"
)

app.include_router(health_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(management_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
