import pytest
from app.auth.utils import hash_password, verify_password, create_access_token, decode_access_token
from fastapi import HTTPException
from app.models.user_model import UserResponse
from datetime import datetime

def test_verify_password():
    raw = "mypassword"
    hashed = hash_password(raw)
    assert verify_password(raw, hashed)
    assert not verify_password("wrongpass", hashed)

def test_create_and_decode_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"

@pytest.mark.anyio
async def test_protected_route_with_invalid_token(async_client):
    # Use a clearly invalid JWT token
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    response = await async_client.get("/auth/user", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.anyio
async def test_protected_route_with_invalid_token(async_client):
    headers = {"Authorization": "Bearer this.is.not.valid"}
    response = await async_client.get("/auth/user", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
