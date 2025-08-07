#!/usr/bin/env python3
"""
🚀 SCRIPT DE CONFIGURATION AUTOMATIQUE DU SYSTÈME BI BIMEX
Configure automatiquement tout le système Business Intelligence
"""

import os
import json
import subprocess
import sys
from pathlib import Path
import shutil

def print_step(step, message):
    """Affiche une étape avec style"""
    print(f"\n🔧 ÉTAPE {step}: {message}")
    print("=" * 60)

def install_requirements():
    """Installe les dépendances Python nécessaires"""
    print_step(1, "INSTALLATION DES DÉPENDANCES")
    
    requirements = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "requests",
        "pandas",
        "python-dateutil",
        "aiofiles",
        "jinja2"
    ]
    
    for req in requirements:
        try:
            print(f"📦 Installation de {req}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ {req} installé avec succès")
        except subprocess.CalledProcessError:
            print(f"⚠️ Erreur installation {req} - continuons...")

def create_bi_config():
    """Crée la configuration BI avec des endpoints de test"""
    print_step(2, "CRÉATION DE LA CONFIGURATION BI")
    
    config = {
        "connectors": [
            {
                "name": "PowerBI_Demo",
                "type": "powerbi",
                "endpoint": "https://api.powerbi.com/v1.0/myorg/datasets",
                "credentials": {
                    "client_id": "demo_client_id",
                    "client_secret": "demo_client_secret",
                    "tenant_id": "demo_tenant_id"
                },
                "active": True,
                "last_sync": None
            },
            {
                "name": "Tableau_Demo",
                "type": "tableau",
                "endpoint": "https://demo-tableau-server.com/api/3.0",
                "credentials": {
                    "username": "demo_user",
                    "password": "demo_password",
                    "site_id": "demo_site"
                },
                "active": True,
                "last_sync": None
            },
            {
                "name": "n8n_Demo",
                "type": "n8n",
                "endpoint": "https://demo-n8n.com/webhook",
                "credentials": {
                    "webhook_id": "demo_webhook_123",
                    "api_key": "demo_api_key_456"
                },
                "active": True,
                "last_sync": None
            },
            {
                "name": "ERP_Demo",
                "type": "erp",
                "endpoint": "https://demo-erp-system.com/api",
                "credentials": {
                    "username": "demo_erp_user",
                    "password": "demo_erp_password",
                    "client": "100"
                },
                "active": True,
                "last_sync": None
            }
        ],
        "settings": {
            "auto_sync_enabled": True,
            "sync_interval_minutes": 60,
            "max_history_entries": 1000,
            "notification_enabled": True
        }
    }
    
    config_path = Path("backend/bi_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration BI créée : {config_path}")
    return config_path

