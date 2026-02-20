import os
import csv
import time
from google.cloud import storage
# Import the new Google Gen AI SDK
from google import genai
from google.genai import types

# --- Configuration ---
# Project ID is often needed for Vertex AI initialization even with default creds
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "gcloud-interactive-courses")
LOCATION = "us-central1"
BUCKET_NAME = "cymbal-sports-prod-images-dar"
INVENTORY_FILE = "app/data/inventory.csv"
MODEL_NAME = "gemini-2.5-flash-image"

def generate_image(client, prompt, output_file):
    """Generates an image with exponential backoff for 429 errors."""
    max_retries = 5
    delay = 2  # Initial delay
    
    for attempt in range(max_retries):
        try:
            print(f"Generating image for prompt: {prompt[:50]}... (Attempt {attempt+1}/{max_retries})")
            
            # Configuration adapted from your Vertex AI Studio sample
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                max_output_tokens=8192,
                response_modalities=["IMAGE"], 
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
                ],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                    output_mime_type="image/png",
                ),
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt)
                    ]
                ),
            ]
            
            # Call the model
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=generate_content_config,
            )

            # Handle formatting of response to get image bytes
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            # Extract image bytes (inline_data is where genai SDK puts it)
                            if part.inline_data:
                                # Save the image bytes
                                with open(output_file, "wb") as f:
                                    # Data comes as bytes typically
                                    f.write(part.inline_data.data)
                                print(f"Saved local image: {output_file}")
                                return True
            
            print(f"No image data found in response.")
            return False
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                print(f"Rate limit hit (429). Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print(f"Error generating image: {e}")
                return False

    print("Max retries exceeded for image generation.")
    return False

def upload_to_gcs(bucket, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"Uploaded {source_file_name} to gs://{bucket.name}/{destination_blob_name}")

def main():
    print(f"Initializing Vertex AI Client for project: {PROJECT_ID}, location: {LOCATION}")
    
    # Initialize the Gen AI client with Vertex AI enabled (uses ADC)
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )
    
    # Initialize GCS
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        try:
            bucket = storage_client.get_bucket(BUCKET_NAME)
            print(f"Found bucket: {BUCKET_NAME}")
        except Exception as e:
            print(f"Bucket {BUCKET_NAME} not found. Creating it...")
            try:
                bucket = storage_client.create_bucket(BUCKET_NAME, location="US")
                print(f"Created bucket: {BUCKET_NAME}")
            except Exception as create_error:
                print(f"Error creating bucket: {create_error}")
                # Fallback to just getting the bucket ref if creation fails (maybe permissions/exists)
                bucket = storage_client.bucket(BUCKET_NAME)
    except Exception as e:
        print(f"Could not initialize GCS client: {e}")
        return

    # Read Inventory
    with open(INVENTORY_FILE, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        items = list(csv_reader)

    # Process first 3 items for testing
    count = 0
    limit = 300 
    
    # Create a temp directory for images
    os.makedirs("generated_images", exist_ok=True)

    for item in items:
        if count >= limit:
            break
            
        sku = item['id']
        title = item['title']
        description = item['description']
        category = item['category']
        
        # Prompt Engineering
        prompt = f"Professional studio product photography of a {title}. {description}. The item is a high-quality sporting good for {category}. Clean white background, 4k, ultra-realistic."
        
        local_filename = f"generated_images/{sku}.png"
        gcs_filename = f"{sku}.png"

        # Check if exists in GCS
        blob = bucket.blob(gcs_filename)
        if blob.exists():
            print(f"Image {gcs_filename} already exists in GCS. Skipping.")
            continue
        
        # Generate & Upload
        if generate_image(client, prompt, local_filename):
            upload_to_gcs(bucket, local_filename, gcs_filename)
        
        # Rate limiting
        time.sleep(2)
        count += 1
        
    print("\nTest complete! Check your GCS bucket.")

if __name__ == "__main__":
    main()
