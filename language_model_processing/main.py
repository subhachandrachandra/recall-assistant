# File: recall_assistant/language_model_processing/main.py

import logging

from processor import LanguageModelProcessor


def main():
    # Configure logging for the main module
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting Language Model Processing...")

    # Initialize the Language Model Processor
    processor = LanguageModelProcessor()

    # Start processing articles
    processor.process_articles()

    logger.info("Language Model Processing finished successfully.")


if __name__ == "__main__":
    main()
