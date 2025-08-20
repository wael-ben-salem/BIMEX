from pydantic import BaseModel
from typing import List, Optional

class ProcessingOptions(BaseModel):
    enable_ocr: bool = True
    enable_vision: bool = True
    languages: Optional[List[str]] = ['eng']  # Tesseract languages
    use_llm: bool = True

class OCRTextItem(BaseModel):
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float = 100.0
    type: str = "label"  # default to "label"

class OCRResult(BaseModel):
    file_id: str
    extracted_text: List[OCRTextItem]
    processing_time: float
    
class DetectedSymbolModel(BaseModel):
    name: str
    bbox: List[int]  # [x_min, y_min, x_max, y_max]
    confidence: float

class DetectedElementModel(BaseModel):
    element_type: str
    bbox: List[int]
    confidence: Optional[float] = None