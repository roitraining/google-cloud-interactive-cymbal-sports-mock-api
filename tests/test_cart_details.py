from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models import CartModel

client = TestClient(app)

@patch('app.database.get_cart_details')
def test_get_cart_details(mock_get_details):
    # Mock data structure matching dict returned by database.get_cart_details
    mock_data = {
        "user_id": "user123",
        "items": [
            {
                "item_id": "SKU-1", 
                "quantity": 2, 
                "title": "Shoe", 
                "price": 50.0, 
                "image_url": "img.png"
            }
        ],
        "total_price": 100.0
    }
    mock_get_details.return_value = mock_data
    
    response = client.get("/api/cart/user123")
    assert response.status_code == 200
    
    # Validate against Pydantic model structure
    data = response.json()
    assert data["user_id"] == "user123"
    assert len(data["items"]) == 1
    assert data["total_price"] == 100.0
    assert data["items"][0]["title"] == "Shoe"

@patch('app.database.get_cart_details')
def test_get_cart_empty(mock_get_details):
    mock_data = {
        "user_id": "user123",
        "items": [],
        "total_price": 0.0
    }
    mock_get_details.return_value = mock_data
    
    response = client.get("/api/cart/user123")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 0
    assert data["total_price"] == 0.0
