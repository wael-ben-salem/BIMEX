#!/usr/bin/env python3
"""
Script de démarrage simplifié pour le serveur BIMEX 2.0
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_dependencies():
    """Vérifier les dépendances Python"""
    required_modules = ['fastapi', 'uvicorn', 'jinja2']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"Module {module} trouvé")
        except ImportError:
            missing_modules.append(module)
            print_error(f"Module {module} manquant")
    
    return missing_modules

def install_dependencies(missing_modules):
    """Installer les dépendances manquantes"""
    if not missing_modules:
        return True
    
    print_info("Installation des dépendances manquantes...")
    try:
        for module in missing_modules:
            print_info(f"Installation de {module}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', module], 
                         check=True, capture_output=True)
            print_success(f"{module} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors de l'installation: {e}")
        return False

def start_server():
    """Démarrer le serveur FastAPI"""
    print_info("Démarrage du serveur BIMEX 2.0...")
    
    # Changer vers le répertoire backend
    backend_path = Path('backend')
    if not backend_path.exists():
        print_error("Répertoire 'backend' non trouvé")
        print_info("Assurez-vous d'être dans le répertoire racine du projet")
        return False
    
    main_py = backend_path / 'main.py'
    if not main_py.exists():
        print_error("Fichier 'backend/main.py' non trouvé")
        return False
    
    try:
        # Démarrer le serveur
        os.chdir('backend')
        print_info("Lancement de uvicorn...")
        print_info("Serveur accessible sur: http://localhost:8001")
        print_info("Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Ouvrir le navigateur après un délai
        def open_browser():
            time.sleep(3)
            try:
                webbrowser.open('http://localhost:8001')
                print_success("Navigateur ouvert automatiquement")
            except:
                print_info("Ouvrez manuellement: http://localhost:8001")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Démarrer le serveur
        subprocess.run([sys.executable, 'main.py'], check=True)
        
    except KeyboardInterrupt:
        print_info("\nServeur arrêté par l'utilisateur")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Erreur lors du démarrage du serveur: {e}")
        return False
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return False

def main():
    print_header("🚀 DÉMARRAGE SERVEUR BIMEX 2.0")
    
    # Vérifier les fichiers nécessaires
    required_files = ['backend/main.py', 'xeokit-bim-viewer/app/home.html']
    for file_path in required_files:
        if not os.path.exists(file_path):
            print_error(f"Fichier manquant: {file_path}")
            print_info("Assurez-vous d'être dans le répertoire racine du projet")
            sys.exit(1)
        else:
            print_success(f"Fichier trouvé: {file_path}")
    
    # Vérifier les dépendances
    print_header("📦 VÉRIFICATION DES DÉPENDANCES")
    missing_modules = check_dependencies()
    
    if missing_modules:
        print_info("Certaines dépendances sont manquantes")
        response = input("Voulez-vous les installer automatiquement? (o/n): ")
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            if not install_dependencies(missing_modules):
                print_error("Échec de l'installation des dépendances")
                sys.exit(1)
        else:
            print_info("Installation manuelle requise:")
            for module in missing_modules:
                print_info(f"  pip install {module}")
            sys.exit(1)
    
    # Démarrer le serveur
    print_header("🌐 DÉMARRAGE DU SERVEUR")
    success = start_server()
    
    if success:
        print_header("✨ SERVEUR ARRÊTÉ PROPREMENT")
    else:
        print_header("❌ ERREUR DE DÉMARRAGE")
        print_info("Utilisez le script de diagnostic pour plus d'informations:")
        print_info("  python diagnostic-serveur.py")

if __name__ == "__main__":
    main()
