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
