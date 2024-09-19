# File: recall_assistant/language_model_processing/config.py

import os

from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Firestore Configuration (reuse from PDF Processing)
    GCP_PROJECT = os.getenv("GCP_PROJECT")
    FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "articles")

    # Other Configurations
    LANGUAGE_MODEL_PROCESSED_FIELD = os.getenv(
        "LANGUAGE_MODEL_PROCESSED_FIELD", "processed_language_model"
    )
