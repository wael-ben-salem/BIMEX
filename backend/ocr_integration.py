"""
Module d'intégration OCR pour le backend principal
Ce module permet d'intégrer automatiquement les fonctionnalités OCR dans le backend principal
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Ajouter le chemin des modules OCR au path Python
ocr_modules_path = Path(__file__).parent / "ocr_modules"
sys.path.insert(0, str(ocr_modules_path))

# Variables globales pour l'état OCR
OCR_AVAILABLE = False
OCR_MODULES = {}
OCR_ROUTERS = []

def is_ocr_available() -> bool:
    """Vérifie si les modules OCR sont disponibles"""
    global OCR_AVAILABLE
    try:
        # Vérifier que le dossier ocr_modules existe
        if not ocr_modules_path.exists():
            print("✗ Dossier ocr_modules non trouvé")
            return False
        
        # Vérifier que les modules essentiels existent
        required_modules = [
            "app.api.files",
            "app.api.processing", 
            "app.api.results"
        ]
        
        for module_name in required_modules:
            try:
                # Importer depuis le dossier ocr_modules
                module = __import__(module_name, fromlist=['*'])
                print(f"✓ Module {module_name} chargé avec succès")
            except ImportError as e:
                print(f"✗ Module {module_name} non disponible: {e}")
                return False
        
        OCR_AVAILABLE = True
        print("✓ Modules OCR disponibles")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de la vérification des modules OCR: {e}")
        return False

def init_ocr() -> bool:
    """Initialise les modules OCR et charge les routers"""
    global OCR_MODULES, OCR_ROUTERS
    
    if not is_ocr_available():
        return False
    
    try:
        # Importer les modules OCR
        from app.api import files, processing, results
        
        # Stocker les références aux modules
        OCR_MODULES = {
            "files": files,
            "processing": processing,
            "results": results
        }
        
        # Créer les routers avec leurs préfixes et tags
        OCR_ROUTERS = [
            (files.router, "/ocr/files", ["OCR Files"]),
            (processing.router, "/ocr/process", ["OCR Processing"]),
            (results.router, "/ocr", ["OCR Results"])
        ]
        
        print("✓ Modules OCR initialisés avec succès")
        return True
        
    except Exception as e:
        print(f"✗ Erreur lors de l'initialisation des modules OCR: {e}")
        return False

def get_ocr_routers() -> List[Tuple]:
    """Retourne la liste des routers OCR avec leurs préfixes et tags"""
    return OCR_ROUTERS

def get_ocr_info() -> Dict[str, Any]:
    """Retourne les informations sur l'état des modules OCR"""
    return {
        "available": OCR_AVAILABLE,
        "modules": list(OCR_MODULES.keys()) if OCR_MODULES else [],
        "routers_count": len(OCR_ROUTERS),
        "status": "active" if OCR_AVAILABLE else "inactive",
        "message": "Modules OCR intégrés et fonctionnels" if OCR_AVAILABLE else "Modules OCR non disponibles"
    }

def get_ocr_module(module_name: str):
    """Retourne un module OCR spécifique"""
    return OCR_MODULES.get(module_name)

def list_ocr_endpoints() -> List[str]:
    """Liste tous les endpoints OCR disponibles"""
    endpoints = []
    if OCR_ROUTERS:
        for router, prefix, tags in OCR_ROUTERS:
            if hasattr(router, 'routes'):
                for route in router.routes:
                    if hasattr(route, 'path'):
                        endpoints.append(f"{prefix}{route.path}")
    return endpoints

# Initialisation automatique au chargement du module
if __name__ == "__main__":
    print("=== Test du module d'intégration OCR ===")
    print(f"Chemin des modules OCR: {ocr_modules_path}")
    print(f"Modules disponibles: {is_ocr_available()}")
    
    if OCR_AVAILABLE:
        init_ocr()
        print(f"Routers créés: {len(OCR_ROUTERS)}")
        print(f"Endpoints disponibles: {list_ocr_endpoints()}")
        print(f"Informations OCR: {get_ocr_info()}")
    else:
        print("Modules OCR non disponibles")
else:
    # Initialisation automatique lors de l'import
    try:
        is_ocr_available()
        if OCR_AVAILABLE:
            init_ocr()
    except Exception as e:
        print(f"⚠️ Erreur lors de l'initialisation automatique OCR: {e}")
        OCR_AVAILABLE = False
