# app/main.py
from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.routes.cart_routes import router as cart_router
from app.routes.product_routes import router as product_router
from app.routes.order_routes import router as order_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Mini Amazon backend is live!"}
app.include_router(auth_router) 
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
