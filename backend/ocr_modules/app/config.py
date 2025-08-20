import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# =========================
# Server configuration
# =========================
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8001))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# =========================
# File storage paths
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

UPLOADS_DIR = os.getenv("UPLOAD_DIR", os.path.join(DATA_DIR, "uploads"))
RESULTS_DIR = os.getenv("RESULTS_DIR", os.path.join(DATA_DIR, "results"))
EXPORTS_DIR = os.getenv("EXPORTS_DIR", os.path.join(DATA_DIR, "exports"))
THUMBNAILS_DIR = os.path.join(DATA_DIR, "thumbnails")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
MODELS_DIR = os.path.join(DATA_DIR, "models")

# =========================
# Processing settings
# =========================
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", 3))
PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", 300))  # seconds

# =========================
# OCR configuration
# =========================
TESSERACT_PATH = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")
OCR_LANGUAGES = os.getenv("OCR_LANGUAGES", "eng")  # comma-separated: "eng,fra"

# =========================
# Logging
# =========================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", os.path.join(BASE_DIR, "..", "logs", "app.log"))

# =========================
# Utility function to ensure directories exist
# =========================
def ensure_dirs():
    for folder in [UPLOADS_DIR, RESULTS_DIR, EXPORTS_DIR, THUMBNAILS_DIR, CACHE_DIR, MODELS_DIR]:
        os.makedirs(folder, exist_ok=True)

# Call it automatically on import
ensure_dirs()
