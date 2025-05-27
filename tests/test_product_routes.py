import pytest
from bson.errors import InvalidId
from bson import ObjectId

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

@pytest.mark.anyio
async def test_update_product_partial(async_client, admin_token, create_product):
    product_id = create_product["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    response = await async_client.put(f"/products/{product_id}", json={
        "price": 999.99
    }, headers=headers)

    print(response.status_code)
    print(response.json())  # <- This shows the exact error returned by FastAPI

    assert response.status_code == 200
    assert response.json()["price"] == 999.99


@pytest.mark.anyio
async def test_delete_product_not_found(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.delete("/products/000000000000000000000000", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

@pytest.mark.anyio
async def test_get_product_by_invalid_id(async_client):
    response = await async_client.get("/products/invalid_id")
    assert response.status_code == 400

@pytest.mark.anyio
async def test_get_product_by_invalid_id(async_client):
    response = await async_client.get("/products/invalid_id")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid product ID format"

@pytest.mark.anyio
async def test_update_nonexistent_product(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_id = str(ObjectId())
    response = await async_client.put(f"/products/{fake_id}", json={
        "price": 10.99
    }, headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not updated"

@pytest.mark.anyio
async def test_delete_nonexistent_product(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    fake_id = str(ObjectId())
    response = await async_client.delete(f"/products/{fake_id}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

@pytest.mark.anyio
async def test_search_products_no_results(async_client):
    response = await async_client.get("/products/search?q=nonexistent12345")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_search_products_price_filter(async_client, create_product):
    price = create_product["price"]
    high_price = price + 1_000_000  # use a price way beyond existing ones
    response = await async_client.get(f"/products/search?min_price={high_price}")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_search_products_with_multiple_filters(async_client, create_product):
    # Using known values from create_product
    name = create_product["name"]
    price = create_product["price"]

    response = await async_client.get(f"/products/search?q={name}&min_price={price-1}&max_price={price+1}&in_stock=true")
    assert response.status_code == 200
    results = response.json()
    assert any(prod["id"] == create_product["id"] for prod in results)

@pytest.mark.anyio
async def test_update_product_no_change(async_client, admin_token, create_product):
    product_id = create_product["id"]
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Send the same data (no actual update)
    response = await async_client.put(f"/products/{product_id}", json={
        "name": create_product["name"],
        "description": create_product["description"],
        "price": create_product["price"],
        "in_stock": create_product["in_stock"]
    }, headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not updated"

@pytest.mark.anyio
async def test_get_current_user_info(async_client):
    await async_client.post("/auth/signup", json={
        "name": "Coverage User",
        "email": "cov@example.com",
        "password": "pass"
    })
    login = await async_client.post("/auth/login", data={
        "username": "cov@example.com",
        "password": "pass"
    })
    token = login.json()["access_token"]
    response = await async_client.get("/auth/user", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "cov@example.com"