def create_demo_data():
    """Crée des données de démonstration"""
    print_step(3, "CRÉATION DES DONNÉES DE DÉMONSTRATION")
    
    demo_projects = {
        "projects": [
            {
                "id": "Test1",
                "name": "Maison Test 1",
                "description": "Projet de démonstration BIM",
                "created": "2024-01-15T10:00:00Z",
                "status": "active",
                "elements_count": 1247,
                "floor_area": 150.5,
                "volume": 450.0
            },
            {
                "id": "Duplex",
                "name": "Duplex Moderne",
                "description": "Duplex avec analyse BI complète",
                "created": "2024-02-01T14:30:00Z",
                "status": "active",
                "elements_count": 2156,
                "floor_area": 280.0,
                "volume": 840.0
            },
            {
                "id": "WestRiversideHospital",
                "name": "Hôpital West Riverside",
                "description": "Complexe hospitalier avec intégration ERP",
                "created": "2024-01-20T09:15:00Z",
                "status": "active",
                "elements_count": 15420,
                "floor_area": 5200.0,
                "volume": 18600.0
            }
        ]
    }
    
    demo_path = Path("backend/demo_projects.json")
    with open(demo_path, 'w', encoding='utf-8') as f:
        json.dump(demo_projects, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Données de démo créées : {demo_path}")

def create_startup_script():
    """Crée un script de démarrage automatique"""
    print_step(4, "CRÉATION DU SCRIPT DE DÉMARRAGE")
    
    startup_script = '''#!/usr/bin/env python3
"""
🚀 SCRIPT DE DÉMARRAGE AUTOMATIQUE BIMEX BI
Lance le serveur backend avec toutes les fonctionnalités BI
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    print("🚀 DÉMARRAGE DU SYSTÈME BIMEX BI")
    print("=" * 50)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("backend/main.py").exists():
        print("❌ Erreur: Lancez ce script depuis la racine du projet")
        sys.exit(1)
    
    # Changer vers le répertoire backend
    os.chdir("backend")
    
    print("📡 Démarrage du serveur backend...")
    print("🌐 URL: http://localhost:8000")
    print("🏠 Interface: http://localhost:8000/app/home.html")
    print("📊 Dashboard BI: Cliquez sur le bouton BI flottant")
    print("\\n⏳ Démarrage en cours...")
    
    # Attendre un peu puis ouvrir le navigateur
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open("http://localhost:8000/app/home.html")
            print("\\n🌐 Navigateur ouvert automatiquement")
        except:
            print("\\n🌐 Ouvrez manuellement: http://localhost:8000/app/home.html")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Démarrer le serveur
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Arrêt du serveur...")
    except Exception as e:
        print(f"\\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
'''
    
    script_path = Path("start_bimex_bi.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    # Rendre le script exécutable sur Unix
    if os.name != 'nt':
        os.chmod(script_path, 0o755)
    
    print(f"✅ Script de démarrage créé : {script_path}")

def create_user_guide():
    """Crée un guide utilisateur complet"""
    print_step(5, "CRÉATION DU GUIDE UTILISATEUR")
    
    guide = '''# 🚀 GUIDE UTILISATEUR - SYSTÈME BI BIMEX

## 🎯 DÉMARRAGE RAPIDE

### 1. Lancer le système
```bash
python start_bimex_bi.py
```

### 2. Accéder à l'interface
- **URL principale**: http://localhost:8000/app/home.html
- **Cliquez sur le bouton BI flottant** (coin supérieur droit)

## 📊 UTILISATION DU DASHBOARD BI

### Widgets Disponibles
- 🟡 **Power BI**: Export automatique vers Power BI
- 🔵 **Tableau**: Publication vers Tableau Server  
- 🔴 **n8n**: Workflows automatisés
- 🟢 **ERP**: Synchronisation avec systèmes ERP

### Actions Rapides
- **Export Multi-Plateformes**: Exporte vers toutes les plateformes
- **Historique**: Voir toutes les synchronisations
- **Statut BI**: Vérifier l'état des connecteurs

## 🔧 CONFIGURATION

### Modifier les connecteurs
Éditez le fichier `backend/bi_config.json`:

```json
{
  "connectors": [
    {
      "name": "PowerBI_Production",
      "type": "powerbi",
      "endpoint": "https://api.powerbi.com/v1.0/myorg/datasets",
      "credentials": {
        "client_id": "VOTRE_CLIENT_ID",
        "client_secret": "VOTRE_CLIENT_SECRET",
        "tenant_id": "VOTRE_TENANT_ID"
      },
      "active": true
    }
  ]
}
```

### Projets supportés
Le système détecte automatiquement vos projets BIM dans:
- `xeokit-bim-viewer/app/data/projects/`

## 🚀 FONCTIONNALITÉS AVANCÉES

### APIs Disponibles
- `GET /bi/status` - Statut des connecteurs
- `POST /bi/export-powerbi` - Export Power BI
- `POST /bi/export-tableau` - Export Tableau
- `POST /bi/trigger-n8n-workflow` - Workflows n8n
- `POST /bi/sync-erp` - Sync ERP
- `GET /bi/sync-history` - Historique

### Workflows Automatisés
Créez des workflows n8n pour:
- Export quotidien automatique
- Alertes sur anomalies
- Synchronisation ERP temps réel

## 🛠️ DÉPANNAGE

### Problèmes courants
1. **Port 8000 occupé**: Changez le port dans `main.py`
2. **Erreur de connecteur**: Vérifiez `bi_config.json`
3. **Projet non trouvé**: Vérifiez le nom du projet

### Logs
Les logs sont affichés dans la console du serveur.

## 📞 SUPPORT
Pour toute question, consultez les logs du serveur ou vérifiez la configuration.
'''
    
    guide_path = Path("GUIDE_BI_UTILISATEUR.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"✅ Guide utilisateur créé : {guide_path}")

def main():
    """Fonction principale de configuration"""
    print("🚀 CONFIGURATION AUTOMATIQUE DU SYSTÈME BI BIMEX")
    print("=" * 60)
    print("Ce script va configurer automatiquement tout le système BI")
    print("Durée estimée: 2-3 minutes")
    
    try:
        install_requirements()
        create_bi_config()
        create_demo_data()
        create_startup_script()
        create_user_guide()
        
        print("\n" + "=" * 60)
        print("🎉 CONFIGURATION TERMINÉE AVEC SUCCÈS !")
        print("=" * 60)
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Lancez le système: python start_bimex_bi.py")
        print("2. Ouvrez: http://localhost:8000/app/home.html")
        print("3. Cliquez sur le bouton BI flottant")
        print("4. Testez les fonctionnalités BI")
        print("\n📖 Consultez GUIDE_BI_UTILISATEUR.md pour plus d'infos")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA CONFIGURATION: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
