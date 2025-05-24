from pydantic import BaseModel
from typing import List, Optional

class CartItem(BaseModel):
    product_id: str
    quantity: int

class CartAddRequest(BaseModel):
    product_id: str
    quantity: int

class CartUpdateRequest(BaseModel):
    product_id: str
    quantity: int

class CartRemoveRequest(BaseModel):
    product_id: str

class CartResponse(BaseModel):
    user_email: str
    items: List[CartItem]
