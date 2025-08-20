import uuid
import os
import json
import shutil
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from app.utils.validation import validate_file_type
from app.storage.file_storage import save_file_to_disk, save_metadata_to_json
from app.utils.image_utils import generate_thumbnail

UPLOAD_DIR = "data/uploads"

async def process_uploaded_file(file: UploadFile) -> dict:
    validate_file_type(file.filename)

    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1].lower()
    file_dir = os.path.join(UPLOAD_DIR, file_id)
    os.makedirs(file_dir, exist_ok=True)

    saved_path = await save_file_to_disk(file, file_dir, f"original{file_ext}")

    file_size_kb = round(os.path.getsize(saved_path) / 1024, 2)

    file_type = classify_blueprint_type(file.filename)

    thumbnail_path = os.path.join(file_dir, "thumbnail.png")
    generate_thumbnail(saved_path, thumbnail_path)

    metadata = {
        "id": file_id,
        "filename": file.filename,
        "type": file_type,
        "size_kb": file_size_kb,
        "pages": None,
        "dimensions": None,
        "thumbnail": "thumbnail.png"
    }
    save_metadata_to_json(metadata, file_dir)

    return metadata

def classify_blueprint_type(filename: str) -> str:
    name = filename.lower()
    if "arch" in name:
        return "architectural"
    elif "struct" in name:
        return "structural"
    elif "mep" in name:
        return "mep"
    elif "civil" in name:
        return "civil"
    return "General"

def _get_file_folder(file_id: str) -> str:
    return os.path.join(UPLOAD_DIR, file_id)

def list_files() -> List[dict]:
    files = []
    if not os.path.exists(UPLOAD_DIR):
        return files
    for file_id in os.listdir(UPLOAD_DIR):
        meta_path = os.path.join(_get_file_folder(file_id), "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                metadata = json.load(f)
                files.append(metadata)
    return files

def get_file(file_id: str) -> Optional[dict]:
    meta_path = os.path.join(_get_file_folder(file_id), "metadata.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, "r") as f:
        metadata = json.load(f)
    return metadata

def delete_file(file_id: str) -> bool:
    folder = _get_file_folder(file_id)
    if not os.path.exists(folder):
        return False
    shutil.rmtree(folder)
    return True

def get_thumbnail_path(file_id: str) -> Optional[str]:
    thumb_path = os.path.join(_get_file_folder(file_id), "thumbnail.png")
    if not os.path.exists(thumb_path):
        return None
    return thumb_path
