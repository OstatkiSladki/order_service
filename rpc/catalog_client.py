def get_offer_info(offer_id: int) -> dict:
    """Mock RPC call to Catalog Service"""
    # Just a stable mock: venue_id is derived from offer_id 
    # e.g., 10-19 belongs to venue 1, 20-29 belongs to venue 2 
    venue_id = (offer_id // 10)
    if venue_id == 0:
        venue_id = 1
        
    return {
        "offer_id": offer_id,
        "venue_id": venue_id,
        "product_name": f"Item {offer_id}",
        "price": float(offer_id * 100.0)
    }
