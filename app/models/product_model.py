def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product.get("description"),
        "price": product["price"],
        "in_stock": product["in_stock"],
        "created_at": product["created_at"]
    }
