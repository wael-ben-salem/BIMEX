"""
Script de test pour vérifier les corrections apportées
"""

import os
import sys
import json
import requests
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_index_json_access():
    """Test 1: Vérifier l'accès au fichier index.json"""
    logger.info("🧪 Test 1: Accès au fichier index.json")
    
    # Vérifier que le fichier existe physiquement
    backend_dir = Path(__file__).parent
    index_path = backend_dir.parent / "xeokit-bim-viewer" / "app" / "data" / "projects" / "index.json"
    
    if index_path.exists():
        logger.info(f"✅ Fichier index.json trouvé: {index_path}")
        
        # Lire le contenu
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                projects_count = len(data.get('projects', []))
                logger.info(f"✅ Fichier index.json valide avec {projects_count} projets")
                return True
        except Exception as e:
            logger.error(f"❌ Erreur lecture index.json: {e}")
            return False
    else:
        logger.error(f"❌ Fichier index.json non trouvé: {index_path}")
        return False

def test_api_index_json_route():
    """Test 2: Vérifier la route API pour index.json"""
    logger.info("🧪 Test 2: Route API /data/projects/index.json")
    
    try:
        # Tester la route API (supposer que le serveur tourne sur localhost:8081)
        response = requests.get("http://localhost:8081/data/projects/index.json", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            projects_count = len(data.get('projects', []))
            logger.info(f"✅ Route API fonctionne avec {projects_count} projets")
            return True
        else:
            logger.error(f"❌ Route API retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Serveur non démarré - impossible de tester la route API")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test route API: {e}")
        return False

def test_xkt_model_configuration():
    """Test 3: Vérifier la configuration XKTModel"""
    logger.info("🧪 Test 3: Configuration XKTModel maxIndicesForEdge")
    
    try:
        # Vérifier le fichier XKTModel.js
        backend_dir = Path(__file__).parent
        xkt_model_path = backend_dir.parent / "src" / "XKTModel" / "XKTModel.js"
        
        if xkt_model_path.exists():
            with open(xkt_model_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Vérifier que la valeur a été modifiée
                if "maxIndicesForEdge || 200000" in content:
                    logger.info("✅ Configuration XKTModel mise à jour (200000)")
                    return True
                elif "maxIndicesForEdge || 10000" in content:
                    logger.error("❌ Configuration XKTModel non mise à jour (encore 10000)")
                    return False
                else:
                    logger.warning("⚠️ Configuration XKTModel non trouvée")
                    return None
        else:
            logger.error(f"❌ Fichier XKTModel.js non trouvé: {xkt_model_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test XKTModel: {e}")
        return False

def test_comprehensive_analyzer():
    """Test 4: Vérifier l'analyseur complet"""
    logger.info("🧪 Test 4: Analyseur IFC complet")
    
    try:
        # Importer l'analyseur
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ifc_analyzer import ComprehensiveIFCAnalyzer
        
        logger.info("✅ ComprehensiveIFCAnalyzer importé avec succès")
        
        # Vérifier qu'un fichier IFC de test existe
        backend_dir = Path(__file__).parent
        test_ifc_path = backend_dir.parent / "tests" / "BasicHouse.ifc"
        
        if test_ifc_path.exists():
            logger.info(f"✅ Fichier IFC de test trouvé: {test_ifc_path}")
            
            # Tester l'initialisation
            try:
                analyzer = ComprehensiveIFCAnalyzer(str(test_ifc_path))
                logger.info("✅ Analyseur initialisé avec succès")
                return True
            except Exception as e:
                logger.error(f"❌ Erreur initialisation analyseur: {e}")
                return False
        else:
            logger.warning(f"⚠️ Fichier IFC de test non trouvé: {test_ifc_path}")
            return None
            
    except ImportError as e:
        logger.error(f"❌ Erreur import ComprehensiveIFCAnalyzer: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur test analyseur: {e}")
        return False

def test_api_comprehensive_route():
    """Test 5: Vérifier la route API complète"""
    logger.info("🧪 Test 5: Route API /analyze-comprehensive-project")

    try:
        # Tester avec le projet BasicHouse
        response = requests.get("http://localhost:8000/analyze-comprehensive-project/BasicHouse", timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                logger.info("✅ Route API analyse complète fonctionne")
                return True
            else:
                logger.error(f"❌ Route API retourne erreur: {data}")
                return False
        else:
            logger.error(f"❌ Route API retourne status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Serveur non démarré - impossible de tester la route API")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test route API: {e}")
        return False

def test_xeokit_viewer_route():
    """Test 6: Vérifier la route du viewer XeoKit"""
    logger.info("🧪 Test 6: Route viewer XeoKit /index.html")

    try:
        # Tester la route index.html
        response = requests.get("http://localhost:8000/index.html", timeout=10)

        if response.status_code == 200:
            content = response.text
            if "xeokit BIM Viewer" in content:
                logger.info("✅ Route viewer XeoKit fonctionne")
                return True
            else:
                logger.error("❌ Contenu du viewer incorrect")
                return False
        else:
            logger.error(f"❌ Route viewer retourne status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Serveur non démarré - impossible de tester la route viewer")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test route viewer: {e}")
        return False

def run_all_tests():
    """Exécuter tous les tests"""
    logger.info("🚀 Début des tests de correction")
    
    tests = [
        ("Accès index.json", test_index_json_access),
        ("Route API index.json", test_api_index_json_route),
        ("Configuration XKTModel", test_xkt_model_configuration),
        ("Analyseur complet", test_comprehensive_analyzer),
        ("Route API complète", test_api_comprehensive_route),
        ("Route viewer XeoKit", test_xeokit_viewer_route)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        result = test_func()
        results[test_name] = result
        
        if result is True:
            logger.info(f"✅ {test_name}: SUCCÈS")
        elif result is False:
            logger.error(f"❌ {test_name}: ÉCHEC")
        else:
            logger.warning(f"⚠️ {test_name}: NON TESTÉ")
    
    # Résumé
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info(f"{'='*50}")
    
    success_count = sum(1 for r in results.values() if r is True)
    failure_count = sum(1 for r in results.values() if r is False)
    skipped_count = sum(1 for r in results.values() if r is None)
    
    logger.info(f"✅ Succès: {success_count}")
    logger.info(f"❌ Échecs: {failure_count}")
    logger.info(f"⚠️ Non testés: {skipped_count}")
    
    if failure_count == 0:
        logger.info("🎉 TOUS LES TESTS DISPONIBLES ONT RÉUSSI!")
    else:
        logger.warning(f"⚠️ {failure_count} test(s) ont échoué")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
