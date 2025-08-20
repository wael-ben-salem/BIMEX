from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.models.ocr_models import ProcessingOptions
from app.core.processing_manager import ProcessingManager
import asyncio

router = APIRouter()
manager = ProcessingManager()

@router.post("/process/{file_id}")
async def start_processing(file_id: str, options: ProcessingOptions):
    if manager.get_status(file_id) == "processing":
        raise HTTPException(400, "Processing already in progress for this file")

    task = manager.add_task(file_id, manager.start_processing(file_id, options))
    return JSONResponse({"file_id": file_id, "status": "processing_started"})


@router.get("/process/{file_id}/status")
async def get_status(file_id: str):
    status = manager.get_status(file_id)
    if status == "not_found":
        raise HTTPException(404, "File not found")
    return {"file_id": file_id, "status": status}

@router.post("/process/{file_id}/cancel")
async def cancel_processing(file_id: str):
    cancelled = manager.cancel_processing(file_id)
    if not cancelled:
        raise HTTPException(400, "No active processing task to cancel")
    return {"file_id": file_id, "status": "cancelled"}

@router.get("/process/queue")
async def get_queue():
    queue = manager.get_queue()
    return {"processing_queue": queue}
