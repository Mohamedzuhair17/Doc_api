"""
FastAPI Backend with Caching
Returns task ID immediately (no timeout risk).
"""

from fastapi import FastAPI, Header, HTTPException, status, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.api.schemas import DocumentRequest, TaskResponse
from src.core.config import settings
from celery.result import AsyncResult
import redis
import json
import uuid
import os
import logging
import base64

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced Document AI API",
    version="1.0",
    description="Production-grade document processing with OCR correction"
)

# Enable CORS for local frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000", "https://doc-mcy2e530p-mohamedzuhair17s-projects.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client for direct cache access if needed, 
# although Celery handles task result storage in Redis.
redis_client = redis.from_url(settings.CELERY_RESULT_BACKEND)

# Middleware-like verification
async def verify_api_key(x_api_key: str = Header(...)):
    """Validate API key from header."""
    if x_api_key != settings.API_SECRET_KEY:
        logger.warning(f"Unauthorized access attempt with key: {x_api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key


@app.post("/api/document-analyze", status_code=202, response_model=TaskResponse)
async def analyze_document(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
) -> TaskResponse:
    """
    Analyze document (async).
    
    Returns immediately with task ID. Processing happens in background.
    """
    
    # Import worker lazily so docs/root can boot even if worker-only deps
    # are unavailable in serverless environments.
    from src.workers.tasks import process_document

    # Read file content
    content = await file.read()
    file_base64 = base64.b64encode(content).decode('utf-8')
    
    # Determine file type from filename
    filename = file.filename or ""
    if filename.lower().endswith('.pdf'):
        file_type = 'pdf'
    elif filename.lower().endswith('.docx'):
        file_type = 'docx'
    else:
        file_type = 'image'

    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Queue task with the generated ID
    process_document.apply_async(
        args=[file_base64, file_type, task_id],
        task_id=task_id
    )
    
    logger.info(f"Task {task_id} queued for {file_type}")
    
    return TaskResponse(
        task_id=task_id,
        status="queued"
    )


@app.get("/api/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str, 
    api_key: str = Depends(verify_api_key)
):
    """Get task status and result."""
    
    # Use Celery's AsyncResult to retrieve task information
    result = AsyncResult(task_id)
    
    if result.state == 'PENDING':
        return TaskResponse(task_id=task_id, status="queued")
    elif result.state == 'STARTED':
        return TaskResponse(task_id=task_id, status="processing")
    elif result.state == 'SUCCESS':
        data = result.result
        return TaskResponse(
            task_id=task_id,
            status="completed",
            result=data.get("result")
        )
    elif result.state == 'FAILURE':
        logger.error(f"Task {task_id} failed: {result.info}")
        return TaskResponse(task_id=task_id, status="failed")
    else:
        return TaskResponse(task_id=task_id, status=result.state.lower())


@app.get("/")
async def root():
    """Simple root endpoint to avoid 404 on /."""
    return {"message": "Document AI backend running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
