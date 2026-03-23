import pytest

def setup_cart_for_order(client, headers):
    client.delete("/api/v1/cart", headers=headers)
    payload = {"offer_id": 15, "quantity": 2} # price 1500, amount 3000
    client.post("/api/v1/cart/items", json=payload, headers=headers)

def test_get_orders_empty(client, user_headers):
    response = client.get("/api/v1/orders", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_count"] == 0

def test_create_order_empty_cart_fails(client, user_headers):
    client.delete("/api/v1/cart", headers=user_headers)
    response = client.post("/api/v1/orders", headers=user_headers)
    assert response.status_code == 400
    assert "Cart is empty" in response.json()["detail"]

def test_create_order(client, user_headers):
    setup_cart_for_order(client, user_headers)
    
    response = client.post("/api/v1/orders", headers=user_headers)
    assert response.status_code == 201
    data = response.json()
    
    assert data["user_id"] == 1
    assert data["venue_id"] == 1
    assert data["status"] == "created"
    assert data["total_amount"] == 3000.0 # 2 * 15 * 100
    assert len(data["items"]) == 1
    assert data["items"][0]["offer_id"] == 15
    assert data["items"][0]["price_snapshot"] == 1500.0
    
    # Check cart is empty now
    cart_resp = client.get("/api/v1/cart", headers=user_headers)
    assert cart_resp.json()["items"] == []
    assert cart_resp.json()["venue_id"] is None

def test_get_order_by_id(client, user_headers):
    setup_cart_for_order(client, user_headers)
    create_resp = client.post("/api/v1/orders", headers=user_headers)
    order_id = create_resp.json()["id"]
    
    get_resp = client.get(f"/api/v1/orders/{order_id}", headers=user_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == order_id
    assert get_resp.json()["total_amount"] == 3000.0

def test_get_order_not_found(client, user_headers):
    response = client.get("/api/v1/orders/99999", headers=user_headers)
    assert response.status_code == 404

def test_get_pickup_code_not_paid(client, user_headers):
    setup_cart_for_order(client, user_headers)
    create_resp = client.post("/api/v1/orders", headers=user_headers)
    order_id = create_resp.json()["id"]
    
    response = client.get(f"/api/v1/orders/{order_id}/pickup-code", headers=user_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Order not paid yet"

def test_order_pagination_and_status_filtering(client, user_headers):
    # Create 3 orders
    for _ in range(3):
        setup_cart_for_order(client, user_headers)
        client.post("/api/v1/orders", headers=user_headers)
        
    # Get all 3 orders
    response = client.get("/api/v1/orders", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["total_count"] == 3
    assert len(response.json()["items"]) == 3
    
    # Test limits limit = 2
    response_limited = client.get("/api/v1/orders?limit=2&page=1", headers=user_headers)
    assert response_limited.status_code == 200
    assert len(response_limited.json()["items"]) == 2
    
    # Test query by status that shouldn't exist ('paid')
    response_filtered = client.get("/api/v1/orders?status=paid", headers=user_headers)
    assert response_filtered.status_code == 200
    assert response_filtered.json()["total_count"] == 0

def test_missing_x_user_id_headers_fail(client):
    response = client.get("/api/v1/orders")
    assert response.status_code == 422 # missing header validation failure
