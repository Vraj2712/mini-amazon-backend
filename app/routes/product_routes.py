from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.models.product_model import product_helper
from app.database import db
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Query
from typing import Optional
from bson.errors import InvalidId

router = APIRouter(prefix="/products", tags=["Products"])

# Create a product
@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.utcnow()
    result = await db.products.insert_one(product_dict)
    new_product = await db.products.find_one({"_id": result.inserted_id})
    return product_helper(new_product)

# Get all products
@router.get("/", response_model=list[ProductResponse])
async def get_all_products():
    products_cursor = db.products.find()
    products = []
    async for product in products_cursor:
        products.append(product_helper(product))
    return products

@router.get("/search")
async def search_products(
    q: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    in_stock: Optional[bool] = Query(None)
):
    query = {}

    if q:
        query["name"] = {"$regex": q, "$options": "i"}

    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price

    if in_stock is not None:
        query["in_stock"] = in_stock

    cursor = db.products.find(query)
    results = []
    async for product in cursor:
        results.append(product_helper(product))

    return results


# Get a single product
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id)})
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product_helper(product)

# Update a product
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, update: ProductUpdate):
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {k: v for k, v in update.model_dump().items() if v is not None}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not updated")
    updated_product = await db.products.find_one({"_id": ObjectId(product_id)})
    return product_helper(updated_product)

# Delete a product
@router.delete("/{product_id}")
async def delete_product(product_id: str):
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

