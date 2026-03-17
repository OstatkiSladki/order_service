from repositories.cart import cart_repo
from datetime import datetime, timezone
from schemas.cart import CartItem

class CartService:
    def __init__(self):
        self.repo = cart_repo

    def get_cart(self, user_id: str) -> dict:
        return self.repo.get_by_user_id(user_id)

    def clear_cart(self, user_id: str):
        self.repo.delete(user_id)

    def add_item(self, user_id: str, item: CartItem) -> dict:
        cart_data = self.repo.get_by_user_id(user_id)
        existing_item = next((i for i in cart_data["items"] if i["offer_id"] == item.offer_id), None)
        if existing_item:
            existing_item["quantity"] += item.quantity
        else:
            cart_data["items"].append(item.model_dump())
        cart_data["updated_at"] = datetime.now(timezone.utc)
        return self.repo.save(user_id, cart_data)

cart_service = CartService()
