"""
Test rapide pour vérifier que l'erreur FontAwesome est corrigée
"""

import requests
import logging
from urllib.parse import urlparse

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fontawesome_fix():
    """Test pour vérifier que FontAwesome se charge correctement"""
    logger.info("🧪 Test de correction FontAwesome")
    
    # URL du viewer
    viewer_url = "http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2"
    
    try:
        # Récupérer le contenu HTML
        response = requests.get(viewer_url, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"❌ Viewer inaccessible: Status {response.status_code}")
            return False
        
        html_content = response.text
        
        # Vérifications
        checks = [
            ("cdnjs.cloudflare.com/ajax/libs/font-awesome", "CDN FontAwesome présent"),
            ("localhost:8000/lib/fontawesome", "Référence locale problématique ABSENTE"),
            ("xeokit-bim-viewer.es.js", "Script principal présent"),
        ]
        
        results = {}
        
        for check, description in checks:
            if "ABSENTE" in description:
                # Pour cette vérification, on veut que ce soit ABSENT
                if check.lower() not in html_content.lower():
                    logger.info(f"✅ {description}")
                    results[check] = True
                else:
                    logger.error(f"❌ {description} - TROUVÉ (problème!)")
                    results[check] = False
            else:
                # Pour les autres, on veut que ce soit présent
                if check.lower() in html_content.lower():
                    logger.info(f"✅ {description}")
                    results[check] = True
                else:
                    logger.error(f"❌ {description}")
                    results[check] = False
        
        # Test du CDN FontAwesome
        logger.info("🧪 Test d'accessibilité du CDN FontAwesome...")
        cdn_url = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.11.2/css/all.min.css"
        
        try:
            cdn_response = requests.head(cdn_url, timeout=5)
            if cdn_response.status_code == 200:
                logger.info("✅ CDN FontAwesome accessible")
                results["cdn_accessible"] = True
            else:
                logger.error(f"❌ CDN FontAwesome inaccessible: Status {cdn_response.status_code}")
                results["cdn_accessible"] = False
        except Exception as e:
            logger.error(f"❌ Erreur test CDN: {e}")
            results["cdn_accessible"] = False
        
        # Résumé
        success_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        
        logger.info(f"\n{'='*50}")
        logger.info("📊 RÉSUMÉ DU TEST FONTAWESOME")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Tests réussis: {success_count}/{total_count}")
        
        if success_count == total_count:
            logger.info("🎉 PROBLÈME FONTAWESOME CORRIGÉ!")
            logger.info("💡 Le viewer devrait maintenant fonctionner sans erreur 404")
            return True
        else:
            logger.warning(f"⚠️ {total_count - success_count} problème(s) détecté(s)")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Serveur non accessible sur port 8081")
        logger.info("💡 Démarrez le serveur: npx http-server . -p 8081")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test: {e}")
        return False

def test_no_port_8000_references():
    """Vérifier qu'il n'y a plus de références au port 8000 dans index.html"""
    logger.info("🧪 Test des références au port 8000")
    
    try:
        with open("../xeokit-bim-viewer/app/index.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher les références problématiques
        problematic_refs = [
            "localhost:8000",
            "127.0.0.1:8000",
            ":8000/lib/",
            ":8000/dist/",
        ]
        
        issues_found = []
        for ref in problematic_refs:
            if ref in content:
                issues_found.append(ref)
        
        if not issues_found:
            logger.info("✅ Aucune référence problématique au port 8000 trouvée")
            return True
        else:
            logger.error(f"❌ Références problématiques trouvées: {issues_found}")
            return False
            
    except FileNotFoundError:
        logger.error("❌ Fichier index.html non trouvé")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur lecture fichier: {e}")
        return False

def run_all_tests():
    """Exécuter tous les tests de correction FontAwesome"""
    logger.info("🚀 Tests de correction FontAwesome")
    
    # Test 1: Références dans le fichier
    logger.info(f"\n{'='*50}")
    logger.info("TEST 1: RÉFÉRENCES DANS INDEX.HTML")
    logger.info(f"{'='*50}")
    file_test = test_no_port_8000_references()
    
    # Test 2: Fonctionnement du viewer
    logger.info(f"\n{'='*50}")
    logger.info("TEST 2: FONCTIONNEMENT DU VIEWER")
    logger.info(f"{'='*50}")
    viewer_test = test_fontawesome_fix()
    
    # Résumé final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ FINAL")
    logger.info(f"{'='*50}")
    
    if file_test and viewer_test:
        logger.info("🎉 CORRECTION FONTAWESOME RÉUSSIE!")
        logger.info("🔗 Testez: http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2")
    elif viewer_test is None:
        logger.warning("⚠️ Serveur non démarré - impossible de tester complètement")
    else:
        logger.warning("⚠️ Problèmes détectés")
    
    return file_test, viewer_test

if __name__ == "__main__":
    run_all_tests()
