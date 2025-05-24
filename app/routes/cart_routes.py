from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.cart_schema import CartAddRequest, CartUpdateRequest, CartRemoveRequest, CartResponse
from app.auth.dependencies import get_current_user
from app.models.cart_model import cart_helper
from app.database import db

router = APIRouter(prefix="/cart", tags=["Cart"])

# View cart
@router.get("/", response_model=CartResponse)
async def get_cart(current_user=Depends(get_current_user)):
    cart = await db.carts.find_one({"user_email": current_user.email})
    if not cart:
        return {"user_email": current_user.email, "items": []}
    return cart_helper(cart)

# Add item to cart
@router.post("/add", response_model=CartResponse)
async def add_to_cart(item: CartAddRequest, current_user=Depends(get_current_user)):
    cart = await db.carts.find_one({"user_email": current_user.email})
    if not cart:
        new_cart = {
            "user_email": current_user.email,
            "items": [{"product_id": item.product_id, "quantity": item.quantity}]
        }
        await db.carts.insert_one(new_cart)
        return new_cart

    # Check if item already exists in cart
    for cart_item in cart["items"]:
        if cart_item["product_id"] == item.product_id:
            cart_item["quantity"] += item.quantity
            break
    else:
        cart["items"].append({"product_id": item.product_id, "quantity": item.quantity})

    await db.carts.update_one(
        {"user_email": current_user.email},
        {"$set": {"items": cart["items"]}}
    )

    return cart_helper(cart)

# Update quantity
@router.put("/update", response_model=CartResponse)
async def update_cart_item(update: CartUpdateRequest, current_user=Depends(get_current_user)):
    cart = await db.carts.find_one({"user_email": current_user.email})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    updated = False
    for item in cart["items"]:
        if item["product_id"] == update.product_id:
            item["quantity"] = update.quantity
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    await db.carts.update_one(
        {"user_email": current_user.email},
        {"$set": {"items": cart["items"]}}
    )

    return cart_helper(cart)

# Remove item from cart
@router.delete("/item", response_model=CartResponse)
async def remove_from_cart(remove: CartRemoveRequest, current_user=Depends(get_current_user)):
    cart = await db.carts.find_one({"user_email": current_user.email})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart["items"] = [item for item in cart["items"] if item["product_id"] != remove.product_id]

    await db.carts.update_one(
        {"user_email": current_user.email},
        {"$set": {"items": cart["items"]}}
    )

    return cart_helper(cart)
