import os
import base64
import io
import json
import logging
from typing import Optional

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from docx import Document
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, AliasChoices, model_validator
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
FLASH_MODEL_CANDIDATES = [
    model_name.strip()
    for model_name in os.environ.get(
        "GEMINI_FLASH_MODELS",
        "gemini-2.0-flash-lite,gemini-2.0-flash,gemini-1.5-flash",
    ).split(",")
    if model_name.strip()
]

app = FastAPI(title="DocAI", version="1.0.0")

origins = [
    "https://doc-api-nu.vercel.app",
    "https://doc-api-git-main-mohamedzuhair17s-projects.vercel.app",
    "https://doc-6hkam2osk-mohamedzuhair17s-projects.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_SECRET_KEY = os.environ.get("API_SECRET_KEY", "")
API_SECRET_KEYS = {
    key.strip()
    for key in os.environ.get("API_SECRET_KEYS", "").split(",")
    if key.strip()
}
if API_SECRET_KEY:
    API_SECRET_KEYS.add(API_SECRET_KEY)


class DocumentRequest(BaseModel):
    fileName: str = Field(validation_alias=AliasChoices("fileName", "filename", "name"))
    fileType: str = Field(validation_alias=AliasChoices("fileType", "file_type", "type"))
    fileBase64: str = Field(validation_alias=AliasChoices("fileBase64", "file_base64", "file"))

    @model_validator(mode="before")
    @classmethod
    def normalize_payload(cls, data):
        if not isinstance(data, dict):
            return data

        # Normalize camelCase/snake_case and common legacy keys.
        normalized = dict(data)
        if "fileName" not in normalized:
            if "filename" in normalized:
                normalized["fileName"] = normalized["filename"]
            elif "name" in normalized:
                normalized["fileName"] = normalized["name"]
        if "fileType" not in normalized:
            if "file_type" in normalized:
                normalized["fileType"] = normalized["file_type"]
            elif "type" in normalized:
                normalized["fileType"] = normalized["type"]
        if "fileBase64" not in normalized:
            if "file_base64" in normalized:
                normalized["fileBase64"] = normalized["file_base64"]
            elif "file" in normalized:
                normalized["fileBase64"] = normalized["file"]

        # Accept full Data URL and keep only raw base64 payload.
        maybe_base64 = normalized.get("fileBase64")
        if isinstance(maybe_base64, str) and maybe_base64.startswith("data:") and "," in maybe_base64:
            normalized["fileBase64"] = maybe_base64.split(",", 1)[1]

        return normalized


class EntitiesResponse(BaseModel):
    names: list[str]
    dates: list[str]
    organizations: list[str]
    amounts: list[str]


class DocumentResponse(BaseModel):
    status: str
    fileName: str
    summary: str
    entities: EntitiesResponse
    sentiment: str


def extract_text_pdf(data: bytes) -> str:
    text_parts = []
    with fitz.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                text_parts.append(page_text)
                continue

            # Fallback for scanned/image-only PDFs.
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                image = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(image).strip()
                if ocr_text:
                    text_parts.append(ocr_text)
            except Exception as e:
                logger.warning(f"OCR fallback failed for PDF page {page.number + 1}: {e}")
    return "\n".join(text_parts).strip()


def extract_text_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_image(data: bytes) -> str:
    image = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(image).strip()


def extract_text(file_type: str, data: bytes) -> str:
    ft = file_type.lower().strip()
    if ft == "pdf":
        return extract_text_pdf(data)
    if ft == "docx":
        return extract_text_docx(data)
    if ft in ("image", "png", "jpg", "jpeg", "tiff", "bmp"):
        return extract_text_image(data)
    raise HTTPException(status_code=400, detail=f"Unsupported fileType: {file_type}")


def analyse_with_gemini(text: str) -> dict:
    prompt = f"""
You are a document analysis AI. Analyse the following document text and return a JSON object with EXACTLY this structure - no markdown, no code fences, raw JSON only:

{{
  "summary": "A concise 2-3 sentence summary of the document.",
  "entities": {{
    "names": ["list of person names found"],
    "dates": ["list of dates found"],
    "organizations": ["list of organization names found"],
    "amounts": ["list of monetary amounts found"]
  }},
  "sentiment": "Positive or Neutral or Negative"
}}

Rules:
- summary: concise, factual, 2-3 sentences max
- entities: extract only what actually appears in the text; use empty list [] if none found
- sentiment: must be exactly one of: Positive, Neutral, Negative

Document text:
\"\"\"
{text[:8000]}
\"\"\"
"""
    response = None
    last_error = None
    selected_model = None
    for model_name in FLASH_MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            selected_model = model_name
            break
        except Exception as e:
            last_error = e
            logger.warning(f"Flash model unavailable: {model_name} ({e})")

    if response is None:
        raise RuntimeError(f"No available Flash model found: {last_error}")

    logger.info(f"Gemini analysis model: {selected_model}")
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


def infer_mime_type(file_type: str, file_name: str) -> str:
    ft = (file_type or "").lower().strip()
    ext = (file_name.rsplit(".", 1)[-1] if "." in file_name else "").lower()

    if ft == "pdf" or ext == "pdf":
        return "application/pdf"
    if ft == "docx" or ext == "docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if ft in ("png",) or ext == "png":
        return "image/png"
    if ft in ("jpg", "jpeg") or ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ft in ("tif", "tiff") or ext in ("tif", "tiff"):
        return "image/tiff"
    if ft in ("bmp",) or ext == "bmp":
        return "image/bmp"
    if ft == "image":
        return "image/png"
    return "application/octet-stream"


def analyse_with_gemini_file(file_bytes: bytes, mime_type: str) -> dict:
    prompt = """
You are a document analysis AI.
Analyse the attached document and return a JSON object with EXACTLY this structure - no markdown, no code fences, raw JSON only:

{
  "summary": "A concise 2-3 sentence summary of the document.",
  "entities": {
    "names": ["list of person names found"],
    "dates": ["list of dates found"],
    "organizations": ["list of organization names found"],
    "amounts": ["list of monetary amounts found"]
  },
  "sentiment": "Positive or Neutral or Negative"
}

Rules:
- summary: concise, factual, 2-3 sentences max
- entities: extract only what actually appears in the document; use empty list [] if none found
- sentiment: must be exactly one of: Positive, Neutral, Negative
"""
    response = None
    last_error = None
    selected_model = None
    for model_name in FLASH_MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                ],
            )
            selected_model = model_name
            break
        except Exception as e:
            last_error = e
            logger.warning(f"Flash model unavailable for file analysis: {model_name} ({e})")

    if response is None:
        raise RuntimeError(f"No available Flash model found for file analysis: {last_error}")

    logger.info(f"Gemini file analysis model: {selected_model}")
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)


