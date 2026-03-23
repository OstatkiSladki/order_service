from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from schemas.cart import Cart, CartItemCreate
from models.cart import Cart as CartModel, CartItem as CartItemModel
from rpc.catalog_client import get_offer_info

router = APIRouter(tags=["Carts"])

@router.get("/api/v1/cart", response_model=Cart)
def get_cart(x_user_id: str = Header(...), db: Session = Depends(get_db)):
    cart = db.query(CartModel).filter(CartModel.user_id == int(x_user_id)).first()
    if not cart:
        cart = CartModel(user_id=int(x_user_id))
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

@router.delete("/api/v1/cart", status_code=204)
def clear_cart(x_user_id: str = Header(...), db: Session = Depends(get_db)):
    cart = db.query(CartModel).filter(CartModel.user_id == int(x_user_id)).first()
    if cart:
        db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id).delete()
        cart.venue_id = None
        db.commit()
    return None

@router.post("/api/v1/cart/items", status_code=201)
def add_cart_item(item: CartItemCreate, x_user_id: str = Header(...), db: Session = Depends(get_db)):
    offer_info = get_offer_info(item.offer_id)
    if not offer_info:
        raise HTTPException(status_code=404, detail="Offer not found")

    cart = db.query(CartModel).filter(CartModel.user_id == int(x_user_id)).first()
    if not cart:
        cart = CartModel(user_id=int(x_user_id))
        db.add(cart)
        db.commit()
        db.refresh(cart)
        
    if cart.venue_id is not None and cart.venue_id != offer_info["venue_id"]:
        if db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id).count() > 0:
            raise HTTPException(status_code=400, detail="Одна корзина может содержать товары только из одного заведения")
        else:
            cart.venue_id = offer_info["venue_id"]
    elif cart.venue_id is None:
        cart.venue_id = offer_info["venue_id"]
        
    if item.quantity <= 0:
        db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id, CartItemModel.offer_id == item.offer_id).delete()
        db.commit()
        return {"message": "item removed"}
    
    existing_item = db.query(CartItemModel).filter(CartItemModel.cart_id == cart.id, CartItemModel.offer_id == item.offer_id).first()
    if existing_item:
        existing_item.quantity = item.quantity
    else:
        new_item = CartItemModel(cart_id=cart.id, offer_id=item.offer_id, quantity=item.quantity)
        db.add(new_item)
        
    db.commit()
    return {"message": "item added/updated"}
