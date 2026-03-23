import pytest

def test_management_forbidden_role(client, user_headers):
    payload = {"status": "picked_up", "pickup_code": "123456"}
    response = client.patch(
        "/api/v1/management/orders/1/status", 
        json=payload, 
        headers={
            "x-user-id": "1",
            "x-user-role": "customer",
            "x-user-venue-id": "1"
        }
    )
    assert response.status_code == 403

def test_management_order_not_found(client, venue_headers):
    payload = {"status": "picked_up", "pickup_code": "123456"}
    response = client.patch(
        "/api/v1/management/orders/999/status", 
        json=payload, 
        headers={
            "x-user-id": "2",
            "x-user-role": "staff",
            "x-user-venue-id": "1"
        }
    )
    assert response.status_code == 404

def test_management_wrong_venue(client, user_headers):
    client.delete("/api/v1/cart", headers=user_headers)
    client.post("/api/v1/cart/items", json={"offer_id": 15, "quantity": 1}, headers=user_headers) # venue 1
    create_resp = client.post("/api/v1/orders", headers=user_headers)
    order_id = create_resp.json()["id"]

    # staff from venue 2 trying to edit venue 1 order
    payload = {"status": "paid"}
    response = client.patch(
        f"/api/v1/management/orders/{order_id}/status", 
        json=payload, 
        headers={
            "x-user-id": "2",
            "x-user-role": "staff",
            "x-user-venue-id": "2"
        }
    )
    assert response.status_code == 403
    assert "Forbidden venue" in response.json()["detail"]

def test_management_update_status_paid(client, user_headers):
    client.delete("/api/v1/cart", headers=user_headers)
    client.post("/api/v1/cart/items", json={"offer_id": 15, "quantity": 1}, headers=user_headers)
    create_resp = client.post("/api/v1/orders", headers=user_headers)
    order_id = create_resp.json()["id"]

    payload = {"status": "paid"}
    response = client.patch(
        f"/api/v1/management/orders/{order_id}/status", 
        json=payload, 
        headers={
            "x-user-id": "2",
            "x-user-role": "staff",
            "x-user-venue-id": "1"
        }
    )
    assert response.status_code == 200

    # Get code should work now
    code_resp = client.get(f"/api/v1/orders/{order_id}/pickup-code", headers=user_headers)
    assert code_resp.status_code == 200
    real_pickup_code = code_resp.json()["code"]

    # Now update to picked_up with correct code
    payload = {"status": "picked_up", "pickup_code": real_pickup_code}
    response2 = client.patch(
        f"/api/v1/management/orders/{order_id}/status", 
        json=payload, 
        headers={
            "x-user-id": "2",
            "x-user-role": "staff",
            "x-user-venue-id": "1"
        }
    )
    assert response2.status_code == 200

def test_management_invalid_pickup_code(client, user_headers):
    client.delete("/api/v1/cart", headers=user_headers)
    client.post("/api/v1/cart/items", json={"offer_id": 15, "quantity": 1}, headers=user_headers)
    create_resp = client.post("/api/v1/orders", headers=user_headers)
    order_id = create_resp.json()["id"]

    payload = {"status": "picked_up", "pickup_code": "wrong"}
    response = client.patch(
        f"/api/v1/management/orders/{order_id}/status", 
        json=payload, 
        headers={
            "x-user-id": "2",
            "x-user-role": "staff",
            "x-user-venue-id": "1"
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid pickup code"

def test_management_invalid_order_status(client, user_headers):
    client.delete("/api/v1/cart", headers=user_headers)
    client.post("/api/v1/cart/items", json={"offer_id": 15, "quantity": 1}, headers=user_headers)
    create_resp = client.post("/api/v1/orders", headers=user_headers)
    order_id = create_resp.json()["id"]

    # status unexist
    payload = {"status": "non_exist_status"}
    response = client.patch(
        f"/api/v1/management/orders/{order_id}/status", 
        json=payload, 
        headers={
            "x-user-id": "2",
            "x-user-role": "staff",
            "x-user-venue-id": "1"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status"
