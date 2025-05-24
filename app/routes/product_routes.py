from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.models.product_model import product_helper
from app.database import db
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/products", tags=["Products"])

# Create a product
@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    product_dict = product.dict()
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

# Get a single product
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_helper(product)

# Update a product
@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, update: ProductUpdate):
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {k: v for k, v in update.dict().items() if v is not None}}
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
