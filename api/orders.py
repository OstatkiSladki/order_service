from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import secrets
from core.database import get_db
from schemas.order import Order, OrderListResponse, PickupCode
from models.order import Order as OrderModel, OrderItem as OrderItemModel, OrderStatus
from models.cart import Cart as CartModel, CartItem as CartItemModel
from rpc.catalog_client import get_offer_info

router = APIRouter(tags=["Orders"])

def generate_pickup_code() -> str:
    # Use secrets for cryptographically secure 6-digit string
    return str(secrets.randbelow(900000) + 100000)

@router.get("/api/v1/orders", response_model=OrderListResponse)
def get_orders(
    status: Optional[str] = None, 
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100), 
    x_user_id: str = Header(...), 
    db: Session = Depends(get_db)
):
    query = db.query(OrderModel).filter(OrderModel.user_id == int(x_user_id))
    if status:
        query = query.filter(OrderModel.status == status)
    
    total_count = query.count()
    orders = query.offset((page - 1) * limit).limit(limit).all()
    
    return OrderListResponse(items=orders, total_count=total_count, page=page, limit=limit)

@router.post("/api/v1/orders", status_code=201, response_model=Order)
def create_order(x_user_id: str = Header(...), db: Session = Depends(get_db)):
    cart = db.query(CartModel).filter(CartModel.user_id == int(x_user_id)).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    new_order = OrderModel(
        user_id=int(x_user_id), 
        venue_id=cart.venue_id, 
        status=OrderStatus.created,
        pickup_code=generate_pickup_code()
    )
    db.add(new_order)
    db.flush()
    
    total_amount = 0.0
    for item in cart.items:
        offer_info = get_offer_info(item.offer_id)
        subtotal = item.quantity * offer_info["price"]
        total_amount += subtotal
        
        order_item = OrderItemModel(
            order_id=new_order.id,
            offer_id=item.offer_id,
            product_name_snapshot=offer_info["product_name"],
            price_snapshot=offer_info["price"],
            quantity=item.quantity,
            subtotal=subtotal
        )
        db.add(order_item)
        
    new_order.total_amount = total_amount
    new_order.final_amount = total_amount
    new_order.service_fee = total_amount * 0.1
    new_order.venue_payout = total_amount * 0.9
    
    # Clear user's cart
    db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id).delete()
    cart.venue_id = None
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/api/v1/orders/{order_id}", response_model=Order)
def get_order(order_id: int, x_user_id: str = Header(...), db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == int(x_user_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/api/v1/orders/{order_id}/pickup-code", response_model=PickupCode)
def get_pickup_code(order_id: int, x_user_id: str = Header(...), db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id, OrderModel.user_id == int(x_user_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.paid:
        raise HTTPException(status_code=403, detail="Order not paid yet")
    
    return PickupCode(code=order.pickup_code, expires_at=order.updated_at)
