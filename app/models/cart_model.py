def cart_helper(cart) -> dict:
    return {
        "user_email": cart["user_email"],
        "items": [
            {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
            for item in cart["items"]
        ]
    }
