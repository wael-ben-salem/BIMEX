import json
import os

RESULTS_DIR = "./data/results"

import os
import json
from app.config import RESULTS_DIR

def save_ocr_results(file_id: str, ocr_result: dict,):
    folder_path = os.path.join(RESULTS_DIR, file_id)
    os.makedirs(folder_path, exist_ok=True)
    result_file = os.path.join(folder_path, "ocr_results.json")
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(ocr_result, f, indent=2)

def save_vision_results(file_id: str, vision_result: dict):
    """
    Save vision results (symbols, elements, dimensions, areas) for a given file ID.
    """
    folder_path = os.path.join(RESULTS_DIR, file_id)
    os.makedirs(folder_path, exist_ok=True)
    result_file = os.path.join(folder_path, "vision_results.json")
    
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(vision_result, f, indent=2)
