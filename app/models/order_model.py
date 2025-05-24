def order_helper(order) -> dict:
    return {
        "id": str(order["_id"]),
        "user_email": order["user_email"],
        "items": order["items"],  # list of {product_id, quantity}
        "total_price": order["total_price"],
        "status": order["status"],
        "created_at": order["created_at"]
    }
