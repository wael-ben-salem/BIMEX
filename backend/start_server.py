#!/usr/bin/env python3
"""
Script pour démarrer le serveur FastAPI pour la conversion IFC
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Installe les dépendances Python si nécessaire"""
    try:
        import fastapi
        import uvicorn
        print("✓ Dépendances Python déjà installées")
    except ImportError:
        print("Installation des dépendances Python...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dépendances Python installées")

def check_node_dependencies():
    """Vérifie que les dépendances Node.js sont installées"""
    parent_dir = Path(__file__).parent.parent
    node_modules = parent_dir / "node_modules"
    
    if not node_modules.exists():
        print("⚠️  Les dépendances Node.js ne semblent pas installées.")
        print("   Veuillez exécuter 'npm install' dans le répertoire racine du projet.")
        return False
    
    print("✓ Dépendances Node.js détectées")
    return True

def start_server():
    """Démarre le serveur FastAPI"""
    print("Démarrage du serveur FastAPI...")
    print("Le serveur sera accessible sur: http://localhost:8001")
    print("Documentation API: http://localhost:8001/docs")
    print("\nPour arrêter le serveur, appuyez sur Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8001", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\nServeur arrêté.")

if __name__ == "__main__":
    print("=== Serveur de conversion IFC vers XKT ===\n")
    
    # Vérifier et installer les dépendances
    install_dependencies()
    
    # Vérifier les dépendances Node.js
    if not check_node_dependencies():
        sys.exit(1)
    
    # Démarrer le serveur
    start_server()