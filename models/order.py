from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone
import enum

def utc_now():
    return datetime.now(timezone.utc)

class OrderStatus(str, enum.Enum):
    created = 'created'
    paid = 'paid'
    picked_up = 'picked_up'
    cancelled = 'cancelled'

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    venue_id = Column(Integer, index=True)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.created)
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    service_fee = Column(Float, default=0.0)
    venue_payout = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)
    promo_code_id = Column(Integer, nullable=True)
    pickup_time = Column(DateTime, nullable=True)
    pickup_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    offer_id = Column(Integer, index=True)
    product_name_snapshot = Column(String)
    price_snapshot = Column(Float)
    quantity = Column(Integer)
    subtotal = Column(Float)
    order = relationship("Order", back_populates="items")
