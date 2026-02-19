import os
from dotenv import load_dotenv

load_dotenv()

# Google Cloud Configuration
# In Cloud Run, Service Account is auto-detected. Locally, set this path.
# Example: /Users/doug/gcloud-keys/my-service-account.json
# If not set, it will look for default credentials.
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Service URL Configuration
# Used in OpenAPI spec for agents to know where to call
SERVICE_URL = os.getenv("SERVICE_URL", "http://localhost:8080")

# Project ID (Optional check)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

def configure_environment():
    """
    Sets up environment variables if they are not already set.
    """
    if GOOGLE_APPLICATION_CREDENTIALS:
        print(f"Setting credentials from config: {GOOGLE_APPLICATION_CREDENTIALS}")
        # This is required for the google-cloud-firestore library to pick it up
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
    
    # Other setup if needed
    print(f"Service URL configured as: {SERVICE_URL}")

# Execute configuration
configure_environment()
