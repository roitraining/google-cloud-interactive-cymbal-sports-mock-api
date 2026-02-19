from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Cymbal Sports Mock API"}

@patch('app.database.get_inventory_item')
def test_get_product_details(mock_get_item):
    mock_item = {
        "id": "SKU-12345",
        "category": "Shoes",
        "title": "Cymbal Aero Running Shoes",
        "description": "Lightweight performance...",
        "price": 95.00,
        "inventory_status": "IN_STOCK",
        "rating": 4.8,
        "image_url": "http://example.com/image.png"
    }
    mock_get_item.return_value = mock_item
    
    response = client.get("/products/SKU-12345")
    assert response.status_code == 200
    assert response.json() == mock_item

@patch('app.database.get_inventory_item')
def test_get_product_details_not_found(mock_get_item):
    mock_get_item.return_value = None
    response = client.get("/products/SKU-99999")
    assert response.status_code == 404

def test_get_order_status():
    # Mock behavior is deterministic in code, so predictable
    response = client.get("/orders/ORDER-123")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "ORDER-123"
    assert "status" in data
    
def test_return_order():
    response = client.post("/orders/ORDER-123/return", json={"reason": "size too small"})
    assert response.status_code == 200
    assert response.json()["status"] == "RETURN_INITIATED"

@patch('app.database.add_item_to_cart')
@patch('app.database.get_cart')
def test_add_to_cart(mock_get_cart, mock_add):
    mock_add.return_value = True
    mock_get_cart.return_value = {"items": {"SKU-123": 1}}
    
    response = client.post("/cart/add", json={"user_id": "user1", "item_id": "SKU-123", "quantity": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Item added to cart"

@patch('app.database.verify_user')
def test_login(mock_verify):
    mock_verify.return_value = True
    response = client.post("/login", json={"username": "user1", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.json()

@patch('app.database.verify_user')
def test_login_fail(mock_verify):
    mock_verify.return_value = False
    response = client.post("/login", json={"username": "user1", "password": "wrongpassword"})
    assert response.status_code == 401
