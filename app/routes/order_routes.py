from fastapi import APIRouter, Depends, HTTPException
from app.schemas.order_schema import OrderResponse
from app.models.order_model import order_helper
from app.auth.dependencies import get_current_user
from app.database import db
from datetime import datetime
from bson import ObjectId
from app.schemas.order_schema import OrderStatusUpdate
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/orders", tags=["Orders"])

# Place order from cart
@router.post("/", response_model=OrderResponse)
async def place_order(current_user=Depends(get_current_user)):
    cart = await db.carts.find_one({"user_email": current_user.email})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Calculate total price from product catalog
    total_price = 0.0
    for item in cart["items"]:
        product = await db.products.find_one({"_id": ObjectId(item["product_id"])})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
        total_price += product["price"] * item["quantity"]

    order_data = {
        "user_email": current_user.email,
        "items": cart["items"],
        "total_price": total_price,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = await db.orders.insert_one(order_data)
    order = await db.orders.find_one({"_id": result.inserted_id})

    # Clear cart after placing order
    await db.carts.update_one(
        {"user_email": current_user.email},
        {"$set": {"items": []}}
    )

    return order_helper(order)

# View all orders (for the current user)
@router.get("/", response_model=list[OrderResponse])
async def get_user_orders(current_user=Depends(get_current_user)):
    cursor = db.orders.find({"user_email": current_user.email})
    orders = []
    async for order in cursor:
        orders.append(order_helper(order))
    return orders


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: str, update: OrderStatusUpdate, admin_user=Depends(require_admin)):
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    VALID_STATUSES = ["pending", "shipped", "delivered", "cancelled"]
    if update.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status value")

    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": update.status}}
    )

    updated_order = await db.orders.find_one({"_id": ObjectId(order_id)})
    return order_helper(updated_order)

