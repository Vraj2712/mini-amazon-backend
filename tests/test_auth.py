import pytest

@pytest.mark.anyio
async def test_get_current_user_invalid_token(async_client):
    response = await async_client.get("/orders/", headers={
        "Authorization": "Bearer invalidtoken"
    }, follow_redirects=True)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.anyio
async def test_admin_access_denied(async_client):
    # Login as regular user
    login_resp = await async_client.post("/auth/login", data={
        "username": "pytest@example.com",
        "password": "testpass"
    }, follow_redirects=True)
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to update a fake order
    response = await async_client.put(
        "/orders/000000000000000000000000/status",  # fake ObjectId
        json={"status": "shipped"},
        headers=headers,
        follow_redirects=True
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admins only"  # ✅ match the real message
