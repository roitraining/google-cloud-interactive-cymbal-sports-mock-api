import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

# This fixture allows us to share the same client across tests if needed
# and guarantees the app is imported correctly.
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# Generate a unique username for each run to avoid conflicts
UNIQUE_USER = f"user_{uuid.uuid4().hex[:8]}"
UNIQUE_PASS = "securepassword"
ORDER_ID = "ORDER-123456" # Mocked, so ID doesn't need to exist in DB
ITEM_ID = "SKU-10001" # Should exist after save_inventory

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Cymbal Sports Mock API"}

def test_save_inventory(client):
    """
    Depending on permissions, this might fail in some environments if not authed.
    If it succeeds, it populates the DB.
    """
    print("\n[Integration] Initializing Inventory...")
    response = client.get("/save_inventory")
    # It might fail if GOOGLE_APPLICATION_CREDENTIALS aren't set or valid
    # But for integration tests we assume environment is ready.
    assert response.status_code == 200
    assert response.json() == {"message": "Inventory saved successfully"}

def test_get_categories(client):
    response = client.get("/products/categories")
    assert response.status_code == 200
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) > 0 # Should have categories after save_inventory
    print(f"\n[Integration] Found categories: {categories}")

def test_get_top_products(client):
    response = client.get("/products/top")
    assert response.status_code == 200
    products = response.json()
    assert isinstance(products, list)
    assert len(products) <= 5
    if len(products) > 0:
        print(f"\n[Integration] Top product: {products[0]['title']}")

def test_get_products_by_category(client):
    # First get a valid category
    cat_response = client.get("/products/categories")
    categories = cat_response.json()
    if not categories:
        pytest.skip("No categories found to test filtering")
    
    category = categories[0]
    response = client.get(f"/products/category/{category}")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    assert products[0]["category"] == category

def test_get_product_details(client):
    # Find a real product first
    top_response = client.get("/products/top")
    products = top_response.json()
    if not products:
        pytest.skip("No products found to test details")
        
    item_id = products[0]["id"]
    response = client.get(f"/products/{item_id}")
    assert response.status_code == 200
    product = response.json()
    assert product["id"] == item_id

def test_create_user(client):
    response = client.post("/users", json={"username": UNIQUE_USER, "password": UNIQUE_PASS})
    # If user already exists from previous failed run, handle gracefully or expect success
    if response.status_code == 400:
        assert response.json()["detail"] == "User already exists"
    else:
        assert response.status_code == 200
        assert response.json()["username"] == UNIQUE_USER

def test_login(client):
    response = client.post("/login", json={"username": UNIQUE_USER, "password": UNIQUE_PASS})
    assert response.status_code == 200
    assert "token" in response.json()

def test_cart_workflow(client):
    # 1. Add to cart
    # Need a valid item ID.
    top_response = client.get("/products/top")
    products = top_response.json()
    if not products:
        pytest.skip("No products found for cart test")
    
    item_id = products[0]["id"]
    
    add_response = client.post("/cart/add", json={
        "user_id": UNIQUE_USER, 
        "item_id": item_id, 
        "quantity": 2
    })
    assert add_response.status_code == 200
    cart = add_response.json()["cart"]
    assert cart["items"][item_id] == 2
    
    # 2. Remove from cart
    remove_response = client.post("/cart/remove", json={
        "user_id": UNIQUE_USER, 
        "item_id": item_id
    })
    assert remove_response.status_code == 200
    # Should be gone
    cart_after = remove_response.json()["cart"]
    assert item_id not in cart_after["items"]

def test_order_mock_logic(client):
    # These are mocked so they don't depend on DB state, but good to test integration of the endpoint
    status_response = client.get(f"/orders/{ORDER_ID}")
    assert status_response.status_code == 200
    assert status_response.json()["order_id"] == ORDER_ID
    
    return_response = client.post(f"/orders/{ORDER_ID}/return", json={"reason": "Test return"})
    assert return_response.status_code == 200
    assert return_response.json()["status"] == "RETURN_INITIATED"
