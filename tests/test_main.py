from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Cymbal Sports Mock API"}

@patch('app.database.get_all_categories')
def test_get_categories(mock_get_categories):
    mock_categories = ["Shoes", "Apparel", "Gear"]
    mock_get_categories.return_value = mock_categories
    # Note: URL is /products/categories
    response = client.get("/api/products/categories")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert "Shoes" in response.json()

@patch('app.database.save_inventory_from_csv')
def test_save_inventory(mock_save):
    mock_save.return_value = True
    response = client.get("/api/save_inventory") # Now a GET request
    assert response.status_code == 200
    assert response.json() == {"message": "Inventory saved successfully"}

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
    
    response = client.get("/api/products/SKU-12345")
    assert response.status_code == 200
    assert response.json() == mock_item

@patch('app.database.get_inventory_item')
def test_get_product_details_not_found(mock_get_item):
    mock_get_item.return_value = None
    response = client.get("/api/products/SKU-99999")
    assert response.status_code == 404

@patch('app.database.get_top_products')
def test_get_top_products(mock_get_top):
    mock_products = [
        {"id": "SKU-1", "category": "Shoes", "title": "Shoe 1", "description": "Desc", "price": 10.0, "inventory_status": "IN_STOCK", "rating": 5.0, "image_url": "url"},
        {"id": "SKU-2", "category": "Shoes", "title": "Shoe 2", "description": "Desc", "price": 20.0, "inventory_status": "IN_STOCK", "rating": 4.9, "image_url": "url"}
    ]
    mock_get_top.return_value = mock_products
    response = client.get("/api/products/top")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == "SKU-1"

@patch('app.database.get_products_by_category')
def test_get_products_by_category(mock_get_by_cat):
    mock_products = [
        {"id": "SKU-1", "category": "Running", "title": "Running Shoe", "description": "Desc", "price": 10.0, "inventory_status": "IN_STOCK", "rating": 5.0, "image_url": "url"}
    ]
    mock_get_by_cat.return_value = mock_products
    response = client.get("/api/products/category/Running")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "Running"

def test_get_order_status():
    # Mock behavior is deterministic in code, so predictable
    response = client.get("/api/orders/ORDER-123")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "ORDER-123"
    assert "status" in data
    
def test_return_order():
    response = client.post("/api/orders/ORDER-123/return", json={"reason": "size too small"})
    assert response.status_code == 200
    assert response.json()["status"] == "RETURN_INITIATED"

@patch('app.database.add_item_to_cart')
@patch('app.database.get_cart')
def test_add_to_cart(mock_get_cart, mock_add):
    mock_add.return_value = True
    mock_get_cart.return_value = {"items": {"SKU-123": 1}}
    
    response = client.post("/api/cart/add", json={"user_id": "user1", "item_id": "SKU-123", "quantity": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Item added to cart"

@patch('app.database.verify_user')
def test_login(mock_verify):
    mock_verify.return_value = True
    response = client.post("/api/login", json={"username": "user1", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.json()

@patch('app.database.verify_user')
def test_login_fail(mock_verify):
    mock_verify.return_value = False
    response = client.post("/api/login", json={"username": "user1", "password": "wrongpassword"})
    assert response.status_code == 401
