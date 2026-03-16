from pydantic import BaseModel
from enum import Enum

class ManagementOrderStatusUpdate(str, Enum):
    picked_up = "picked_up"
    cancelled = "cancelled"

class OrderStatusUpdate(BaseModel):
    status: ManagementOrderStatusUpdate
    pickup_code: str
