# File: recall_assistant/pdf_processing/main.py

import logging

from processor import PDFProcessor


def main():
    # Configure logging for the main module
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Starting PDF Processing Pipeline...")

    # Initialize the PDF Processor
    processor = PDFProcessor()

    # Start processing PDFs
    processor.process_pdfs()

    logger.info("PDF Processing Pipeline finished successfully.")


if __name__ == "__main__":
    main()
