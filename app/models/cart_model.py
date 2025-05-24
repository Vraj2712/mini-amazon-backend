def cart_helper(cart) -> dict:
    return {
        "user_email": cart["user_email"],
        "items": cart["items"]  # list of {product_id, quantity}
    }
