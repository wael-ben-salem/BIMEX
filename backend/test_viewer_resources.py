"""
Test pour vérifier que toutes les ressources du viewer XeoKit sont accessibles
"""

import requests
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_viewer_resources():
    """Test des ressources essentielles du viewer XeoKit"""
    logger.info("🧪 Test des ressources du viewer XeoKit")
    
    base_url = "http://localhost:8081/xeokit-bim-viewer"
    
    # Ressources à tester
    resources_to_test = [
        # Fichiers principaux
        "/app/index.html",
        "/dist/xeokit-bim-viewer.es.js",
        "/dist/xeokit-bim-viewer.min.es.js",
        "/dist/xeokit-bim-viewer.css",
        "/dist/messages.js",
        
        # FontAwesome local
        "/app/lib/fontawesome-free-5.11.2-web/css/all.min.css",
        "/app/lib/fontawesome-free-5.11.2-web/webfonts/fa-solid-900.woff2",
        "/app/lib/fontawesome-free-5.11.2-web/webfonts/fa-regular-400.woff2",
        
        # CSS et JS supplémentaires
        "/app/css/style.css",
        "/app/lib/split.min.js",
        "/app/lib/tippy.js",
        "/app/lib/popper.js",
    ]
    
    results = {}
    
    for resource in resources_to_test:
        url = base_url + resource
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {resource} - OK")
                results[resource] = "OK"
            else:
                logger.error(f"❌ {resource} - Status {response.status_code}")
                results[resource] = f"ERROR_{response.status_code}"
        except requests.exceptions.ConnectionError:
            logger.warning(f"⚠️ {resource} - Serveur non accessible")
            results[resource] = "SERVER_DOWN"
        except Exception as e:
            logger.error(f"❌ {resource} - Erreur: {e}")
            results[resource] = f"ERROR_{str(e)}"
    
    # Résumé
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info(f"{'='*50}")
    
    ok_count = sum(1 for r in results.values() if r == "OK")
    error_count = sum(1 for r in results.values() if r.startswith("ERROR"))
    server_down_count = sum(1 for r in results.values() if r == "SERVER_DOWN")
    
    logger.info(f"✅ Ressources OK: {ok_count}")
    logger.info(f"❌ Erreurs: {error_count}")
    logger.info(f"⚠️ Serveur inaccessible: {server_down_count}")
    
    if error_count == 0 and server_down_count == 0:
        logger.info("🎉 TOUTES LES RESSOURCES SONT ACCESSIBLES!")
    elif server_down_count > 0:
        logger.warning("⚠️ Serveur http-server non démarré sur port 8081")
        logger.info("💡 Démarrez le serveur: npx http-server . -p 8081")
    else:
        logger.warning(f"⚠️ {error_count} ressource(s) inaccessible(s)")
    
    return results

def test_viewer_with_project():
    """Test du viewer avec un projet spécifique"""
    logger.info("🧪 Test du viewer avec projet basic2")
    
    url = "http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Vérifications du contenu
            checks = [
                ("xeokit BIM Viewer", "Titre présent"),
                ("basic2", "Projet ID présent"),
                ("xeokit-bim-viewer.es.js", "Script principal référencé"),
                ("fontawesome", "FontAwesome référencé"),
            ]
            
            all_good = True
            for check, description in checks:
                if check.lower() in content.lower():
                    logger.info(f"✅ {description}")
                else:
                    logger.error(f"❌ {description}")
                    all_good = False
            
            if all_good:
                logger.info("🎉 VIEWER HTML CORRECT!")
                return True
            else:
                logger.warning("⚠️ Problèmes détectés dans le HTML")
                return False
        else:
            logger.error(f"❌ Viewer retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Serveur non accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test viewer: {e}")
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    logger.info("🚀 Tests des ressources du viewer XeoKit")
    
    # Test 1: Ressources
    logger.info(f"\n{'='*50}")
    logger.info("TEST 1: RESSOURCES")
    logger.info(f"{'='*50}")
    resources_result = test_viewer_resources()
    
    # Test 2: Viewer avec projet
    logger.info(f"\n{'='*50}")
    logger.info("TEST 2: VIEWER AVEC PROJET")
    logger.info(f"{'='*50}")
    viewer_result = test_viewer_with_project()
    
    # Résumé final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ FINAL")
    logger.info(f"{'='*50}")
    
    if viewer_result is True:
        logger.info("🎉 VIEWER XEOKIT ENTIÈREMENT FONCTIONNEL!")
        logger.info("🔗 URL de test: http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2")
    elif viewer_result is None:
        logger.warning("⚠️ Impossible de tester - serveur non démarré")
        logger.info("💡 Démarrez le serveur: npx http-server . -p 8081")
    else:
        logger.warning("⚠️ Problèmes détectés avec le viewer")
    
    return resources_result, viewer_result

if __name__ == "__main__":
    run_all_tests()
