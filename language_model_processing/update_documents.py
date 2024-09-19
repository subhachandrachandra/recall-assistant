# File: recall_assistant/language_model_processing/update_existing_documents.py

import logging

from config import Config
from google.cloud import firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_processed_language_model_field():
    """Add 'processed_language_model' field set to False for all documents that lack it."""
    try:
        firestore_client = firestore.Client(project=Config.GCP_PROJECT)
        articles_collection = firestore_client.collection(Config.FIRESTORE_COLLECTION)

        # Query all documents in the collection
        docs = articles_collection.stream()
        update_count = 0

        for doc in docs:
            doc_dict = doc.to_dict()
            if "processed_language_model" not in doc_dict:
                # Update the document to include the field
                articles_collection.document(doc.id).update(
                    {"processed_language_model": False}
                )
                logger.info(
                    f"Updated document '{doc.id}' with 'processed_language_model': False"
                )
                update_count += 1

        logger.info(f"Total documents updated: {update_count}")

    except Exception as e:
        logger.error(f"Error updating documents: {e}")


if __name__ == "__main__":
    add_processed_language_model_field()