@app.post("/api/document-analyze", response_model=DocumentResponse)
async def analyze_document(
    request: DocumentRequest,
    x_api_key: Optional[str] = Header(default=None),
):
    if not API_SECRET_KEYS:
        raise HTTPException(status_code=500, detail="API keys are not configured on server")

    if not x_api_key or x_api_key not in API_SECRET_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        file_bytes = base64.b64decode(request.fileBase64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

    text = ""
    extraction_error = None
    try:
        text = extract_text(request.fileType, file_bytes)
    except HTTPException:
        raise
    except Exception as e:
        extraction_error = str(e)
        logger.warning(f"Text extraction failed, falling back to Gemini file analysis: {e}")

    try:
        if text:
            result = analyse_with_gemini(text)
        else:
            if extraction_error:
                logger.info(f"Proceeding with file-level analysis after extraction issue: {extraction_error}")
            mime_type = infer_mime_type(request.fileType, request.fileName)
            result = analyse_with_gemini_file(file_bytes, mime_type)
    except json.JSONDecodeError as e:
        logger.error(f"Gemini returned invalid JSON: {e}")
        raise HTTPException(status_code=500, detail="AI analysis returned invalid response")
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return DocumentResponse(
        status="success",
        fileName=request.fileName,
        summary=result.get("summary", ""),
        entities=EntitiesResponse(
            names=result.get("entities", {}).get("names", []),
            dates=result.get("entities", {}).get("dates", []),
            organizations=result.get("entities", {}).get("organizations", []),
            amounts=result.get("entities", {}).get("amounts", []),
        ),
        sentiment=result.get("sentiment", "Neutral"),
    )


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"status": "ok", "service": "DocAI"}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}
