from typing import Dict, Any, List, Optional

# Наш In-Memory справочник
FAKEDB_ORDERS: Dict[int, Dict[str, Any]] = {}

class OrderRepository:
    def create(self, order_data: dict) -> dict:
        order_id = len(FAKEDB_ORDERS) + 1
        order_data["id"] = order_id
        FAKEDB_ORDERS[order_id] = order_data
        return order_data
        
    def get_by_id(self, order_id: int) -> Optional[dict]:
        return FAKEDB_ORDERS.get(order_id)
        
    def get_by_user_id(self, user_id: int, status: Optional[str] = None) -> List[dict]:
        orders = [o for o in FAKEDB_ORDERS.values() if o["user_id"] == user_id]
        if status:
            return [o for o in orders if o["status"] == status]
        return orders
        
    def update_status(self, order_id: int, status: str) -> Optional[dict]:
        if order_id in FAKEDB_ORDERS:
            FAKEDB_ORDERS[order_id]["status"] = status
            return FAKEDB_ORDERS[order_id]
        return None
