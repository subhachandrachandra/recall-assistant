# File: recall_assistant/pdf_processing/processor.py

import io
import logging

import requests
from config import Config
from google.api_core.exceptions import NotFound
from google.cloud import firestore, storage
from llama_parse import LlamaParse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        # Initialize Google Cloud Storage client
        self.storage_client = storage.Client(project=Config.GCP_PROJECT)
        self.bucket = self.storage_client.bucket(Config.GCS_BUCKET_NAME)

        # Initialize Firestore client
        self.firestore_client = firestore.Client(project=Config.GCP_PROJECT)
        self.articles_collection = self.firestore_client.collection(
            Config.FIRESTORE_COLLECTION
        )
        self.processed_files_collection = self.firestore_client.collection(
            Config.PROCESSED_FILES_COLLECTION
        )

        # LlamaParse Configuration
        self.llamaparse_url = Config.LLAMAPARSE_API_URL
        self.llamaparse_api_key = Config.LLAMAPARSE_API_KEY

    def list_pdf_files(self):
        """List all PDF files in the GCS bucket."""
        blobs = self.bucket.list_blobs()
        pdf_files = [blob.name for blob in blobs if blob.name.lower().endswith(".pdf")]
        logger.info(f"Found {len(pdf_files)} PDF files in the bucket.")
        return pdf_files

    def is_file_processed(self, file_name):
        """Check if the file has already been processed."""
        try:
            doc = self.processed_files_collection.document(file_name).get()
            return doc.exists
        except Exception as e:
            logger.error(f"Error checking if file is processed: {e}")
            return False

    def mark_file_as_processed(self, file_name):
        """Mark the file as processed in Firestore."""
        try:
            self.processed_files_collection.document(file_name).set({"processed": True})
            logger.info(f"Marked '{file_name}' as processed.")
        except Exception as e:
            logger.error(f"Error marking file as processed: {e}")

    def download_pdf(self, file_name):
        """Download the PDF file from GCS."""
        try:
            blob = self.bucket.blob(file_name)
            pdf_bytes = blob.download_as_bytes()
            logger.info(f"Downloaded '{file_name}' from bucket.")
            return pdf_bytes
        except Exception as e:
            logger.error(f"Error downloading '{file_name}': {e}")
            return None

    def convert_pdf_to_markdown(self, pdf_bytes, file_name):
        """Convert PDF bytes to Markdown using LlamaParse."""
        try:
            parser = LlamaParse(
                result_type="markdown",  # "markdown" and "text" are available,
                do_not_cache=True,
                split_by_page=False,
                gpt4o_mode=True,
                gpt4o_api_key=Config.OPENAI_API_KEY,
                page_separator="",
            )
            md = parser.load_data(pdf_bytes, extra_info={"file_name": file_name})
            markdown_content = md[0].text
            logger.info("Successfully converted PDF to Markdown.")
            return markdown_content
        except requests.exceptions.RequestException as e:
            logger.error(f"LlamaParse API request failed: {e}")
            return None

    def save_markdown_to_firestore(self, file_name, markdown_content):
        """Save the Markdown content and metadata to Firestore."""
        try:
            # Extract metadata from file name or content as needed
            # For simplicity, using file name as title
            article_data = {
                "title": file_name.replace(".pdf", ""),
                "markdown": markdown_content,
                "source": "GCS Bucket",
                "file_name": file_name,
            }
            self.articles_collection.document(file_name).set(article_data)
            logger.info(f"Saved Markdown content of '{file_name}' to Firestore.")
        except Exception as e:
            logger.error(f"Error saving Markdown to Firestore: {e}")

    def process_pdfs(self):
        """Main method to process unprocessed PDF files."""
        pdf_files = self.list_pdf_files()
        unprocessed_files = [f for f in pdf_files if not self.is_file_processed(f)]

        logger.info(f"Processing {len(unprocessed_files)} unprocessed PDF files.")

        for file_name in unprocessed_files:
            logger.info(f"Processing file: {file_name}")

            # Download PDF
            pdf_bytes = self.download_pdf(file_name)
            if not pdf_bytes:
                continue

            # Convert to Markdown
            markdown = self.convert_pdf_to_markdown(pdf_bytes, file_name)
            if not markdown:
                continue

            # Save to Firestore
            self.save_markdown_to_firestore(file_name, markdown)

            # Mark as processed
            self.mark_file_as_processed(file_name)

        logger.info("PDF processing completed.")
