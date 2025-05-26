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

@pytest.mark.anyio
async def test_place_order_without_cart(async_client):
    await async_client.post("/auth/signup", json={
        "name": "No Cart User",
        "email": "nocart@example.com",
        "password": "pass"
    })
    login = await async_client.post("/auth/login", data={
        "username": "nocart@example.com",
        "password": "pass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post("/orders/", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] in ["Cart not found", "Cart is empty"]

@pytest.mark.anyio
async def test_place_order_with_invalid_product(async_client):
    await async_client.post("/auth/signup", json={
        "name": "Invalid Product User",
        "email": "invalidproduct@example.com",
        "password": "pass"
    })
    login = await async_client.post("/auth/login", data={
        "username": "invalidproduct@example.com",
        "password": "pass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await async_client.post("/cart/add", json={
        "product_id": "000000000000000000000000",  # fake ObjectId
        "quantity": 1
    }, headers=headers)

    response = await async_client.post("/orders/", headers=headers)
    assert response.status_code == 404
    assert "Product" in response.json()["detail"]

@pytest.mark.anyio
async def test_non_admin_cannot_update_order(async_client):
    await async_client.post("/auth/signup", json={
        "name": "Not Admin",
        "email": "usernotadmin@example.com",
        "password": "pass"
    })
    login = await async_client.post("/auth/login", data={
        "username": "usernotadmin@example.com",
        "password": "pass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.put("/orders/replace_this_with_real_order_id/status", json={
        "status": "shipped"
    }, headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Admins only"

@pytest.mark.anyio
async def test_update_order_invalid_status(async_client):
    # Step 1: Login as admin
    admin_login = await async_client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "adminpass"
    })
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Login as user
    await async_client.post("/auth/signup", json={
        "name": "UserForInvalidStatusTest",
        "email": "invalidstatus@example.com",
        "password": "userpass"
    })
    user_login = await async_client.post("/auth/login", data={
        "username": "invalidstatus@example.com",
        "password": "userpass"
    })
    user_token = user_login.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Step 3: Create a product
    prod_resp = await async_client.post("/products/", json={
        "name": "Invalid Status Product",
        "description": "Testing invalid status",
        "price": 10.0,
        "in_stock": True
    }, headers=user_headers)
    product_id = prod_resp.json()["id"]

    # Step 4: Add to cart
    await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=user_headers)

    # Step 5: Place an order
    order_resp = await async_client.post("/orders/", headers=user_headers)
    order_id = order_resp.json()["id"]

    # Step 6: Try updating to an invalid status
    response = await async_client.put(f"/orders/{order_id}/status", json={
        "status": "notastatus"
    }, headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid status value"

