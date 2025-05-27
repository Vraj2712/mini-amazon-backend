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

@pytest.mark.anyio
async def test_signup_existing_email(async_client):
    # First signup
    await async_client.post("/auth/signup", json={
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "pass123"
    })

    # Try signing up again with the same email
    response = await async_client.post("/auth/signup", json={
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "pass123"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.anyio
async def test_login_with_wrong_password(async_client):
    # Create user
    await async_client.post("/auth/signup", json={
        "name": "WrongPass User",
        "email": "wrongpass@example.com",
        "password": "correctpass"
    })

    # Attempt login with incorrect password
    response = await async_client.post("/auth/login", data={
        "username": "wrongpass@example.com",
        "password": "wrongpass"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.anyio
async def test_login_with_nonexistent_email(async_client):
    response = await async_client.post("/auth/login", data={
        "username": "notfound@example.com",
        "password": "irrelevant"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.anyio
async def test_get_current_user_valid_token(async_client):
    # Sign up and login
    await async_client.post("/auth/signup", json={
        "name": "Current User",
        "email": "currentuser@example.com",
        "password": "mypassword"
    })

    login_resp = await async_client.post("/auth/login", data={
        "username": "currentuser@example.com",
        "password": "mypassword"
    })
    token = login_resp.json()["access_token"]

    # Use token to call /auth/user
    response = await async_client.get("/auth/user", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json()["email"] == "currentuser@example.com"

@pytest.mark.anyio
async def test_login_with_missing_fields(async_client):
    response = await async_client.post("/auth/login", data={
        "username": "user@example.com"
        # password missing
    })
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.anyio
async def test_login_with_get_method_not_allowed(async_client):
    response = await async_client.get("/auth/login")
    assert response.status_code == 405  # Method Not Allowed

@pytest.mark.anyio
async def test_get_current_user_without_token(async_client):
    response = await async_client.get("/auth/user")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.anyio
async def test_get_current_user_info(async_client):
    # Sign up
    await async_client.post("/auth/signup", json={
        "name": "Get User",
        "email": "getuser@example.com",
        "password": "password123"
    })

    # Login
    login_resp = await async_client.post("/auth/login", data={
        "username": "getuser@example.com",
        "password": "password123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Call /auth/user
    resp = await async_client.get("/auth/user", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "getuser@example.com"

@pytest.mark.anyio
async def test_get_current_user_user_not_found(async_client):
    await async_client.post("/auth/signup", json={
        "name": "Ghost User",
        "email": "ghost@example.com",
        "password": "ghostpass"
    })
    login = await async_client.post("/auth/login", data={
        "username": "ghost@example.com",
        "password": "ghostpass"
    })
    token = login.json()["access_token"]

    # Delete user manually
    from app.database import db
    await db.users.delete_one({"email": "ghost@example.com"})

    response = await async_client.get("/auth/user", headers={
        "Authorization": f"Bearer {token}"
    })

    # Updated expected status
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
