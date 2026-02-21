from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)

@patch('app.database.search_products')
def test_search_products(mock_search):
    # Mock data
    mock_results = [
        {
            "id": "SKU-1", 
            "title": "Soccer Ball", 
            "category": "Sports",
            "description": "A great ball",
            "price": 20.0,
            "inventory_status": "IN_STOCK",
            "rating": 4.5,
            "image_url": "http://example.com/ball.jpg"
        },
        {
            "id": "SKU-2", 
            "title": "Basketball",
            "category": "Sports",
            "description": "Good grip",
            "price": 25.0,
            "inventory_status": "IN_STOCK",
            "rating": 4.8,
            "image_url": "http://example.com/bball.jpg"
        }
    ]
    mock_search.return_value = mock_results
    
    response = client.get("/api/products/search?q=Ball")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Soccer Ball"

@patch('app.database.search_products')
def test_search_products_empty(mock_search):
    mock_search.return_value = []
    
    response = client.get("/api/products/search?q=XYZ")
    
    assert response.status_code == 200
    assert response.json() == []

def test_search_products_no_query():
    response = client.get("/api/products/search?q=")
    assert response.status_code == 200
    assert response.json() == []
