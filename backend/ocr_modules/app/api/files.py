from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from app.core import file_manager

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        metadata = await file_manager.process_uploaded_file(file)
        return JSONResponse(content={"status": "success", "data": metadata})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("")
async def list_files():
    files = file_manager.list_files()
    return {"status": "success", "data": files}

@router.get("/{file_id}")
async def get_file_details(file_id: str):
    file_info = file_manager.get_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "success", "data": file_info}
 
@router.delete("/{file_id}")
async def delete_file(file_id: str):
    success = file_manager.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "success", "message": "File deleted"}

@router.get("/{file_id}/thumbnail")
async def get_thumbnail(file_id: str):
    thumbnail_path = file_manager.get_thumbnail_path(file_id)
    if not thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumbnail_path)
