# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

pytestmark = pytest.mark.asyncio(scope="function")
# Ensure consistent use of asyncio as the event loop backend
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
