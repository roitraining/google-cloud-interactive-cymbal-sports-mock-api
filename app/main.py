import os
import random
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    InventoryItem, CartItem, User, LoginRequest, 
    CartAddRequest, CartRemoveRequest, OrderStatusResponse, 
    ReturnOrderRequest, ReturnOrderResponse, CartModel
)
from app import database
from app import config

app = FastAPI(
    title="Cymbal Sports Mock API",
    description="Mock API for Cymbal Sports store for CX Agent Studio training.",
    version="1.0.0",
    servers=[{"url": config.SERVICE_URL, "description": "Cloud Run Service URL"}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to the Cymbal Sports Mock API"}

@app.get("/save_inventory", tags=["Admin"], summary="Initialize Inventory")
async def save_inventory():
    """
    Load the inventory from the CSV file into Firestore. 
    This is a one-time management function.
    """
    success = database.save_inventory_from_csv()
    if success:
        return {"message": "Inventory saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save inventory")

@app.get("/products/categories", tags=["Products"], response_model=List[str])
async def get_categories():
    """
    Get all unique object categories from the inventory.
    """
    return database.get_all_categories()

@app.get("/products/top", tags=["Products"], response_model=List[InventoryItem])
async def get_top_products():
    """
    Get 5 random products representing top sellers from the store.
    """
    products = database.get_top_products()
    return products

@app.get("/products/category/{category}", tags=["Products"], response_model=List[InventoryItem])
async def get_products_by_category(category: str):
    """
    Get all products in a specific category.
    """
    products = database.get_products_by_category(category)
    if not products:
        # Should we return 404 or empty list? List is better for user experience but 404 is technically correct if none exist.
        # But this is "get by category", if category is empty, return empty list.
        return []
    return products

@app.get("/products/{item_id}", tags=["Products"], response_model=InventoryItem)
async def get_product_details(item_id: str):
    """
    Get details for a specific product by its ID (SKU).
    """
    item = database.get_inventory_item(item_id)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/orders/{order_id}", tags=["Orders"], response_model=OrderStatusResponse)
async def get_order_status(order_id: str):
    """
    Get the status of an order. 
    Mocks the response for any order ID.
    """
    # Mock logic: Deterministic based on order_id hash or just random
    # To be consistent for demos, let's hash it slightly
    statuses = ["SHIPPED", "DELIVERED", "PROCESSING", "CANCELLED"]
    # unique status based on order_id characters
    idx = sum(ord(c) for c in order_id) % len(statuses)
    status = statuses[idx]
    
    return {
        "order_id": order_id,
        "status": status,
        "estimated_delivery": "2023-12-01" # Mock date
    }

@app.post("/orders/{order_id}/return", tags=["Orders"], response_model=ReturnOrderResponse)
async def return_order(order_id: str, request: ReturnOrderRequest):
    """
    Process a return for an order.
    """
    # Mock logic
    return {
        "order_id": order_id,
        "status": "RETURN_INITIATED",
        "message": f"Return initiated for order {order_id}. Reason: {request.reason}"
    }

@app.post("/cart/add", tags=["Cart"])
async def add_item_to_cart(request: CartAddRequest):
    """
    Add an item to a user's cart.
    """
    success = database.add_item_to_cart(request.user_id, request.item_id, request.quantity)
    if success:
        return {"message": "Item added to cart", "cart": database.get_cart(request.user_id)}
    raise HTTPException(status_code=400, detail="Failed to add item (Item might not exist)")

@app.post("/cart/remove", tags=["Cart"])
async def remove_item_from_cart(request: CartRemoveRequest):
    """
    Remove an item from a user's cart.
    """
    success = database.remove_item_from_cart(request.user_id, request.item_id)
    if success:
        return {"message": "Item removed from cart", "cart": database.get_cart(request.user_id)}
    raise HTTPException(status_code=400, detail="Failed to remove item (Item might not be in cart)")

@app.get("/cart/{user_id}", tags=["Cart"], response_model=CartModel)
async def get_cart(user_id: str):
    """
    Get the current user's cart with full product details (title, price, image).
    Useful for displaying the cart to the user in a rich response.
    """
    cart_data = database.get_cart_details(user_id)
    # Map dictionary to Pydantic model
    return CartModel(
        user_id=cart_data["user_id"],
        items=cart_data["items"], # List of dicts matching CartItemDetail
        total_price=cart_data["total_price"]
    )

@app.post("/users", tags=["Users"])
async def create_account(user: User):
    """
    Create a new user account.
    """
    success = database.create_user(user.username, user.password)
    if success:
        return {"message": "User created successfully", "username": user.username}
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/login", tags=["Users"])
async def login(request: LoginRequest):
    """
    Log in a user.
    """
    success = database.verify_user(request.username, request.password)
    if success:
        return {"message": "Login successful", "token": "mock-token-123"}
    raise HTTPException(status_code=401, detail="Invalid username or password")
