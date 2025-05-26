from pydantic import BaseModel
from typing import List
from datetime import datetime
from pydantic import ConfigDict

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]

class OrderResponse(BaseModel):
    id: str
    user_email: str
    items: List[OrderItem]
    total_price: float
    status: str
    created_at: datetime

    class Config:
        model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    status: str  # e.g., "shipped", "delivered"

