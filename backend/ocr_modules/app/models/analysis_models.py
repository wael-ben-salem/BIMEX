from pydantic import BaseModel
from typing import List, Optional

class DetectedSymbol(BaseModel):
    symbol_type: str
    confidence: float
    bbox: List[int]

class DetectedElement(BaseModel):
    element_type: str
    confidence: float
    bbox: List[int]

class VisionResult(BaseModel):
    file_id: str
    symbols: List[DetectedSymbol]
    elements: List[DetectedElement]
    processing_time: float



