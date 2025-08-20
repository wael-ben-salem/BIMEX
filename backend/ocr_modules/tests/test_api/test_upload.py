import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

TEST_FILES_DIR = "tests/sample_files"

def test_upload_valid_file():
    file_path = os.path.join(TEST_FILES_DIR, "bridge.png")
    with open(file_path, "rb") as f:
        response = client.post("/ocr/files/upload", files={"file": ("bridge.png", f, "image/png")})
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"
    data = json_resp["data"]
    assert data["filename"] == "bridge.png"
    assert data["id"] is not None
    assert data["size_kb"] > 0
    assert data["thumbnail"] == "thumbnail.png"

def test_upload_unsupported_file_type():
    # Using a .exe file or any unsupported extension
    file_path = os.path.join(TEST_FILES_DIR, "malicious.exe")
    with open(file_path, "rb") as f:
        response = client.post("/ocr/files/upload", files={"file": ("malicious.exe", f, "application/octet-stream")})
    assert response.status_code == 400
    json_resp = response.json()
    assert "Unsupported file type" in json_resp["detail"]

def test_upload_no_file():
    response = client.post("/ocr/files/upload", files={})
    assert response.status_code == 422  # Unprocessable Entity (missing file)
