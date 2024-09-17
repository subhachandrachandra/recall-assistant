# File: recall_assistant/pdf_processing/config.py

import os

from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


class Config:
    # Google Cloud Configuration
    GCP_PROJECT = os.getenv("GCP_PROJECT")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "articles")

    # LlamaParse Configuration
    LLAMAPARSE_API_URL = os.getenv("LLAMAPARSE_API_URL")
    LLAMAPARSE_API_KEY = os.getenv("LLAMAPARSE_API_KEY")

    # Firestore Credentials
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # OpenAI Key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Other Configurations
    PROCESSED_FILES_COLLECTION = os.getenv(
        "PROCESSED_FILES_COLLECTION", "processed_files"
    )
