import os
import base64
import io
import json
import logging

import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from docx import Document
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
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


class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str


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
            text_parts.append(page.get_text())
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


@app.post("/api/document-analyze", response_model=DocumentResponse)
async def analyze_document(
    request: DocumentRequest,
    x_api_key: str = Header(...),
):
    if not API_SECRET_KEY or x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        file_bytes = base64.b64decode(request.fileBase64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoding")

    try:
        text = extract_text(request.fileType, file_bytes)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(status_code=422, detail=f"Could not extract text: {str(e)}")

    if not text:
        raise HTTPException(status_code=422, detail="No text could be extracted from the document")

    try:
        result = analyse_with_gemini(text)
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
