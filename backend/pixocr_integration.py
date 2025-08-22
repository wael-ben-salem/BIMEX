"""
Module d'intégration PixOCR pour le backend principal
Monte automatiquement l'app FastAPI de backend/pixocr_modules sous /pixocr
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Chemins
_here = Path(__file__).parent  # backend/
pixocr_modules_path = _here / "pixocr_modules"

PIX_AVAILABLE = False
PIX_APP = None

def is_pix_available() -> bool:
    """Vérifie si pixocr_modules est disponible"""
    global PIX_AVAILABLE
    if pixocr_modules_path.exists():
        PIX_AVAILABLE = True
        return True
    return False

def init_pix() -> bool:
    """Initialise PixOCR en chargeant l'app FastAPI depuis app.py"""
    global PIX_APP
    if not is_pix_available():
        print("✗ PixOCR non disponible")
        return False
    
    try:
        # Sauvegarder le sys.path original
        original_path = sys.path.copy()
        
        # Ajouter pixocr_modules au path pour permettre les imports locaux
        sys.path.insert(0, str(pixocr_modules_path))
        
        # Importer l'app depuis pixocr_modules/app.py en utilisant un chemin spécifique
        import importlib.util
        spec = importlib.util.spec_from_file_location("pixocr_app", pixocr_modules_path / "app.py")
        pixocr_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pixocr_module)
        
        PIX_APP = pixocr_module.app
        print("✓ PixOCR app chargée depuis app.py")
        
        # Restaurer le sys.path original
        sys.path[:] = original_path
        return True
        
    except Exception as e:
        print(f"✗ Échec chargement app PixOCR: {e}")
        # Restaurer le sys.path en cas d'erreur
        if 'original_path' in locals():
            sys.path[:] = original_path
        return False

def get_pix_app():
    """Retourne l'app FastAPI PixOCR à monter"""
    return PIX_APP

def get_pix_info() -> Dict[str, Any]:
    return {
        "available": PIX_AVAILABLE,
        "app_loaded": PIX_APP is not None,
        "routes": [
            "/process",  # POST - Traitement de documents
            "/review",   # GET - Re-exécution de review
            "/outputs",  # Static files
            "/uploads"   # Static files
        ] if PIX_APP else []
    }
