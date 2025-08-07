#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier le statut du serveur BIMEX
"""

import requests
import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def check_port_availability(port):
    """Vérifier si un port est utilisé"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def check_backend_process():
    """Vérifier si le processus backend est en cours d'exécution"""
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            return 'python.exe' in result.stdout
        else:  # Linux/Mac
            result = subprocess.run(['pgrep', '-f', 'main.py'], 
                                  capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
    except:
        return False

def check_files_exist():
    """Vérifier que les fichiers nécessaires existent"""
    files_to_check = [
        'backend/main.py',
        'xeokit-bim-viewer/app/home.html',
        'frontend/bim_analysis.html'
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print_success(f"Fichier trouvé: {file_path}")
        else:
            print_error(f"Fichier manquant: {file_path}")
            all_exist = False
    
    return all_exist

def test_server_response():
    """Tester la réponse du serveur"""
    urls_to_test = [
        'http://localhost:8001/',
        'http://localhost:8001/app/home.html',
        'http://localhost:8001/analysis'
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_success(f"URL accessible: {url}")
            elif response.status_code == 302:
                print_info(f"URL redirige: {url} -> {response.headers.get('Location', 'Unknown')}")
            else:
                print_warning(f"URL répond avec code {response.status_code}: {url}")
        except requests.exceptions.ConnectionError:
            print_error(f"Connexion refusée: {url}")
        except requests.exceptions.Timeout:
            print_error(f"Timeout: {url}")
        except Exception as e:
            print_error(f"Erreur pour {url}: {str(e)}")

def get_startup_command():
    """Obtenir la commande de démarrage appropriée"""
    if os.path.exists('backend/main.py'):
        return "cd backend && python main.py"
    else:
        return "python backend/main.py"

def main():
    print_header("🔍 DIAGNOSTIC SERVEUR BIMEX 2.0")
    
    print_info("Vérification de l'environnement...")
    
    # 1. Vérifier les fichiers
    print_header("📁 VÉRIFICATION DES FICHIERS")
    files_ok = check_files_exist()
    
    # 2. Vérifier les ports
    print_header("🌐 VÉRIFICATION DES PORTS")
    port_8001 = check_port_availability(8001)
    if port_8001:
        print_success("Port 8001 est utilisé (serveur probablement en cours)")
    else:
        print_error("Port 8001 est libre (serveur non démarré)")
    
    # 3. Vérifier les processus
    print_header("⚙️ VÉRIFICATION DES PROCESSUS")
    backend_running = check_backend_process()
    if backend_running:
        print_success("Processus Python détecté")
    else:
        print_error("Aucun processus Python main.py détecté")
    
    # 4. Tester les réponses serveur
    print_header("🌍 TEST DES RÉPONSES SERVEUR")
    if port_8001:
        test_server_response()
    else:
        print_warning("Serveur non accessible - tests ignorés")
    
    # 5. Diagnostic et recommandations
    print_header("📋 DIAGNOSTIC ET RECOMMANDATIONS")
    
    if not files_ok:
        print_error("PROBLÈME: Fichiers manquants")
        print_info("Solution: Vérifiez que vous êtes dans le bon répertoire")
        print_info("Le répertoire doit contenir: backend/, xeokit-bim-viewer/, frontend/")
    
    elif not port_8001 and not backend_running:
        print_error("PROBLÈME: Serveur non démarré")
        print_info("Solution: Démarrez le serveur avec:")
        print_info(f"  {get_startup_command()}")
        print_info("Puis accédez à: http://localhost:8001")
    
    elif port_8001 and not backend_running:
        print_warning("PROBLÈME: Port utilisé par un autre processus")
        print_info("Solution: Arrêtez l'autre processus ou changez de port")
        if os.name == 'nt':
            print_info("Windows: netstat -ano | findstr :8001")
        else:
            print_info("Linux/Mac: lsof -i :8001")
    
    elif backend_running and not port_8001:
        print_warning("PROBLÈME: Processus détecté mais port non accessible")
        print_info("Solution: Vérifiez les logs du serveur pour les erreurs")
    
    else:
        print_success("STATUT: Serveur semble fonctionnel")
        print_info("Accédez à: http://localhost:8001")
        print_info("Si vous voyez encore 'Not Found', vérifiez les logs du serveur")
    
    # 6. Commandes utiles
    print_header("🛠️ COMMANDES UTILES")
    print_info("Démarrer le serveur:")
    print_info(f"  {get_startup_command()}")
    print_info("")
    print_info("Vérifier les processus:")
    if os.name == 'nt':
        print_info("  tasklist | findstr python")
    else:
        print_info("  ps aux | grep python")
    print_info("")
    print_info("Tester manuellement:")
    print_info("  curl http://localhost:8001/")
    print_info("  curl http://localhost:8001/app/home.html")
    
    print_header("✨ DIAGNOSTIC TERMINÉ")

if __name__ == "__main__":
    main()
