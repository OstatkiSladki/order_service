from datetime import datetime, timezone
from typing import Dict, Any

class CartRepository:
    def __init__(self):
        self.db: Dict[str, Dict[str, Any]] = {}

    def get_by_user_id(self, user_id: str) -> dict:
        if user_id not in self.db:
            self.db[user_id] = {
                "id": len(self.db) + 1,
                "venue_id": None,
                "items": [],
                "updated_at": datetime.now(timezone.utc)
            }
        return self.db[user_id]

    def delete(self, user_id: str):
        if user_id in self.db:
            del self.db[user_id]

    def save(self, user_id: str, cart_data: dict) -> dict:
        self.db[user_id] = cart_data
        return cart_data

# Временная глобальная база
cart_repo = CartRepository()
