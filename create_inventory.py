import csv
import random

categories = [
    "Football", 
    "Baseball", 
    "Basketball", 
    "Golf", 
    "Footwear", 
    "Apparel", 
    "Fishing", 
    "Hunting", 
    "Camping"
]

adjectives = ["Lightweight", "Performance", "Durable", "Comfort", "Speed", "Pro", "Elite", "Vent", "Tech", "Ultra"]
nouns = {
    "Football": [
        ("Helmet", 150, 450), 
        ("Shoulder Pads", 80, 250), 
        ("Jersey", 60, 150), 
        ("Cleats", 70, 180), 
        ("Ball", 25, 90)
    ],
    "Baseball": [
        ("Bat", 100, 400), 
        ("Glove", 50, 300), 
        ("Helmet", 40, 90), 
        ("Cleats", 60, 140), 
        ("Ball", 15, 40)
    ],
    "Basketball": [
        ("Sneakers", 90, 220), 
        ("Jersey", 50, 130), 
        ("Shorts", 30, 70), 
        ("Ball", 30, 80), 
        ("Headband", 10, 25)
    ],
    "Golf": [
        ("Clubs", 300, 1200), 
        ("Balls", 20, 60), 
        ("Bag", 90, 250), 
        ("Polo", 40, 90), 
        ("Shoes", 80, 200)
    ],
    "Footwear": [
        ("Running Shoes", 90, 180), 
        ("Slides", 25, 50), 
        ("Sneakers", 70, 160), 
        ("Boots", 110, 220), 
        ("Sandals", 30, 80)
    ],
    "Apparel": [
        ("T-Shirt", 20, 50), 
        ("Hoodie", 50, 110), 
        ("Jacket", 80, 250), 
        ("Leggings", 40, 100), 
        ("Hat", 20, 40)
    ],
    "Fishing": [
        ("Rod", 80, 300), 
        ("Reel", 50, 200), 
        ("Tackle Box", 20, 80), 
        ("Waders", 70, 200), 
        ("Lure", 5, 25)
    ],
    "Hunting": [
        ("Blind", 150, 400), 
        ("Boots", 120, 300), 
        ("Vest", 40, 120), 
        ("Scope", 100, 500), 
        ("Knife", 30, 150)
    ],
    "Camping": [
        ("Tent", 100, 600), 
        ("Sleeping Bag", 50, 250), 
        ("Stove", 40, 150), 
        ("Lantern", 20, 80), 
        ("Cooler", 50, 300)
    ]
}

statuses = ["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]
ratings = [3.5, 3.8, 4.0, 4.2, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0]

def generate_sku(n):
    return f"SKU-{10000 + n}"

items = []

for i in range(200):
    category = random.choice(categories)
    # Select random tuple (noun, min_price, max_price)
    noun_data = random.choice(nouns[category])
    noun = noun_data[0]
    min_p = noun_data[1]
    max_p = noun_data[2]
    
    adj = random.choice(adjectives)
    
    # Slightly adjust title generation to sound more natural
    if category == "Footwear" or category == "Apparel":
        title = f"Cymbal {adj} {noun}"
    else:
        title = f"Cymbal {adj} {category} {noun}"
        
    description = f"Experience the {adj.lower()} design of our {category.lower()} {noun.lower()}. Perfect for outdoor enthusiasts and athletes."
    
    # Generate realistic price based on specific item range
    price = round(random.uniform(float(min_p), float(max_p)), 2)
    
    rand_val = random.random()
    if rand_val > 0.9:
        status = "OUT_OF_STOCK"
    elif rand_val > 0.75:
        status = "LOW_STOCK"
    else:
        status = "IN_STOCK"
        
    rating = random.choice(ratings)
    sku = generate_sku(i)
    image_url = f"https://storage.googleapis.com/cymbal-sports-prod-images-dar/{sku}.png"
    
    item = {
        "id": sku,
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
