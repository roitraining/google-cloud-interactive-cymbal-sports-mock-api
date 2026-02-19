import csv
import random

categories = [
    "Running", 
    "Soccer", 
    "Basketball", 
    "Apparel", 
    "Yoga", 
    "Boxing"
]

adjectives = ["Lightweight", "Performance", "Durable", "Comfort", "Speed", "Pro", "Elite", "Vent", "Tech", "Ultra"]
nouns = {
    "Running": ["Shoes", "Shorts", "Vest", "Socks", "Headband"],
    "Soccer": ["Cleats", "Ball", "Shin Guards", "Jersey", "Shorts"],
    "Basketball": ["Sneakers", "Jersey", "Shorts", "Ball", "Headband"],
    "Apparel": ["T-Shirt", "Hoodie", "Jacket", "Leggings", "Hat"],
    "Yoga": ["Mat", "Block", "Strap", "Towel", "Leggings"],
    "Boxing": ["Gloves", "Wraps", "Shoes", "Headgear", "Punching Bag"]
}

statuses = ["IN_STOCK", "LOW_STOCK"]
ratings = [3.5, 3.8, 4.0, 4.2, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0]

def generate_sku(n):
    return f"SKU-{10000 + n}"

items = []

for i in range(100):
    category = random.choice(categories)
    noun = random.choice(nouns[category])
    adj = random.choice(adjectives)
    
    title = f"Cymbal {adj} {category} {noun}"
    description = f"Experience the {adj.lower()} design of our {category.lower()} {noun.lower()}. Perfect for training and competition."
    
    # Random price between 20 and 200
    price = round(random.uniform(20.0, 200.0), 2)
    
    status = random.choice(statuses) # Typically skewed to In Stock but randomized here
    if random.random() > 0.8:
        status = "LOW_STOCK"
    else:
        status = "IN_STOCK"
        
    rating = random.choice(ratings)
    image_url = "https://storage.googleapis.com/cymbal-sports/placeholder.png" # Placeholder
    
    item = {
        "id": generate_sku(i),
        "category": category,
        "title": title,
        "description": description,
        "price": price,
        "inventory_status": status,
        "rating": rating,
        "image_url": image_url
    }
    items.append(item)

# Write to CSV
file_path = "app/data/inventory.csv"
with open(file_path, mode='w', newline='') as csv_file:
    fieldnames = ["id", "category", "title", "description", "price", "inventory_status", "rating", "image_url"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for item in items:
        writer.writerow(item)

print(f"Generated {len(items)} items in {file_path}")
