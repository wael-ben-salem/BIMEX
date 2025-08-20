import os
import asyncio
from typing import Dict
from app.core.ocr_engine import perform_ocr
from app.core.vision_engine import detect_symbols_and_elements
from app.storage.file_storage import get_file_path, save_results
from app.models.ocr_models import ProcessingOptions, DetectedSymbolModel, DetectedElementModel

class ProcessingManager:
    def __init__(self):
        self.status: Dict[str, str] = {}  # file_id -> status
        self.tasks: Dict[str, asyncio.Task] = {}  # file_id -> asyncio.Task

    async def start_processing(self, file_id: str, options: ProcessingOptions):
        if self.status.get(file_id) == "processing":
            return  # Already processing

        self.status[file_id] = "processing"

        try:
            folder_path = get_file_path(file_id)
            # Find file starting with "original."
            file_path = None
            for fname in os.listdir(folder_path):
                if fname.startswith("original."):
                    file_path = os.path.join(folder_path, fname)
                    break
            if not file_path:
                raise FileNotFoundError(f"No file starting with 'original.' found in {folder_path}")

            ocr_results = []
            vision_results = {}
            ocr_time = 0
            vision_time = 0

            if options.enable_ocr:
                # Enable LLM type detection if requested
                ocr_results, ocr_time = perform_ocr(file_path, options.languages, use_llm=options.use_llm)

            if options.enable_vision:
                symbols, elements, vision_time = detect_symbols_and_elements(file_path)

                # Convert to dicts for JSON serialization using Pydantic models
                vision_results = {
                    "symbols": [DetectedSymbolModel(
                        name=s.name,
                        bbox=s.bbox,
                        confidence=s.confidence
                    ).dict() for s in symbols],

                    "elements": [DetectedElementModel(
                        element_type=e.element_type,
                        bbox=e.bbox,
                        confidence=getattr(e, 'confidence', None)
                    ).dict() for e in elements],

                    "processing_time": vision_time
                }

            # Save results as JSON-serializable dicts
            save_results(file_id, {
                "ocr": {
                    "results": [item.dict() for item in ocr_results],
                    "processing_time": ocr_time
                },
                "vision": vision_results
            })

            self.status[file_id] = "completed"

        except asyncio.CancelledError:
            self.status[file_id] = "cancelled"
            raise
        except Exception as e:
            self.status[file_id] = f"failed: {str(e)}"

    def get_status(self, file_id: str) -> str:
        return self.status.get(file_id, "not_found")

    def cancel_processing(self, file_id: str) -> bool:
        task = self.tasks.get(file_id)
        if task and not task.done():
            task.cancel()
            self.status[file_id] = "cancelled"
            return True
        return False

    def get_queue(self):
        return [fid for fid, status in self.status.items() if status == "processing"]

    def add_task(self, file_id: str, coro):
        task = asyncio.create_task(coro)
        self.tasks[file_id] = task
        return task
