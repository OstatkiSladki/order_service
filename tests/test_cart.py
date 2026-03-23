import pytest

def test_get_cart_empty(client, user_headers):
    response = client.get("/api/v1/cart", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []

def test_add_cart_item(client, user_headers):
    payload = {"offer_id": 15, "quantity": 2} # venue_id = 1
    response = client.post("/api/v1/cart/items", json=payload, headers=user_headers)
    assert response.status_code == 201
    
    # Check if item is in cart
    cart_resp = client.get("/api/v1/cart", headers=user_headers)
    assert cart_resp.status_code == 200
    cart_data = cart_resp.json()
    assert len(cart_data["items"]) == 1
    assert cart_data["items"][0]["offer_id"] == 15
    assert cart_data["items"][0]["quantity"] == 2
    assert cart_data["venue_id"] == 1

def test_add_different_venue_fails(client, user_headers):
    # Add offer_id 15 (venue 1) FIRST.
    payload = {"offer_id": 15, "quantity": 1}
    client.post("/api/v1/cart/items", json=payload, headers=user_headers)

    # Now add 25 (venue 2) which should fail.
    payload2 = {"offer_id": 25, "quantity": 1}
    response = client.post("/api/v1/cart/items", json=payload2, headers=user_headers)
    assert response.status_code == 400
    assert "одного заведения" in response.json()["detail"]

def test_add_update_quantity_and_remove(client, user_headers):
    # Seed with 15
    client.post("/api/v1/cart/items", json={"offer_id": 15, "quantity": 2}, headers=user_headers)

    # Update quantity to 5
    payload = {"offer_id": 15, "quantity": 5}
    resp1 = client.post("/api/v1/cart/items", json=payload, headers=user_headers)
    assert resp1.status_code == 200 or resp1.status_code == 201
    
    cart_resp = client.get("/api/v1/cart", headers=user_headers)
    assert cart_resp.json()["items"][0]["quantity"] == 5

    # Remove item by setting quantity to 0
    payload = {"offer_id": 15, "quantity": 0}
    resp2 = client.post("/api/v1/cart/items", json=payload, headers=user_headers)
    
    cart_resp2 = client.get("/api/v1/cart", headers=user_headers)
    assert len(cart_resp2.json()["items"]) == 0

def test_delete_cart(client, user_headers):
    payload = {"offer_id": 15, "quantity": 2}
    client.post("/api/v1/cart/items", json=payload, headers=user_headers)
    
    del_resp = client.delete("/api/v1/cart", headers=user_headers)
    assert del_resp.status_code == 204
    
    cart_resp = client.get("/api/v1/cart", headers=user_headers)
    assert cart_resp.status_code == 200
    cart_data = cart_resp.json()
    assert cart_data["items"] == []
    assert cart_data["venue_id"] is None

def test_add_negative_and_zero_quantity(client, user_headers):
    client.post("/api/v1/cart/items", json={"offer_id": 15, "quantity": -5}, headers=user_headers)
    
    cart_resp = client.get("/api/v1/cart", headers=user_headers)
    assert len(cart_resp.json()["items"]) == 0
