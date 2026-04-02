"""
Smart AI Engine with OCR Error Correction

Key insight: Gemini's language model can "fix" Tesseract typos
using context. Example:
  Tesseract: "The contract va1ue is $5 mi11ion"
  Gemini: "The contract value is $5 million"
"""

from google import genai
from google.genai import types
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SmartAIEngine:
    """
    Gemini-powered extraction with OCR error correction.
    
    Uses a specialized system prompt to:
    1. Correct common OCR errors (5→S, 0→O, 1→l)
    2. Extract structured entities
    3. Classify sentiment accurately
    """
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize AI engine.
        
        Args:
            api_key: Gemini API key
            model: Optional Gemini model override
        """
        self.client = genai.Client(api_key=api_key)
        self.model_candidates = [model] if model else [
            "gemini-flash-latest",
            "gemini-2.0-flash",
        ]
        self.model_name = self.model_candidates[0]
    
    def analyze_with_correction(self, ocr_text: str) -> dict:
        """
        Analyze OCR text with intelligent error correction.
        
        This is the WINNING technique:
        1. Admit the text came from OCR
        2. Ask Gemini to fix typos using context
        3. Then extract entities and sentiment
        
        Args:
            ocr_text: Raw text from Tesseract (may have errors)
        
        Returns:
            dict: {summary, entities, sentiment}
        """
        
        # Build the user prompt
        user_prompt = f"""
Below is text extracted from a document using OCR technology. 
OCR can make mistakes (like reading 'S' as '5', 'l' as '1', 'O' as '0').

Your task:
1. CORRECT common OCR errors using context clues
2. EXTRACT entities (names, dates, organizations, amounts)
3. CLASSIFY sentiment (Positive, Neutral, Negative)

OCR TEXT:
{ocr_text}

CRITICAL: Return ONLY valid JSON, no markdown, no explanation:
{{
  "summary": "2-3 sentence overview",
  "entities": {{
    "names": ["list of people"],
    "organizations": ["list of companies"],
    "dates": ["list of dates"],
    "amounts": ["list of monetary values"]
  }},
  "sentiment": "Positive|Neutral|Negative"
}}
"""
        
        try:
            # Call Gemini with fallback model handling
            result = self._generate_with_fallback(user_prompt)
            
            # Validate required fields
            if "summary" not in result or "entities" not in result or "sentiment" not in result:
                raise ValueError(f"Missing required fields in response")
            
            logger.info(f"Analysis successful - sentiment: {result['sentiment']}")
            return result
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    def _generate_with_fallback(self, user_prompt: str) -> dict:
        last_exc = None

        for model_name in self.model_candidates:
            try:
                if model_name != self.model_name:
                    logger.warning(f"Switching Gemini model from {self.model_name} to {model_name}")
                    self.model_name = model_name

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self._get_correction_system_prompt(),
                        response_mime_type="application/json",
                    ),
                )
                return json.loads(response.text)
            except Exception as exc:
                last_exc = exc
                error_text = str(exc).lower()
                # Keep trying only when model availability is the issue.
                if "not found" in error_text or "is not supported" in error_text:
                    continue
                raise

        raise last_exc if last_exc else RuntimeError("Gemini request failed without a specific error")
    
    def _get_correction_system_prompt(self) -> str:
        """
        System prompt that teaches Gemini to correct OCR errors.
        
        This is why the hybrid approach wins:
        - Tesseract handles the requirement
        - Gemini handles the accuracy
        """
        
        return """You are a legal and document expert with deep knowledge of:
- Contract analysis
- Financial documents
- Government documents
- Invoice and receipt processing

Your specialty: Correcting OCR (Optical Character Recognition) extraction errors.

COMMON OCR ERRORS TO WATCH FOR:
- 'S' misread as '5' → "va1ue" should be "value"
- 'l' (lowercase L) misread as '1' → "5 mi11ion" should be "5 million"
- 'O' misread as '0' → "c0ntract" should be "contract"
- 'a' misread as 'd' → "the" sometimes becomes "tbe"
- Missing spaces → "John Smith" becomes "JohnSmith"

CORRECTION STRATEGY:
1. Read the entire text to understand context
2. Identify obvious OCR errors based on:
   - Known words and phrases
   - Grammatical patterns
   - Domain-specific terminology (contracts, invoices, etc.)
3. Replace errors with corrected versions
4. Preserve the original meaning and intent

IMPORTANT:
- Do NOT hallucinate information that isn't there
- Do NOT change names or numbers unless you're certain it's an OCR error
- Use context (surrounding words) to guide corrections
- When uncertain, keep the original text

EXTRACTION REQUIREMENTS:
- Summary: 2-3 sentences capturing the essence
- Entities: Names, organizations, dates, monetary amounts
- Sentiment: Based on overall tone (not just keywords)

OUTPUT: Valid JSON only, no explanations."""
