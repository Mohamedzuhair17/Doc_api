import base64
import io
import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def extract_text(file_b64: str, file_name: str) -> str:
    """Decodes base64 and extracts text based on file extension."""
    
    # Handle base64 prefix if present
    if "," in file_b64:
        file_b64 = file_b64.split(",")[1]
        
    try:
        file_bytes = base64.b64decode(file_b64)
    except Exception as e:
        logger.error(f"Base64 decoding failed: {str(e)}")
        raise ValueError("Invalid Base64 string")
        
    ext = file_name.split('.')[-1].lower()
    text = ""

    try:
        if ext == "pdf":
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text += page.get_text()
                
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        elif ext in ["png", "jpg", "jpeg"]:
            image = Image.open(io.BytesIO(file_bytes))
            # Basic OCR extraction
            text = pytesseract.image_to_string(image)
            
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        return text.strip()
    except Exception as e:
        logger.exception(f"Text extraction failed for {file_name}")
        raise Exception(f"Extraction failed: {str(e)}")
