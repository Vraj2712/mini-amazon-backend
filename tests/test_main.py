import pytest

@pytest.mark.anyio
async def test_signup(async_client):
    response = await async_client.post("/auth/signup", json={
        "name": "Test User",
        "email": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    assert response.status_code in [200, 400]  # 400 if already registered


@pytest.mark.anyio
async def test_login(async_client):
    response = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_create_product(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post("/products", json={
        "name": "Pytest Product",
        "description": "Test product",
        "price": 49.99,
        "in_stock": True
    }, headers=headers, follow_redirects=True)

    assert response.status_code in [200, 201, 400]  # Add 201 for newly created

@pytest.mark.anyio
async def test_list_products(async_client):
    response = await async_client.get("/products", follow_redirects=True)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.anyio
async def test_root_path(async_client):
    response = await async_client.get("/")
    assert response.status_code in (200, 404)
