from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
file_id = "c1841bee-3715-40f5-868a-82bcdbcbefd8"
processing_options = {"enable_ocr": True, "enable_cv": False}

def test_start_processing():
    response = client.post(f"/process/{file_id}", json=processing_options)
    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert data["status"] == "processing_started"

def test_get_status():
    # Ensure processing started first
    client.post(f"/process/{file_id}", json=processing_options)
    response = client.get(f"/process/{file_id}/status")
    assert response.status_code == 200
    assert "status" in response.json()

def test_cancel_processing():
    # Ensure processing started first
    client.post(f"/process/{file_id}", json=processing_options)
    response = client.post(f"/process/{file_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_get_queue():
    response = client.get("/process/queue")
    assert response.status_code == 200
    json_data = response.json()
    assert "processing_queue" in json_data
    assert isinstance(json_data["processing_queue"], list)
