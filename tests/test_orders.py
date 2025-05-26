import pytest

@pytest.mark.anyio
async def test_user_orders(async_client):
    # Login
    login_response = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get user's orders
    orders_response = await async_client.get("/orders/", headers=headers, follow_redirects=True)
    assert orders_response.status_code == 200

    orders = orders_response.json()
    assert isinstance(orders, list)

@pytest.mark.anyio
async def test_order_status_update_requires_admin(async_client):
    # Create and log in regular user
    await async_client.post("/auth/signup", json={
        "name": "Test Buyer",
        "email": "buyer@example.com",
        "password": "buyerpass"
    }, follow_redirects=True)

    buyer_login = await async_client.post("/auth/login", data={
        "username": "buyer@example.com",
        "password": "buyerpass"
    }, follow_redirects=True)
    token = buyer_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create product
    prod_resp = await async_client.post("/products/", json={
        "name": "UnauthorizedStatusTestProduct",
        "description": "Should not allow status change",
        "price": 20.0,
        "in_stock": True
    }, headers=headers, follow_redirects=True)
    assert prod_resp.status_code in [200, 201]
    product_id = prod_resp.json()["id"]

    # Add to cart
    await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers, follow_redirects=True)

    # Place order
    order_resp = await async_client.post("/orders/", headers=headers, follow_redirects=True)
    order_id = order_resp.json()["id"]

    # Try updating status as non-admin (should fail)
    update_resp = await async_client.put(f"/orders/{order_id}/status", json={
        "status": "shipped"
    }, headers=headers, follow_redirects=True)

    assert update_resp.status_code == 403
    assert update_resp.json()["detail"] == "Admins only"
