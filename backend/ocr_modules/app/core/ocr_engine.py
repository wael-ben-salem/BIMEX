import time
from typing import List, Tuple
from app.processors.text_extractor import TextExtractor
from app.models.ocr_models import OCRTextItem
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

LLM_API_KEY = os.getenv("GROQ_API_KEY")
if not LLM_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")


def perform_ocr(
    file_path: str,
    languages: List[str] = ["eng"],
    use_llm: bool = True
) -> Tuple[List[OCRTextItem], float]:
    """
    Perform OCR on an image or PDF using TextExtractor.
    Can optionally use an LLM to classify types and filter irrelevant text.
    Returns extracted OCR items and processing time.
    """
    print(os.getenv("GROQ_API_KEY"))

    start_time = time.time()
    extractor = TextExtractor(use_llm=use_llm, groq_api_key=LLM_API_KEY)
    extracted_text = extractor.extract_text(file_path, languages)

    end_time = time.time()
    processing_time = round(end_time - start_time, 2)

    return extracted_text, processing_time
