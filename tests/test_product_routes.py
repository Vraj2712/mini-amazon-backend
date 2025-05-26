import pytest

@pytest.mark.anyio
async def test_get_product_by_id(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/products/", json={
        "name": "Test Product Fetch",
        "description": "Test get by id",
        "price": 10.0,
        "in_stock": True
    }, headers=headers)
    assert create_resp.status_code in [200, 201]
    product_id = create_resp.json()["id"]

    get_resp = await async_client.get(f"/products/{product_id}", headers=headers)
    assert create_resp.status_code in [200, 201]
    assert get_resp.json()["id"] == product_id


@pytest.mark.anyio
async def test_update_product(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/products/", json={
        "name": "Product to Update",
        "description": "Original desc",
        "price": 15.0,
        "in_stock": True
    }, headers=headers)
    assert create_resp.status_code in [200, 201]
    product_id = create_resp.json()["id"]

    update_resp = await async_client.put(f"/products/{product_id}", json={
        "name": "Updated Product",
        "description": "Updated desc",
        "price": 20.0,
        "in_stock": False
    }, headers=headers)
    assert create_resp.status_code in [200, 201]
    assert update_resp.json()["name"] == "Updated Product"


@pytest.mark.anyio
async def test_delete_product(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/products/", json={
        "name": "Product to Delete",
        "description": "To be deleted",
        "price": 9.0,
        "in_stock": True
    }, headers=headers)
    assert create_resp.status_code in [200, 201]
    product_id = create_resp.json()["id"]

    delete_resp = await async_client.delete(f"/products/{product_id}", headers=headers)
    assert create_resp.status_code in [200, 201]
