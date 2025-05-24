from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models.user_model import UserResponse  # Adjust path if needed
from app.auth.utils import SECRET_KEY, ALGORITHM  # We already used these
from app.database import db  # If you're using Motor or another DB instance
from app.models.user_model import UserResponse
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db["users"].find_one({"email": user_email})
    if user is None:
        raise credentials_exception
    return UserResponse(
    id=str(user["_id"]),
    name=user["name"],
    email=user["email"],
    created_at=user["created_at"]
)

async def require_admin(current_user=Depends(get_current_user)):
    # Simple check: treat one hardcoded email as admin
    if current_user.email != "admin@example.com":
        raise HTTPException(status_code=403, detail="Admins only")
    return current_user
