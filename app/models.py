from pydantic import BaseModel
from typing import Optional, List

class InventoryItem(BaseModel):
    id: str
    category: str
    title: str
    description: str
    price: float
    inventory_status: str
    rating: float
    image_url: str

class CartItem(BaseModel):
    item_id: str
    quantity: int

class User(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str
    
class CartAddRequest(BaseModel):
    user_id: str
    item_id: str
    quantity: int

class CartRemoveRequest(BaseModel):
    user_id: str
    item_id: str

class OrderStatusResponse(BaseModel):
    order_id: str
    status: str
    estimated_delivery: str

class ReturnOrderRequest(BaseModel):
    reason: str

class ReturnOrderResponse(BaseModel):
    order_id: str
    status: str
    message: str
