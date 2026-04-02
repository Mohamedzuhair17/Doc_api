from pydantic import BaseModel
from typing import Optional, Any

class DocumentRequest(BaseModel):
    file_base64: str
    file_type: str  # "pdf", "docx", or "image"

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None

class AnalysisResult(BaseModel):
    summary: str
    key_points: list[str]

