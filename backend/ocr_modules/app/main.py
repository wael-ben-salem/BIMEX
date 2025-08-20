from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import files, processing,results

app = FastAPI(title="OCR BIM Backend")

# CORS setup - allow your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React frontend URL
        "http://localhost:8081",  # xeokit-bim-viewer URL
        "http://127.0.0.1:8081"   # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(files.router, prefix="/files", tags=["Files"])
app.include_router(processing.router, prefix="", tags=["Processing"])
app.include_router(results.router, prefix="",tags=["Results"])  # <-- Added


@app.get("/")
def root():
    return {"message": "OCR BIM Backend is running"}

