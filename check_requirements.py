#!/usr/bin/env python3
"""
🔍 VÉRIFICATION DES PRÉREQUIS SYSTÈME
Vérifie que tout est prêt pour le système BI BIMEX
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Vérifie la version de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Version trop ancienne")
        print("   Minimum requis: Python 3.7+")
        return False

def check_pip():
    """Vérifie que pip est disponible"""
    try:
        subprocess.check_output([sys.executable, "-m", "pip", "--version"])
        print("✅ pip - OK")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip - Non disponible")
        return False

def check_required_modules():
    """Vérifie les modules Python requis"""
    required_modules = [
        "fastapi", "uvicorn", "requests", "pandas", "pathlib", "json", "datetime"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError:
            print(f"⚠️ {module} - Manquant (sera installé automatiquement)")
            missing_modules.append(module)
    
    return len(missing_modules) == 0

def check_file_structure():
    """Vérifie la structure des fichiers"""
    required_files = [
        "backend/main.py",
        "backend/bi_integration.py",
        "xeokit-bim-viewer/app/home.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - OK")
        else:
            print(f"❌ {file_path} - Manquant")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_ports():
    """Vérifie que le port 8001 est disponible"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 8001))
            print("✅ Port 8001 - Disponible")
            return True
    except OSError:
        print("⚠️ Port 8001 - Occupé (le serveur peut déjà être en cours d'exécution)")
        return True  # Ce n'est pas bloquant

def check_projects_directory():
    """Vérifie le répertoire des projets"""
    projects_dir = Path("xeokit-bim-viewer/app/data/projects")
    
    if projects_dir.exists():
        project_count = len([d for d in projects_dir.iterdir() if d.is_dir()])
        print(f"✅ Répertoire projets - {project_count} projets trouvés")
        return True
    else:
        print("⚠️ Répertoire projets - Non trouvé (sera créé si nécessaire)")
        return True

def main():
    """Fonction principale de vérification"""
    print("🔍 VÉRIFICATION DES PRÉREQUIS SYSTÈME BIMEX BI")
    print("=" * 60)
    
    checks = [
        ("Version Python", check_python_version),
        ("Gestionnaire pip", check_pip),
        ("Modules Python", check_required_modules),
        ("Structure fichiers", check_file_structure),
        ("Disponibilité port", check_ports),
        ("Répertoire projets", check_projects_directory)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n📋 Vérification: {check_name}")
        result = check_func()
        results.append((check_name, result))
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES VÉRIFICATIONS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ OK" if result else "❌ ERREUR"
        print(f"{status} {check_name}")
    
    print(f"\n📈 Score: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print("\n🎉 SYSTÈME PRÊT !")
        print("Vous pouvez lancer la configuration avec:")
        print("  python setup_bi_system.py")
        print("ou directement:")
        print("  setup_and_run.bat (Windows)")
        print("  ./setup_and_run.sh (Linux/Mac)")
        return True
    else:
        print("\n⚠️ PROBLÈMES DÉTECTÉS")
        print("Résolvez les erreurs avant de continuer.")
        print("La plupart des modules manquants seront installés automatiquement.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
