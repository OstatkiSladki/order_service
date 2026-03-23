from fastapi import APIRouter, Depends, Header, HTTPException, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from models.order import Order as OrderModel, OrderStatus

router = APIRouter(tags=["Management"])

class StatusUpdate(BaseModel):
    status: str
    pickup_code: str = None

@router.patch("/api/v1/management/orders/{order_id}/status")
def update_status(
    body: StatusUpdate,
    order_id: int = Path(...),
    x_user_id: str = Header(...),
    x_user_role: str = Header(...),
    x_user_venue_id: int = Header(...),
    db: Session = Depends(get_db)
):
    if x_user_role not in ["staff", "admin"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if x_user_role == "staff" and int(x_user_venue_id) != order.venue_id:
        raise HTTPException(status_code=403, detail="Forbidden venue")
        
    if body.status == "picked_up":
        if not body.pickup_code or body.pickup_code != order.pickup_code:
            raise HTTPException(status_code=403, detail="Invalid pickup code")
            
    try:
        order.status = OrderStatus[body.status]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    db.commit()
    return {"message": "Status updated successfully"}
