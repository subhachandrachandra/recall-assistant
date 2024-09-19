# File: recall_assistant/language_model_processing/update_documents.py

import logging

from config import Config
from google.cloud import firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_missing_processed_field():
    firestore_client = firestore.Client(project=Config.GCP_PROJECT)
    articles_collection = firestore_client.collection(Config.FIRESTORE_COLLECTION)

    try:
        # Query documents where 'processed_language_model' field does not exist
        query = articles_collection.where(
            "processed_language_model", "==", firestore.firestore.DELETE_FIELD
        )
        docs = query.stream()
        count = 0
        for doc in docs:
            articles_collection.document(doc.id).update(
                {"processed_language_model": False}
            )
            count += 1
        logger.info(
            f"Updated {count} documents to include 'processed_language_model' field."
        )
    except Exception as e:
        logger.error(f"Error updating documents: {e}")


if __name__ == "__main__":
    update_missing_processed_field()
