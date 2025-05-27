from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user_schema import UserCreate, UserLogin, Token, UserPublic
from app.auth.utils import hash_password, verify_password, create_access_token
from app.database import db
from app.models.user_model import user_helper, UserResponse
from app.auth.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/user", response_model=UserResponse)
async def get_current_user_route(current_user=Depends(get_current_user)):
    return current_user

@router.post("/signup", response_model=UserPublic)
async def signup(user: UserCreate):
    user_exist = await db.users.find_one({"email": user.email})
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))  # hashed_password field
    user_dict["created_at"] = datetime.utcnow()

    result = await db.users.insert_one(user_dict)
    user_in_db = await db.users.find_one({"_id": result.inserted_id})
    return user_helper(user_in_db)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
