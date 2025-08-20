from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

router = APIRouter()
BASE_RESULTS_DIR = Path("data/results")

def load_results(file_id: str) -> dict:
    results_path = BASE_RESULTS_DIR / f"{file_id}.json"
    if not results_path.exists():
        raise HTTPException(status_code=404, detail=f"Results for file_id '{file_id}' not found.")
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/results/{file_id}")
async def get_all_results(file_id: str):
    """Return the entire JSON results for a file."""
    return load_results(file_id)

@router.get("/results/{file_id}/text")
async def get_text_results(file_id: str):
    """Return everything under ocr.results."""
    data = load_results(file_id)
    return data.get("ocr", {}).get("results", [])

@router.get("/results/{file_id}/dimensions")
async def get_dimensions_results(file_id: str):
    """Return only OCR results where type == 'dimension'."""
    data = load_results(file_id)
    ocr_results = data.get("ocr", {}).get("results", [])
    return [item for item in ocr_results if item.get("type") == "dimension"]

@router.get("/results/{file_id}/symbols")
async def get_symbols_results(file_id: str):
    """Return vision.symbols."""
    data = load_results(file_id)
    return data.get("vision", {}).get("symbols", [])

@router.get("/results/{file_id}/elements")
async def get_elements_results(file_id: str):
    """Return vision.elements."""
    data = load_results(file_id)
    return data.get("vision", {}).get("elements", [])
