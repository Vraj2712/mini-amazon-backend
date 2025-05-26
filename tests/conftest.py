# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

pytestmark = pytest.mark.asyncio(scope="function")
# Ensure consistent use of asyncio as the event loop backend
@pytest.fixture
async def admin_token(async_client: AsyncClient):
    await async_client.post("/auth/signup", json={
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "adminpass"
    })
    login_resp = await async_client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "adminpass"
    })
    return login_resp.json()["access_token"]

@pytest.fixture
async def create_product(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.post("/products/", json={
        "name": "PartialUpdateProduct",
        "description": "Initial description",
        "price": 100.0,
        "in_stock": True
    }, headers=headers)
    return resp.json()

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

# Use session-scoped AsyncClient to avoid loop reuse errors
@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
