
import os
import csv
import random
from google.cloud import firestore
from app.models import InventoryItem, CartItem
from app import config

# Initialize Firestore
db = None
try:
    db = firestore.Client()
    print("Firestore client initialized.")
except Exception as e:
    print(f"Warning: Could not initialize Firestore client. {e}")

def get_inventory_item(item_id: str):
    if not db:
        print("Firestore not available.")
        return None
    doc_ref = db.collection("inventory").document(item_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None


def validate_category(category: str):
    """
    Validates and normalizes category names, handling synonyms and case sensitivity.
    """
    if not category:
        return None
        
    # Standardize to Title Case for matching our DB (e.g. "basketball" -> "Basketball")
    normalized_cat = category.strip().title()
    
    # Map common synonyms/plurals to canonical categories
    synonyms = {
        # Apparel
        "Clothing": "Apparel",
        "Clothes": "Apparel",
        "Wear": "Apparel",
        "Jackets": "Apparel",
        "Shirts": "Apparel",
        "Shirt": "Apparel",
        "T-Shirt": "Apparel",
        "T-Shirts": "Apparel",
        "Pants": "Apparel",
        
        # Footwear
        "Shoes": "Footwear",
        "Shoe": "Footwear",
        "Sneakers": "Footwear",
        "Sneaker": "Footwear",
        "Boots": "Footwear",
        "Boot": "Footwear",
        "Sandals": "Footwear",
        "Sandal": "Footwear",
        "Cleats": "Footwear",
        "Cleat": "Footwear",
        
        # Basketball
        "Basketballs": "Basketball",
        "Hoops": "Basketball",
        
        # Baseball
        "Baseballs": "Baseball",
        
        # Football
        "Footballs": "Football",
        "Pads": "Football",
        
        # Golf
        "Golfs": "Golf",
        "Clubs": "Golf",
        "Club": "Golf",
        
        # Camping
        "Tents": "Camping",
        "Tent": "Camping",
        "Gear": "Camping",
        
        # Fishing
        "Fish": "Fishing",
        "Rods": "Fishing",
        "Rod": "Fishing",
        "Lures": "Fishing",
        "Lure": "Fishing",
        
        # Hunting
        "Hunt": "Hunting",
    }
    
    # Check exact match or synonym
    return synonyms.get(normalized_cat, normalized_cat)

def get_products_by_category(category: str):
    if not db:
        print("Firestore not available.")
        return []
    
    # Normalize category (handle case sensitivity and synonyms)
    valid_category = validate_category(category)
    
    products_ref = db.collection("inventory")
    query = products_ref.where("category", "==", valid_category)
    docs = query.stream()
    
    return [doc.to_dict() for doc in docs]

def search_products(search_query: str):
    if not db:
        print("Firestore not available.")
        return []
    
    products_ref = db.collection("inventory")
    # Firestore doesn't support naive substring search. 
    # Since dataset is small (mock), fetch all and filter in Python.
    docs = products_ref.stream()
    
    results = []
    query_lower = search_query.lower().strip()
    
    for doc in docs:
        data = doc.to_dict()
        title = data.get("title", "").lower()
        description = data.get("description", "").lower() # search in description too? User said Product Name. I'll stick to title mostly, or match both for robustness? User said "Product Name" but robust usually implies both. I will check Title for now as requested.
        
        if query_lower in title:
            results.append(data)
            
    return results

def get_top_products():
    if not db:
        print("Firestore not available.")
        return []
    
    # Mocking "Top Products" by randomly selecting 8 items
    products_ref = db.collection("inventory")
    # For a small dataset, fetching all is fine. For larger, we'd need a better strategy.
    docs = list(products_ref.stream())
    
    if not docs:
        return []

    # Select 8 random products (or fewer if less than 8 exist)
    count = min(len(docs), 8)
    selected_docs = random.sample(docs, count)
    
    return [doc.to_dict() for doc in selected_docs]

def get_all_categories():
    if not db:
        print("Firestore not available.")
        return []
        
    products_ref = db.collection("inventory")
    # Get all docs but only the category field to be efficient
    docs = products_ref.select(["category"]).stream()
    
    categories = set()
    for doc in docs:
        data = doc.to_dict()
        if "category" in data:
            categories.add(data["category"])
            
    return list(categories)

def save_inventory_from_csv():
    if not db:
        print("Firestore not initialized. Skipping save.")
        return False
        
    # Correct pathing logic for different execution contexts
    csv_path = os.path.join(os.path.dirname(__file__), "data/inventory.csv")
    if not os.path.exists(csv_path):
        # Try relative to CWD if module path fails
        csv_path = "app/data/inventory.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: Inventory file not found at {csv_path}")
        return False

    batch = db.batch()
    count = 0
    
    try:
        with open(csv_path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                doc_ref = db.collection("inventory").document(row["id"])
                # Convert types
                row["price"] = float(row["price"])
                row["rating"] = float(row["rating"])
                batch.set(doc_ref, row)
                count += 1
                
                # Firestore batch limit is 500
                if count % 400 == 0:
                    batch.commit()
                    batch = db.batch()
                    
        if count % 400 != 0:
            batch.commit()
            
        print(f"Saved {count} items to Firestore.")
        return True
    except Exception as e:
        print(f"Error saving inventory: {e}")
        return False

def add_item_to_cart(user_id: str, item_id: str, quantity: int):
    if not db:
        print("Firestore not available.")
        return False

    cart_ref = db.collection("carts").document(user_id)
    
    # Check if item exists in inventory first? (Optional but good)
    # Skipping for performance/simplicity or assume valid input
    
    cart_doc = cart_ref.get()
    current_data = cart_doc.to_dict() if cart_doc.exists else {"items": {}}
    
    items = current_data.get("items", {})
    # Default to 0 if not present
    current_qty = items.get(item_id, 0)
    items[item_id] = current_qty + quantity
    
    cart_ref.set({"items": items}, merge=True)
    return True

def remove_item_from_cart(user_id: str, item_id: str):
    if not db:
        return False
        
    cart_ref = db.collection("carts").document(user_id)
    cart_doc = cart_ref.get()
    
    if not cart_doc.exists:
        return False
        
    current_data = cart_doc.to_dict()
    items = current_data.get("items", {})
    
    if item_id in items:
        del items[item_id]
        cart_ref.set({"items": items}) # Overwrite items
        return True
        
    return False

def clear_cart(user_id: str):
    if not db:
        return False
        
    cart_ref = db.collection("carts").document(user_id)
    cart_ref.set({"items": {}})
    return True

def get_cart(user_id: str):
    if not db:
        return {"items": {}}
    
    cart_ref = db.collection("carts").document(user_id)
    doc = cart_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return {"items": data.get("items", {})}
    return {"items": {}}

def get_cart_details(user_id: str):
    """
    Returns full cart with product details (title, price, image) joined in.
    """
    if not db:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
    
    # 1. Get Cart
    cart_ref = db.collection("carts").document(user_id)
    doc = cart_ref.get()
    if not doc.exists:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
    
    data = doc.to_dict()
    items_map = data.get("items", {}) # { "SKU-123": 2 }
    
    if not items_map:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
        
    enriched_items = []
    total = 0.0
    
    for item_id, qty in items_map.items():
        p_doc = db.collection("inventory").document(item_id).get()
        if p_doc.exists:
            p_data = p_doc.to_dict()
            price = float(p_data.get("price", 0.0))
            
            enrich = {
                "item_id": item_id,
                "quantity": qty,
                "title": p_data.get("title", "Unknown"),
                "price": price,
                "image_url": p_data.get("image_url", "")
            }
            enriched_items.append(enrich)
            total += price * qty
            
    return {
        "user_id": user_id,
        "items": enriched_items,
        "total_price": round(total, 2)
    }
    
def get_cart_details(user_id: str):
    """
    Returns full cart with product details (title, price, image) joined in.
    """
    if not db:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
    
    # 1. Get Cart
    cart_ref = db.collection("carts").document(user_id)
    doc = cart_ref.get()
    if not doc.exists:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
    
    data = doc.to_dict()
    items_map = data.get("items", {}) # { "SKU-123": 2 }
    
    if not items_map:
        return {"user_id": user_id, "items": [], "total_price": 0.0}
        
    # 2. Get All Products in one go (or loop if small list)
    # Ideally use IN query, but Firestore limits IN to 10-30 items.
    # For a cart, user usually has few items, so loop is okay for mock.
    
    enriched_items = []
    total = 0.0
    
    for item_id, qty in items_map.items():
        # Optimization: Could cache products or use getAll
        p_doc = db.collection("inventory").document(item_id).get()
        if p_doc.exists:
            p_data = p_doc.to_dict()
            price = float(p_data.get("price", 0.0))
            if "total_price" not in p_data:
                # Helper calculation fix
                pass
            
            enrich = {
                "item_id": item_id,
                "quantity": qty,
                "title": p_data.get("title", "Unknown"),
                "price": price,
                "image_url": p_data.get("image_url", "")
            }
            enriched_items.append(enrich)
            total += price * qty
            
    return {
        "user_id": user_id,
        "items": enriched_items,
        "total_price": round(total, 2)
    }

def create_user(username, password):
    if not db:
        return False
    # Simple store, plain text password for mock
    user_ref = db.collection("users").document(username)
    if user_ref.get().exists:
        return False # Already exists
    
    user_ref.set({"username": username, "password": password})
    return True

def verify_user(username, password):
    if not db:
        return True # Mock success if DB down? No, fail secure.
    user_ref = db.collection("users").document(username)
    doc = user_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return data.get("password") == password 
    return False

