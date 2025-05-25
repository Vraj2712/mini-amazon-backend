import pytest

@pytest.mark.anyio
async def test_add_to_cart(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Replace this with a valid product ID that exists in your DB
    product_id = "6831d5a60fccd45a894b5b7a"

    response = await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers)
    assert response.status_code in [200, 400]

@pytest.mark.anyio
async def test_view_cart(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/cart/", headers=headers)
    assert response.status_code == 200

@pytest.mark.anyio
async def test_update_cart_quantity(async_client):
    # Step 1: Login
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create product
    product_resp = await async_client.post("/products/", json={
        "name": "Update Cart Product",
        "description": "To update quantity",
        "price": 15.0,
        "in_stock": True
    }, headers=headers, follow_redirects=True)
    product_id = product_resp.json()["id"]

    # Step 3: Add to cart
    add_resp = await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers, follow_redirects=True)
    assert add_resp.status_code in [200, 201]

    # Step 4: Update quantity
    update_resp = await async_client.put("/cart/update", json={
        "product_id": product_id,
        "quantity": 3
    }, headers=headers, follow_redirects=True)
    assert update_resp.status_code == 200

    updated_cart = update_resp.json()
    item = next((i for i in updated_cart["items"] if i["product_id"] == product_id), None)
    assert item and item["quantity"] == 3

    # tests/test_cart.py

@pytest.mark.anyio
async def test_remove_cart_item(async_client):
    # Step 1: Login
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create product
    product_resp = await async_client.post("/products/", json={
        "name": "Remove Cart Product",
        "description": "To remove from cart",
        "price": 20.0,
        "in_stock": True
    }, headers=headers, follow_redirects=True)
    product_id = product_resp.json()["id"]

    # Step 3: Add to cart
    add_resp = await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers, follow_redirects=True)
    assert add_resp.status_code in [200, 201]

    # Step 4: Remove item
    remove_resp = await async_client.request("DELETE", "/cart/item", json={
        "product_id": product_id
    }, headers=headers, follow_redirects=True)
    assert remove_resp.status_code == 200

    # Step 5: Confirm item is gone
    cart = remove_resp.json()
    assert all(item["product_id"] != product_id for item in cart["items"])
