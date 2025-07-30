#!/usr/bin/env python3
"""
Script de démarrage pour la plateforme d'analyse BIM
Lance le serveur backend et ouvre l'interface web
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")
    
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI et Uvicorn trouvés")

        # Test ifcopenshell séparément
        try:
            import ifcopenshell
            print("✅ ifcopenshell trouvé")
        except ImportError:
            print("⚠️  ifcopenshell non trouvé - certaines fonctionnalités seront limitées")
            print("💡 Pour installer: pip install git+https://github.com/IfcOpenShell/IfcOpenShell.git")

        return True
    except ImportError as e:
        print(f"❌ Dépendance critique manquante: {e}")
        print("\n📦 Installation des dépendances requise:")
        print("cd backend && pip install fastapi uvicorn")
        return False

def start_backend():
    """Lance le serveur backend"""
    print("🚀 Démarrage du serveur backend...")
    
    backend_dir = Path(__file__).parent / "backend"
    
    # Changer vers le répertoire backend
    os.chdir(backend_dir)
    
    # Lancer uvicorn
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage du serveur: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé par l'utilisateur")
        return True

def open_browser():
    """Ouvre le navigateur avec l'interface web"""
    print("🌐 Ouverture de l'interface web...")
    
    # Attendre que le serveur soit prêt
    time.sleep(3)
    
    frontend_path = Path(__file__).parent / "frontend" / "bim_analysis.html"
    
    if frontend_path.exists():
        webbrowser.open(f"file://{frontend_path.absolute()}")
        print(f"✅ Interface ouverte: {frontend_path}")
    else:
        print("❌ Interface web non trouvée")
        print("💡 Vous pouvez accéder à l'API directement sur: http://localhost:8000")

def show_welcome():
    """Affiche le message de bienvenue"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🏗️  BIM ANALYSIS PLATFORM                 ║
║                                                              ║
║  Plateforme d'analyse intelligente de fichiers BIM avec IA  ║
║                                                              ║
║  Fonctionnalités disponibles:                               ║
║  • 🔍 Analyse complète des métriques BIM                    ║
║  • 🚨 Détection automatique d'anomalies                     ║
║  • 🏢 Classification automatique de bâtiments               ║
║  • 📄 Génération de rapports PDF                            ║
║  • 🤖 Assistant IA conversationnel                          ║
║  • 📊 Visualisation 3D avec xeokit                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def show_usage():
    """Affiche les instructions d'utilisation"""
    print("""
📋 INSTRUCTIONS D'UTILISATION:

1. 📁 Chargez votre fichier IFC via l'interface web
2. 🔍 Choisissez le type d'analyse souhaité:
   - Analyse complète des métriques
   - Détection d'anomalies
   - Classification du bâtiment
   - Génération de rapport PDF
   - Assistant IA conversationnel

3. 📊 Consultez les résultats dans les onglets correspondants

🔧 CONFIGURATION AVANCÉE:
- Copiez backend/.env.example vers backend/.env
- Ajoutez votre clé API OpenAI pour l'assistant IA
- Modifiez les paramètres selon vos besoins

🌐 ACCÈS:
- Interface web: Ouverture automatique du navigateur
- API REST: http://localhost:8000
- Documentation API: http://localhost:8000/docs

❓ AIDE:
- Consultez le README.md pour plus d'informations
- Vérifiez les logs en cas de problème
    """)

def main():
    """Fonction principale"""
    show_welcome()
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("\n🛠️  Installez d'abord les dépendances puis relancez ce script")
        return
    
    print("\n" + "="*60)
    show_usage()
    print("="*60 + "\n")
    
    # Demander confirmation
    response = input("🚀 Voulez-vous démarrer la plateforme BIM Analysis ? (o/N): ").lower()
    
    if response not in ['o', 'oui', 'y', 'yes']:
        print("👋 Au revoir !")
        return
    
    # Lancer l'ouverture du navigateur en arrière-plan
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Lancer le serveur backend (bloquant)
    try:
        start_backend()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la plateforme BIM Analysis")
        print("👋 Merci d'avoir utilisé notre plateforme !")

if __name__ == "__main__":
    main()
