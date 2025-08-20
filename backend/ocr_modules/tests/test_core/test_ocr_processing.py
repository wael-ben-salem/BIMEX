import asyncio
from app.core.processing_manager import ProcessingManager
from .app.models.ocr_models import ProcessingOptions

# Change this to your test file ID
file_id = "c1841bee-3715-40f5-868a-82bcdbcbefd8"

async def main():
    manager = ProcessingManager()
    
    options = ProcessingOptions(
        enable_ocr=True,
        enable_vision=False,  # Only OCR for this test
        languages=["eng"]
    )
    
    # Start processing
    print(f"Starting OCR processing for file: {file_id}")
    await manager.start_processing(file_id, options)
    
    status = manager.get_status(file_id)
    print(f"Processing status: {status}")
    
    # Read and display saved OCR results
    from app.storage.file_storage import get_file_path
    import json
    import os
    
    results_path = os.path.join(get_file_path(file_id), "ocr_results.json")
    if os.path.exists(results_path):
        with open(results_path, "r", encoding="utf-8") as f:
            ocr_results = json.load(f)
        print("\n--- OCR Results ---")
        for item in ocr_results.get("extracted_text", []):
            print(item)
    else:
        print("No OCR results found.")

# Run async
asyncio.run(main())
