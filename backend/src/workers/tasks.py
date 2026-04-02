"""
Celery Worker Tasks
Handles async processing to prevent API timeouts.
"""

from src.workers.celery_app import celery_app
from src.services.smart_extractor import SmartExtractor
from src.services.ai_engine import SmartAIEngine
from src.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

extractor = SmartExtractor()
ai_engine = SmartAIEngine(api_key=settings.GEMINI_API_KEY)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_document(self, file_base64: str, file_type: str, task_id: str):
    """
    Main document processing pipeline.
    
    Flow:
    1. Extract text using Tesseract (compliance)
    2. Correct OCR errors using Gemini (accuracy)
    
    Args:
        file_base64: Document as Base64 string
        file_type: "pdf", "docx", or "image"
        task_id: Unique task identifier
    """
    
    try:
        logger.info(f"Task {task_id}: Starting processing of {file_type}")
        
        # Step 1: Extract text (uses Tesseract as required)
        logger.info(f"Task {task_id}: Extracting text...")
        raw_text = extractor.extract_from_file(file_base64, file_type)
        logger.info(f"Task {task_id}: Extracted {len(raw_text)} characters")
        
        # Step 2: Correct OCR errors and extract entities (Gemini)
        logger.info(f"Task {task_id}: Analyzing with AI correction...")
        result = ai_engine.analyze_with_correction(raw_text)
        logger.info(f"Task {task_id}: Analysis complete - sentiment: {result['sentiment']}")
        
        # Return result (will be stored in Celery backend / Redis)
        return {
            "status": "completed",
            "result": result,
            "task_id": task_id
        }
    
    except Exception as exc:
        logger.error(f"Task {task_id}: Error - {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
