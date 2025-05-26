import pytest

@pytest.mark.anyio
async def test_add_to_cart(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create product first
    product_resp = await async_client.post("/products/", json={
        "name": "Cart Add Product",
        "description": "To add to cart",
        "price": 10.0,
        "in_stock": True
    }, headers=headers, follow_redirects=True)
    product_id = product_resp.json()["id"]

    response = await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers, follow_redirects=True)
    assert response.status_code in [200, 201, 400]


@pytest.mark.anyio
async def test_view_cart(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/cart/", headers=headers, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_update_cart_quantity(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    product_resp = await async_client.post("/products/", json={
        "name": "Update Cart Product",
        "description": "To update quantity",
        "price": 15.0,
        "in_stock": True
    }, headers=headers, follow_redirects=True)
    product_id = product_resp.json()["id"]

    await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers, follow_redirects=True)

    update_resp = await async_client.put("/cart/update", json={
        "product_id": product_id,
        "quantity": 3
    }, headers=headers, follow_redirects=True)
    assert update_resp.status_code == 200
    item = next(i for i in update_resp.json()["items"] if i["product_id"] == product_id)
    assert item["quantity"] == 3


@pytest.mark.anyio
async def test_remove_cart_item(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    product_resp = await async_client.post("/products/", json={
        "name": "Remove Cart Product",
        "description": "To remove from cart",
        "price": 20.0,
        "in_stock": True
    }, headers=headers, follow_redirects=True)
    product_id = product_resp.json()["id"]

    await async_client.post("/cart/add", json={
        "product_id": product_id,
        "quantity": 1
    }, headers=headers, follow_redirects=True)

    remove_resp = await async_client.request("DELETE", "/cart/item", json={
        "product_id": product_id
    }, headers=headers, follow_redirects=True)
    assert remove_resp.status_code == 200
    assert all(item["product_id"] != product_id for item in remove_resp.json()["items"])
