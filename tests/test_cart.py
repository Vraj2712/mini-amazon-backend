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
