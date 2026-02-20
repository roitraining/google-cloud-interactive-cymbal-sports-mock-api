import os
import random
import uuid
import shutil
import glob
from dotenv import load_dotenv
from google.cloud import storage
from typing import List, Dict

# Load environment variables (for credentials if in .env)
load_dotenv()

# Constants
BUCKET_PREFIX = "cymbal-sports-faqs-36yt84"
LOCAL_DIR = "rag_data"

# Mock Data Lists
CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", 
    "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", 
    "San Francisco", "Charlotte", "Indianapolis", "Seattle", "Denver", "Washington",
    "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City", "Portland", "Las Vegas",
    "Memphis", "Louisville", "Baltimore", "Milwaukee", "Albuquerque", "Tucson", "Fresno",
    "Sacramento", "Mesa", "Kansas City", "Atlanta", "Long Beach", "Omaha", "Raleigh",
    "Miami", "Virginia Beach", "Oakland", "Minneapolis", "Tulsa", "Tampa", "Arlington", "New Orleans"
]
# Mapping simpler state codes for demo purposes (mostly randomized/approximated for generated cities)
STATES = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA", "TX", "FL", "TX", "OH", "CA", "NC", "IN", "WA", "CO", "DC"] * 3
STREETS = ["Main St", "First Ave", "Broadway", "Market St", "Park Blvd", "State St", "Washington St", "Highland Ave", "Creek Rd", "Sunset Blvd", "River Rd", "Lake View Dr", "Meadow Ln", "Cedar St"]

PRODUCTS = [
    "Running Shoes", "Basketball", "Yoga Mat", "Tennis Racket", "Baseball Glove", 
    "Soccer Ball", "Football", "Golf Clubs", "Hiking Boots", "Swim Goggles", 
    "Cycling Helmet", "Dumbbells", "Kettlebell", "Treadmill", "Elliptical"
]

FAQ_TEMPLATES = [
    {"q": "What is the return policy for {product}?", "a": "You can return any {product} within 30 days of purchase for a full refund, provided it is unused and in its original packaging. Return shipping is free for Cymbal Sports members."},
    {"q": "How long does standard shipping take for {product} to {city}?", "a": "Standard shipping for {product} to {city} typically takes 3-5 business days. Expedited shipping options (1-2 days) are available at checkout."},
    {"q": "Do you offer a warranty on {product}?", "a": "Yes, we offer a 1-year limited manufacturer's warranty on all {product}s sold by Cymbal Sports. This covers defects in materials and workmanship."},
    {"q": "Can I pick up my {product} order at the store in {city}?", "a": "Absolutely! We offer free in-store pickup at our {city} location. Select 'Store Pickup' at checkout and we'll email you when your {product} is ready."},
    {"q": "Do you offer repair services for {product}?", "a": "We do not offer in-house repair services for {product} at this time. However, we can recommend authorized service centers in the {city} area."},
    {"q": "Is the {product} suitable for beginners?", "a": "Yes, our {product} models are designed to be user-friendly and are an excellent choice for beginners starting their fitness journey."},
    {"q": "How do I care for my {product}?", "a": "To ensure longevity, wipe down your {product} with a damp cloth after use and store it in a cool, dry place. Avoid direct sunlight for extended periods."},
    {"q": "Do you price match on {product}?", "a": "Yes, Cymbal Sports offers a Price Match Guarantee on {product}. If you find a lower price at a qualifying retailer within 14 days of purchase, we will match it."},
    {"q": "Are there any upcoming sales on {product}?", "a": "We frequently have sales on fitness equipment including {product}. Sign up for our newsletter to get alerted about seasonal promotions and flash sales."},
    {"q": "Can I use a gift card to buy {product}?", "a": "Yes, Cymbal Sports gift cards can be used to purchase {product} and any other item in our store, both online and at our {city} location."}
]

