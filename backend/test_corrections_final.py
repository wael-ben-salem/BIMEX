"""
Test final des corrections apportées aux problèmes identifiés
"""

import requests
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_comprehensive_analysis():
    """Test de l'analyse complète corrigée"""
    logger.info("🧪 Test de l'analyse complète")
    
    try:
        response = requests.get("http://localhost:8000/analyze-comprehensive-project/basic2", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                analysis = data.get('analysis', {})
                results = analysis.get('analysis_results', {})
                
                # Vérifier que les erreurs sont corrigées
                metrics_status = results.get('metrics', {}).get('status')
                anomalies_status = results.get('anomalies', {}).get('status')
                classification_status = results.get('classification', {}).get('status')
                pmr_status = results.get('pmr', {}).get('status')
                
                logger.info(f"📊 Métriques: {metrics_status}")
                logger.info(f"🚨 Anomalies: {anomalies_status}")
                logger.info(f"🏢 Classification: {classification_status}")
                logger.info(f"♿ PMR: {pmr_status}")
                
                if metrics_status == 'success' and anomalies_status == 'success':
                    logger.info("✅ Erreurs 'analyze_ifc_file' et 'detect_anomalies' corrigées!")
                    return True
                else:
                    logger.error("❌ Erreurs encore présentes")
                    return False
            else:
                logger.error(f"❌ Analyse échouée: {data}")
                return False
        else:
            logger.error(f"❌ Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_building_classification():
    """Test de la classification du bâtiment corrigée"""
    logger.info("🧪 Test de la classification du bâtiment")
    
    try:
        response = requests.get("http://localhost:8000/classify-building-project/basic2", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            note = data.get('note', '')
            classification = data.get('classification', {})
            
            logger.info(f"📝 Note: {note}")
            
            if 'Classification complète disponible après entraînement' in note:
                logger.error("❌ Note d'entraînement encore présente")
                return False
            elif 'Classification IA terminée' in note or classification:
                logger.info("✅ Classification IA fonctionnelle!")
                if classification:
                    building_type = classification.get('building_type', 'Non défini')
                    confidence = classification.get('confidence', 0) * 100
                    logger.info(f"🏗️ Type: {building_type} (Confiance: {confidence:.1f}%)")
                return True
            else:
                logger.warning("⚠️ Classification de base seulement")
                return False
        else:
            logger.error(f"❌ Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_frontend_auto_mode():
    """Test du mode automatique du frontend"""
    logger.info("🧪 Test du mode automatique frontend")
    
    try:
        # Tester l'URL d'analyse automatique
        url = "http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Vérifications du contenu
            checks = [
                ("configureAutoMode", "Fonction de configuration auto présente"),
                ("currentFile", "Variable currentFile présente"),
                ("analyze-comprehensive-project", "Route d'analyse complète référencée"),
                ("basic2", "Projet basic2 détecté"),
            ]
            
            all_good = True
            for check, description in checks:
                if check.lower() in content.lower():
                    logger.info(f"✅ {description}")
                else:
                    logger.error(f"❌ {description}")
                    all_good = False
            
            return all_good
        else:
            logger.error(f"❌ Page d'analyse retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_list_files_api():
    """Test de l'API list-files utilisée par le frontend"""
    logger.info("🧪 Test de l'API list-files")
    
    try:
        response = requests.get("http://localhost:8000/list-files", timeout=10)
        
        if response.status_code == 200:
            files = response.json()
            
            # Chercher des fichiers pour basic2
            basic2_files = [f for f in files if 'basic2' in f.get('name', '').lower() or 'basic2' in f.get('path', '').lower()]
            
            if basic2_files:
                logger.info(f"✅ {len(basic2_files)} fichier(s) trouvé(s) pour basic2:")
                for file in basic2_files[:3]:  # Afficher les 3 premiers
                    logger.info(f"   📁 {file.get('name')} ({file.get('type')})")
                return True
            else:
                logger.warning("⚠️ Aucun fichier trouvé pour basic2")
                return False
        else:
            logger.error(f"❌ API list-files retourne status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️ Backend non accessible")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def run_all_correction_tests():
    """Exécuter tous les tests de correction"""
    logger.info("🚀 Tests des corrections appliquées")
    
    tests = [
        ("Analyse complète", test_comprehensive_analysis),
        ("Classification bâtiment", test_building_classification),
        ("Mode automatique frontend", test_frontend_auto_mode),
        ("API list-files", test_list_files_api)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"TEST: {test_name.upper()}")
        logger.info(f"{'='*50}")
        result = test_func()
        results[test_name] = result
        
        if result is True:
            logger.info(f"✅ {test_name}: SUCCÈS")
        elif result is False:
            logger.error(f"❌ {test_name}: ÉCHEC")
        else:
            logger.warning(f"⚠️ {test_name}: NON TESTÉ")
    
    # Résumé final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES CORRECTIONS")
    logger.info(f"{'='*50}")
    
    success_count = sum(1 for r in results.values() if r is True)
    failure_count = sum(1 for r in results.values() if r is False)
    skipped_count = sum(1 for r in results.values() if r is None)
    
    logger.info(f"✅ Corrections réussies: {success_count}")
    logger.info(f"❌ Corrections échouées: {failure_count}")
    logger.info(f"⚠️ Non testées: {skipped_count}")
    
    if failure_count == 0 and success_count > 0:
        logger.info("🎉 TOUTES LES CORRECTIONS FONCTIONNENT!")
        logger.info("🔗 URLs de test:")
        logger.info("   - Analyse: http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed")
        logger.info("   - Classification: http://localhost:8000/classify-building-project/basic2")
        logger.info("   - Analyse complète: http://localhost:8000/analyze-comprehensive-project/basic2")
    elif skipped_count == len(tests):
        logger.warning("⚠️ Backend non accessible - impossible de tester")
        logger.info("💡 Démarrez le backend: python main.py")
    else:
        logger.warning(f"⚠️ {failure_count} correction(s) ont échoué")
    
    return results

if __name__ == "__main__":
    results = run_all_correction_tests()
