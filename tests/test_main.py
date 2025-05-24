import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport  # 👈 Needed explicitly
from app.main import app
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import db  # Your MongoDB client instance

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.anyio
async def test_signup(async_client):
    response = await async_client.post("/auth/signup", json={
        "name": "Test User",
        "email": "pytest@example.com",
        "password": "testpass"
    })
    assert response.status_code in [200, 400]

@pytest.mark.anyio
async def test_login(async_client):
    response = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.anyio
async def test_create_product(async_client):
    login = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    })
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.post("/products", json={
    "name": "Pytest Product",
    "description": "Test product",
    "price": 49.99,
    "in_stock": True
}, headers=headers, follow_redirects=True) 


@pytest.mark.anyio
async def test_list_products(async_client):
    response = await async_client.get("/products", follow_redirects=True)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
