import pytest
from app.auth.utils import hash_password, verify_password, create_access_token, decode_access_token

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
