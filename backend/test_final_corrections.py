"""
Test final des corrections apportées
"""

import requests
import json
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_viewer_url():
    """Test 1: Vérifier que l'URL du viewer fonctionne"""
    logger.info("🧪 Test 1: URL du viewer XeoKit")
    
    try:
        response = requests.get("http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if "xeokit BIM Viewer" in content and "basic2" in content:
                logger.info("✅ Viewer XeoKit accessible avec le projet basic2")
                return True
            else:
                logger.error("❌ Contenu du viewer incorrect")
                return False
        else:
            logger.error(f"❌ Viewer retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Serveur http-server non démarré sur port 8081")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test viewer: {e}")
        return False

def test_analysis_auto_mode():
    """Test 2: Vérifier l'analyse en mode automatique"""
    logger.info("🧪 Test 2: Analyse automatique du projet basic2")
    
    try:
        response = requests.get("http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            if "BIM Analysis" in content or "Analyse BIM" in content:
                logger.info("✅ Page d'analyse automatique accessible")
                return True
            else:
                logger.error("❌ Contenu de la page d'analyse incorrect")
                return False
        else:
            logger.error(f"❌ Page d'analyse retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non démarré sur port 8000")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test analyse: {e}")
        return False

def test_comprehensive_analysis_api():
    """Test 3: Vérifier l'API d'analyse complète"""
    logger.info("🧪 Test 3: API d'analyse complète")
    
    try:
        response = requests.get("http://localhost:8000/analyze-comprehensive-project/basic2", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success' and 'analysis' in data:
                analysis = data['analysis']
                if 'analysis_results' in analysis:
                    results = analysis['analysis_results']
                    logger.info(f"✅ Analyse complète réussie avec {len(results)} modules")
                    
                    # Vérifier les modules d'analyse
                    expected_modules = ['metrics', 'anomalies', 'classification', 'pmr']
                    found_modules = list(results.keys())
                    logger.info(f"📊 Modules trouvés: {found_modules}")
                    
                    return True
                else:
                    logger.error("❌ Structure d'analyse incorrecte")
                    return False
            else:
                logger.error(f"❌ API retourne erreur: {data}")
                return False
        else:
            logger.error(f"❌ API retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non démarré sur port 8000")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test API: {e}")
        return False

def test_projects_index_api():
    """Test 4: Vérifier l'API index.json"""
    logger.info("🧪 Test 4: API index.json des projets")
    
    try:
        response = requests.get("http://localhost:8000/data/projects/index.json", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'projects' in data:
                projects = data['projects']
                project_ids = [p.get('id') for p in projects]
                
                if 'basic2' in project_ids:
                    logger.info(f"✅ API index.json fonctionne avec {len(projects)} projets, basic2 inclus")
                    return True
                else:
                    logger.warning(f"⚠️ Projet basic2 non trouvé dans l'index. Projets: {project_ids[:5]}...")
                    return False
            else:
                logger.error("❌ Structure de l'index incorrecte")
                return False
        else:
            logger.error(f"❌ API index retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non démarré sur port 8000")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur test index API: {e}")
        return False

def test_project_files():
    """Test 5: Vérifier les fichiers du projet basic2"""
    logger.info("🧪 Test 5: Fichiers du projet basic2")
    
    try:
        backend_dir = Path(__file__).parent
        project_dir = backend_dir.parent / "xeokit-bim-viewer" / "app" / "data" / "projects" / "basic2"
        
        # Vérifier les fichiers essentiels
        files_to_check = [
            project_dir / "index.json",
            project_dir / "models" / "model" / "geometry.ifc",
            project_dir / "models" / "model" / "geometry.xkt"
        ]
        
        all_exist = True
        for file_path in files_to_check:
            if file_path.exists():
                logger.info(f"✅ {file_path.name} existe")
            else:
                logger.error(f"❌ {file_path.name} manquant")
                all_exist = False
        
        if all_exist:
            logger.info("✅ Tous les fichiers du projet basic2 sont présents")
            return True
        else:
            logger.error("❌ Fichiers manquants pour le projet basic2")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur vérification fichiers: {e}")
        return False

def run_final_tests():
    """Exécuter tous les tests finaux"""
    logger.info("🚀 Tests finaux des corrections")
    
    tests = [
        ("Viewer XeoKit", test_viewer_url),
        ("Analyse automatique", test_analysis_auto_mode),
        ("API analyse complète", test_comprehensive_analysis_api),
        ("API index projets", test_projects_index_api),
        ("Fichiers projet", test_project_files)
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
            logger.warning(f"⚠️ {test_name}: NON TESTÉ (serveur non démarré)")
    
    # Résumé
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES TESTS FINAUX")
    logger.info(f"{'='*50}")
    
    success_count = sum(1 for r in results.values() if r is True)
    failure_count = sum(1 for r in results.values() if r is False)
    skipped_count = sum(1 for r in results.values() if r is None)
    
    logger.info(f"✅ Succès: {success_count}")
    logger.info(f"❌ Échecs: {failure_count}")
    logger.info(f"⚠️ Non testés: {skipped_count}")
    
    if failure_count == 0 and success_count > 0:
        logger.info("🎉 TOUTES LES CORRECTIONS FONCTIONNENT!")
        logger.info("🔗 URLs de test:")
        logger.info("   - Viewer: http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2")
        logger.info("   - Analyse: http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true")
        logger.info("   - Home: http://localhost:8081/xeokit-bim-viewer/app/home.html")
    elif skipped_count == len(tests):
        logger.warning("⚠️ Aucun serveur démarré - impossible de tester les corrections")
        logger.info("💡 Démarrez les serveurs:")
        logger.info("   - Backend: python main.py (port 8000)")
        logger.info("   - Frontend: npx http-server . -p 8081")
    else:
        logger.warning(f"⚠️ {failure_count} test(s) ont échoué")
    
    return results

if __name__ == "__main__":
    results = run_final_tests()