ADDITIONAL_CONTENT = {
    "return_policy.txt": """Cymbal Sports Return Policy

At Cymbal Sports, we want you to be completely satisfied with your gear. If you are not 100% satisfied, you can return your items within 30 days of purchase.

Conditions:
- Items must be unused and in original packaging.
- Tags must be attached.
- Proof of purchase is required.

Exceptions:
- Personalized items cannot be returned.
- Gift cards are non-refundable.

How to Return:
1. Online: Log in to your account, visit "Order History", and select "Start a Return". Print the prepaid label and ship.
2. In-Store: Bring your item and receipt to any Cymbal Sports location.

Refunds:
Refunds will be processed to the original payment method within 5-7 business days of receiving the return.""",
    
    "about_us.txt": """About Cymbal Sports

Founded in 2010, Cymbal Sports has grown from a small garage operation to a leading online retailer of premium sporting goods. 

Our Mission:
To inspire the athlete in everyone by providing top-quality gear at accessible prices.

Our Values:
- Integrity: We stand behind every product we sell.
- Innovation: We constantly seek the latest in sports technology.
- Community: We support local sports leagues and fitness initiatives.

Headquarters:
123 Tech Drive, San Francisco, CA 94105

CEO: Jane 'Cymbal' Doe""",

    "sizing_guide.txt": """Cymbal Sports General Sizing Guide

Men's Tops:
- S: Chest 34-36"
- M: Chest 38-40"
- L: Chest 42-44"
- XL: Chest 46-48"

Women's Tops:
- S: Bust 32-34"
- M: Bust 35-37"
- L: Bust 38-40"
- XL: Bust 41-43"

Footwear (US Sizes):
Use our TrueFit technology on the product page for the most accurate recommendation. 
Generally, we recommend sizing up 0.5 for running shoes if you prefer a roomier toe box.

Youth:
Please refer to the specific brand size charts on individual product pages as youth sizing varies significantly by brand."""
}


def create_local_directory():
    if os.path.exists(LOCAL_DIR):
        shutil.rmtree(LOCAL_DIR)
    os.makedirs(LOCAL_DIR)
    print(f"Created local directory: {LOCAL_DIR}")

def generate_faqs(num_files=50):
    for i in range(1, num_files + 1):
        template = random.choice(FAQ_TEMPLATES)
        product = random.choice(PRODUCTS)
        city = random.choice(CITIES)
        
        question = template["q"].format(product=product, city=city)
        answer = template["a"].format(product=product, city=city)
        
        content = f"Question: {question}\nAnswer: {answer}"
        
        filename = f"faq{i}.txt"
        with open(os.path.join(LOCAL_DIR, filename), "w") as f:
            f.write(content)
    print(f"Generated {num_files} FAQ files.")

def generate_locations(num_locations=50):
    lines = []
    lines.append("Cymbal Sports Store Locations Directory")
    lines.append("=======================================\n")
    
    for _ in range(num_locations):
        city = random.choice(CITIES)
        # Simple heuristic to pick a state that "looks" right or just random if not mapped
        state = random.choice(STATES) 
        street = random.choice(STREETS)
        st_num = random.randint(100, 9999)
        zip_code = random.randint(10000, 99999)
        phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        hours = "Mon-Sat: 9am-9pm, Sun: 10am-6pm"
        
        location_entry = f"""
Store: Cymbal Sports {city}
Address: {st_num} {street}, {city}, {state} {zip_code}
Phone: {phone}
Hours: {hours}
---------------------------------------"""
        lines.append(location_entry)
        
    with open(os.path.join(LOCAL_DIR, "locations.txt"), "w") as f:
        f.write("\n".join(lines))
    print(f"Generated locations.txt with {num_locations} locations.")

def generate_additional_content():
    for filename, content in ADDITIONAL_CONTENT.items():
        with open(os.path.join(LOCAL_DIR, filename), "w") as f:
            f.write(content)
    print("Generated additional content (Policies, History, Sizing).")

def upload_to_gcs(bucket_name):
    # Initialize client
    # Note: This expects GOOGLE_APPLICATION_CREDENTIALS to be set or relies on default auth
    storage_client = storage.Client()

    # Create bucket
    try:
        bucket = storage_client.create_bucket(bucket_name, location="US")
        print(f"Created bucket {bucket.name}")
    except Exception as e:
        print(f"Bucket creation failed (might already exist): {e}")
        bucket = storage_client.bucket(bucket_name)

    # Upload files
    files = glob.glob(os.path.join(LOCAL_DIR, "*"))
    for file_path in files:
        blob_name = os.path.basename(file_path)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print(f"Uploaded {blob_name} to {bucket_name}.")

def main():
    # 1. Create local dir
    create_local_directory()
    
    # 2. Generate Content
    generate_faqs(50)
    generate_locations(50)
    generate_additional_content()
    
    # 3. Determine Bucket Name
    # Append 4 random chars to ensure uniqueness as requested
    random_suffix = uuid.uuid4().hex[:4]
    bucket_name = f"{BUCKET_PREFIX}-{random_suffix}"
    print(f"Target Bucket Name: {bucket_name}")
    
    # 4. Upload
    print("Uploading to Google Cloud Storage...")
    try:
        upload_to_gcs(bucket_name)
        print("\nSUCCESS: RAG data generation and upload complete!")
        print(f"Bucket: {bucket_name}")
        print("You can now connect this bucket to your Agent's Data Store.")
    except Exception as e:
        print(f"\nERROR: Failed to upload to GCS. ensure you are authenticated.")
        print(f"Details: {e}")
        print("\nThe files are still available locally in the 'rag_data/' folder.")

if __name__ == "__main__":
    main()
