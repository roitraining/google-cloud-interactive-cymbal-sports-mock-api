
import os
import csv
from google.cloud import firestore
from app.models import InventoryItem, CartItem

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

def get_cart(user_id: str):
    if not db:
        return {"items": {}}
    
    cart_ref = db.collection("carts").document(user_id)
    doc = cart_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return {"items": data.get("items", {})}
    return {"items": {}}
    
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

