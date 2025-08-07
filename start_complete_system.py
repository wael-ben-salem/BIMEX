#!/usr/bin/env python3
"""
🚀 DÉMARRAGE COMPLET DU SYSTÈME BI OPEN-SOURCE BIMEX
Lance tous les services et vérifie leur bon fonctionnement
"""

import os
import sys
import subprocess
import time
import requests
import webbrowser
from pathlib import Path
import threading

def print_banner():
    """Affiche la bannière de démarrage"""
    print("""
🚀 SYSTÈME BI OPEN-SOURCE BIMEX
================================
Apache Superset + IFC.js + n8n + ERPNext
    """)

def check_docker():
    """Vérifie que Docker est disponible"""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker détecté")
            return True
        else:
            print("❌ Docker non disponible")
            return False
    except FileNotFoundError:
        print("❌ Docker non installé")
        return False

def start_docker_services():
    """Démarre les services Docker"""
    print("\n📦 Démarrage des services Docker...")
    
    if not Path("docker-compose-bi.yml").exists():
        print("⚠️ Fichier docker-compose-bi.yml non trouvé")
        print("Exécutez d'abord: python setup_opensource_bi.py")
        return False
    
    try:
        # Démarrer les services
        subprocess.run(["docker-compose", "-f", "docker-compose-bi.yml", "up", "-d"], 
                      check=True, capture_output=True)
        print("✅ Services Docker démarrés")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur démarrage Docker: {e}")
        return False

def wait_for_service(name, url, timeout=60):
    """Attend qu'un service soit disponible"""
    print(f"⏳ Attente du service {name}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 302]:
                print(f"✅ {name} disponible")
                return True
        except:
            pass
        time.sleep(2)
    
    print(f"⚠️ {name} non disponible après {timeout}s")
    return False

def start_bimex_server():
    """Démarre le serveur BIMEX BI"""
    print("\n🚀 Démarrage du serveur BIMEX BI...")
    
    if not Path("backend/main.py").exists():
        print("❌ Fichier backend/main.py non trouvé")
        return None
    
    try:
        # Changer vers le répertoire backend
        os.chdir("backend")
        
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([sys.executable, "main.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Revenir au répertoire racine
        os.chdir("..")
        
        # Attendre que le serveur démarre
        time.sleep(3)
        
        # Vérifier que le serveur répond
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Serveur BIMEX BI démarré")
                return process
            else:
                print("⚠️ Serveur BIMEX BI ne répond pas correctement")
                return process
        except:
            print("⚠️ Serveur BIMEX BI en cours de démarrage...")
            return process
            
    except Exception as e:
        print(f"❌ Erreur démarrage serveur BIMEX: {e}")
        return None

def run_tests():
    """Lance les tests automatiques"""
    print("\n🧪 Lancement des tests automatiques...")
    
    try:
        result = subprocess.run([sys.executable, "test_opensource_bi.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Tests réussis")
            return True
        else:
            print("⚠️ Certains tests ont échoué")
            print(result.stdout[-500:])  # Afficher les dernières lignes
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Tests interrompus (timeout)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

def open_browser_tabs():
    """Ouvre les onglets du navigateur"""
    print("\n🌐 Ouverture des interfaces web...")
    
    urls = [
        ("BIMEX BI Dashboard", "http://localhost:8000/app/home.html"),
        ("Apache Superset", "http://localhost:8088"),
        ("n8n Workflows", "http://localhost:5678"),
        ("IFC.js Viewer", "http://localhost:3000"),
    ]
    
    for name, url in urls:
        try:
            webbrowser.open(url)
            print(f"✅ {name} ouvert")
            time.sleep(1)  # Éviter d'ouvrir tous les onglets en même temps
        except Exception as e:
            print(f"⚠️ Impossible d'ouvrir {name}: {e}")

def display_summary():
    """Affiche le résumé des services"""
    print("\n" + "="*60)
    print("🎉 SYSTÈME BI OPEN-SOURCE DÉMARRÉ !")
    print("="*60)
    
    services = [
        ("🚀 BIMEX BI Dashboard", "http://localhost:8000/app/home.html", "Interface principale"),
        ("📊 Apache Superset", "http://localhost:8088", "admin/admin"),
        ("⚙️ n8n Workflows", "http://localhost:5678", "admin/admin"),
        ("🏗️ IFC.js Viewer", "http://localhost:3000", "Upload IFC"),
        ("🏢 ERPNext", "http://localhost:8000", "Gestion projet"),
    ]
    
    print("\n🌐 SERVICES DISPONIBLES:")
    for name, url, info in services:
        print(f"  {name}")
        print(f"    URL: {url}")
        print(f"    Info: {info}")
        print()
    
    print("📋 PROCHAINES ÉTAPES:")
    print("1. Cliquez sur le bouton BI flottant dans BIMEX")
    print("2. Testez les exports vers chaque plateforme")
    print("3. Configurez vos dashboards dans Superset")
    print("4. Créez vos workflows dans n8n")
    print("\n📖 Consultez GUIDE_OPENSOURCE_BI.md pour plus d'infos")

def cleanup_on_exit(bimex_process):
    """Nettoie les processus à la sortie"""
    print("\n🛑 Arrêt du système...")
    
    if bimex_process:
        bimex_process.terminate()
        print("✅ Serveur BIMEX arrêté")
    
    try:
        subprocess.run(["docker-compose", "-f", "docker-compose-bi.yml", "down"], 
                      capture_output=True)
        print("✅ Services Docker arrêtés")
    except:
        pass

def main():
    """Fonction principale"""
    print_banner()
    
    bimex_process = None
    
    try:
        # Vérifications préliminaires
        if not Path("backend/bi_config.json").exists():
            print("❌ Configuration BI non trouvée")
            print("Exécutez d'abord: python setup_opensource_bi.py")
            return 1
        
        # Démarrage des services Docker (optionnel)
        docker_available = check_docker()
        if docker_available:
            if not start_docker_services():
                print("⚠️ Erreur avec Docker, continuons sans les services externes")
            else:
                print("⏳ Attente du démarrage des services (30s)...")
                time.sleep(30)
                
                # Vérifier les services
                services_to_check = [
                    ("Superset", "http://localhost:8088"),
                    ("n8n", "http://localhost:5678"),
                    ("IFC Viewer", "http://localhost:3000"),
                ]
                
                for name, url in services_to_check:
                    wait_for_service(name, url, timeout=30)
        
        # Démarrage du serveur BIMEX
        bimex_process = start_bimex_server()
        if not bimex_process:
            print("❌ Impossible de démarrer le serveur BIMEX")
            return 1
        
        # Attendre que BIMEX soit prêt
        print("⏳ Attente du serveur BIMEX (10s)...")
        time.sleep(10)
        
        # Tests automatiques
        tests_passed = run_tests()
        
        # Ouverture du navigateur
        def delayed_browser_open():
            time.sleep(5)
            open_browser_tabs()
        
        browser_thread = threading.Thread(target=delayed_browser_open)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Affichage du résumé
        display_summary()
        
        # Attendre l'interruption utilisateur
        print("\n⌨️ Appuyez sur Ctrl+C pour arrêter le système")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return 1
    
    finally:
        cleanup_on_exit(bimex_process)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
