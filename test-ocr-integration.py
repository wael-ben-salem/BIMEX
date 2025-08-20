#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration OCR
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin des modules OCR
backend_path = Path(__file__).parent / "backend"
ocr_modules_path = backend_path / "ocr_modules"
sys.path.insert(0, str(ocr_modules_path))

print(f"=== TEST D'INTÉGRATION OCR ===")
print(f"Chemin des modules OCR: {ocr_modules_path}")
print(f"Chemin ajouté au sys.path: {ocr_modules_path}")

try:
    # Test 1: Importer le module principal
    print("\n1. Test d'import du module principal...")
    import app
    print("✓ Module 'app' importé avec succès")
    
    # Test 2: Importer les modules API
    print("\n2. Test d'import des modules API...")
    from app.api import files, processing, results
    print("✓ Modules API importés avec succès")
    
    # Test 3: Vérifier les routers
    print("\n3. Test des routers FastAPI...")
    print(f"  - Router files: {files.router}")
    print(f"  - Router processing: {processing.router}")
    print(f"  - Router results: {results.router}")
    print("✓ Routers FastAPI disponibles")
    
    # Test 4: Vérifier les routes
    print("\n4. Test des routes disponibles...")
    for router_name, router in [("files", files.router), ("processing", processing.router), ("results", results.router)]:
        print(f"  - {router_name}: {len(router.routes)} routes")
        for route in router.routes:
            if hasattr(route, 'path'):
                print(f"    * {route.methods} {route.path}")
    
    print("\n✅ Intégration OCR testée avec succès !")
    
except ImportError as e:
    print(f"✗ Erreur d'import: {e}")
    print(f"  Détails: {type(e).__name__}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Erreur inattendue: {e}")
    print(f"  Type: {type(e).__name__}")
    sys.exit(1)
