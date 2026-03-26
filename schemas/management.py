from pydantic import BaseModel


class OrderStatusUpdate(BaseModel):
  status: str
  pickup_code: str | None = None
