from repositories.order import OrderRepository
from services.cart import cart_service
import random
from datetime import datetime, timezone, timedelta
from schemas.order import OrderStatus, OrderItem

class OrderService:
    def __init__(self):
        self.repo = OrderRepository()
        
    def checkout_cart(self, user_id: str) -> dict:
        cart_data = cart_service.get_cart(user_id)
        if not cart_data.get("items"):
            raise ValueError("Корзина пуста")
            
        try:
            uid = int(user_id)
        except ValueError:
            uid = 1
            
        total_amount = 0.0
        order_items = []
        for item in cart_data["items"]:
            price = 100.0  # TODO: Call Catalog Service via RPC
            qty = item["quantity"]
            subtotal = price * qty
            total_amount += subtotal
            
            order_items.append(
                OrderItem(
                    offer_id=item["offer_id"],
                    product_name_snapshot=f"Товар #{item['offer_id']}",
                    price_snapshot=price,
                    quantity=qty,
                    subtotal=subtotal
                ).model_dump()
            )
            
        service_fee = 10.0
        final_amount = total_amount + service_fee
        now = datetime.now(timezone.utc)
        pickup_code_val = str(random.randint(100000, 999999))
        
        new_order_data = {
            "user_id": uid,
            "venue_id": cart_data.get("venue_id") or 1,
            "status": OrderStatus.created.value,
            "total_amount": total_amount,
            "service_fee": service_fee,
            "venue_payout": final_amount - service_fee,
            "final_amount": final_amount,
            "created_at": now,
            "updated_at": now,
            "items": order_items,
            "_pickup_code": pickup_code_val
        }
        
        created_order = self.repo.create(new_order_data)
        
        # Очищаем корзину через сервис
        cart_service.clear_cart(user_id)
        
        return created_order

    def update_to_picked_up(self, order_id: int, provided_code: str) -> dict:
        order = self.repo.get_by_id(order_id)
        if not order:
            raise KeyError("Заказ не найден")
            
        if order.get("_pickup_code") != provided_code:
            raise PermissionError("Неверный pickup_code. Выдача заказа запрещена.")
                                                                                    
        updated = self.repo.update_status(order_id, "picked_up")
        return updated
        
order_service = OrderService()
