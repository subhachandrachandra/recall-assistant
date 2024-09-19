# File: recall_assistant/language_model_processing/processor.py

import logging

import openai
from config import Config
from google.api_core.exceptions import NotFound
from google.cloud import firestore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LanguageModelProcessor:
    def __init__(self):
        # Initialize Firestore client
        self.firestore_client = firestore.Client(project=Config.GCP_PROJECT)
        self.articles_collection = self.firestore_client.collection(
            Config.FIRESTORE_COLLECTION
        )

        # Initialize OpenAI API
        openai.api_key = Config.OPENAI_API_KEY

    def fetch_unprocessed_articles(self):
        """Retrieve articles that have not been processed by the language model."""
        try:
            query = self.articles_collection.where(
                Config.LANGUAGE_MODEL_PROCESSED_FIELD, "==", False
            )
            docs = query.stream()
            articles = [doc for doc in docs]
            logger.info(f"Found {len(articles)} unprocessed articles.")
            return articles
        except Exception as e:
            logger.error(f"Error fetching unprocessed articles: {e}")
            return []

    def generate_summary(self, markdown_text):
        """Generate a summary for the given markdown text using OpenAI GPT-4o."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes articles.",
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following article:\n\n{markdown_text}",
                    },
                ],
                max_tokens=150,
                temperature=0.5,
            )
            summary = response.choices[0].message["content"].strip()
            logger.info("Generated summary.")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None

    def extract_metadata_and_keywords(self, markdown_text, file_name):
        """Extract metadata and generate keywords using OpenAI GPT-4o."""
        try:
            prompt = (
                "Extract the following metadata from the article text and file name:\n"
                "- Title\n"
                "- Author\n"
                "- Publication Date\n"
                "- Keywords (comma-separated)\n\n"
                "- Publication Name (like Economist, MIT Technology Review)"
                f"File Name: {file_name}\n"
                f"Article Text: {markdown_text}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that extracts metadata and generates keywords for articles.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.5,
            )
            metadata_text = response.choices[0].message["content"].strip()
            metadata = self.parse_metadata(metadata_text)
            logger.info("Extracted metadata and generated keywords.")
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata and keywords: {e}")
            return None

    def parse_metadata(self, metadata_text):
        """Parse the metadata text returned by OpenAI into a dictionary."""
        metadata = {}
        try:
            lines = metadata_text.split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    if key == "keywords":
                        # Split keywords into a list
                        metadata[key] = [kw.strip() for kw in value.split(",")]
                    else:
                        metadata[key] = value
            return metadata
        except Exception as e:
            logger.error(f"Error parsing metadata: {e}")
            return {}

    def update_article(self, doc_ref, summary, metadata):
        """Update the Firestore document with the summary and metadata."""
        try:
            update_data = {
                "summary": summary,
                "metadata": metadata,
                Config.LANGUAGE_MODEL_PROCESSED_FIELD: True,
            }
            self.firestore_client.collection(Config.FIRESTORE_COLLECTION).document(
                doc_ref.id
            ).update(update_data)
            logger.info(f"Updated article '{doc_ref.id}' with summary and metadata.")
        except Exception as e:
            logger.error(f"Error updating article '{doc_ref.id}': {e}")

    def process_articles(self):
        """Main method to process unprocessed articles."""
        articles = self.fetch_unprocessed_articles()
        for doc in articles:
            try:
                data = doc.to_dict()
                markdown_text = data.get("markdown", "")
                file_name = data.get("file_name", "Unknown")

                if not markdown_text:
                    logger.warning(
                        f"Article '{doc.id}' has no markdown content. Skipping."
                    )
                    continue

                # Generate summary
                summary = self.generate_summary(markdown_text)
                if not summary:
                    logger.warning(
                        f"Failed to generate summary for article '{doc.id}'. Skipping."
                    )
                    continue

                # Extract metadata and generate keywords
                metadata = self.extract_metadata_and_keywords(markdown_text, file_name)
                if not metadata:
                    logger.warning(
                        f"Failed to extract metadata for article '{doc.id}'. Skipping."
                    )
                    continue

                # Update Firestore with summary and metadata
                self.update_article(doc, summary, metadata)

            except Exception as e:
                logger.error(f"Error processing article '{doc.id}': {e}")

        logger.info("Language Model Processing completed.")
