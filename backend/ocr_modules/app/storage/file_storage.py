# app/storage/file_storage.py
import os
import json
from fastapi import UploadFile

async def save_file_to_disk(file: UploadFile, folder: str, filename: str) -> str:
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    return file_path

def save_metadata_to_json(metadata: dict, folder: str):
    metadata_path = os.path.join(folder, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

BASE_UPLOAD_PATH = "data/uploads"
BASE_RESULTS_PATH = "data/results"

def get_file_path(file_id: str) -> str:
    return os.path.join(BASE_UPLOAD_PATH, file_id)

def save_results(file_id: str, results: dict) -> None:
    os.makedirs(BASE_RESULTS_PATH, exist_ok=True)
    filepath = os.path.join(BASE_RESULTS_PATH, f"{file_id}.json")
    with open(filepath, "w") as f:
        json.dump(results, f)
