# app/utils/validation.py
from fastapi import HTTPException

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".dwg", ".dxf"}

def validate_file_type(filename: str):
    ext = filename.lower().split(".")[-1]
    if f".{ext}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{ext}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
