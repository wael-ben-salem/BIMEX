"""
Test des améliorations d'affichage pour la classification et l'analyse
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_classification_display():
    """Test de l'affichage amélioré de la classification"""
    logger.info("🧪 Test de l'affichage de classification amélioré")
    
    try:
        response = requests.get("http://localhost:8000/classify-building-project/basic2", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            logger.info("✅ Réponse de classification reçue")
            logger.info(f"📊 Clés disponibles: {list(data.keys())}")
            
            # Vérifier la structure de classification
            if 'classification' in data:
                classification = data['classification']
                logger.info(f"🏢 Classification: {classification}")
                
                if 'building_type' in classification:
                    logger.info(f"   Type: {classification['building_type']}")
                if 'confidence' in classification:
                    logger.info(f"   Confiance: {classification['confidence'] * 100:.1f}%")
                if 'classification_method' in classification:
                    logger.info(f"   Méthode: {classification['classification_method']}")
                
                return True
            else:
                logger.warning("⚠️ Pas de données de classification dans la réponse")
                return False
        else:
            logger.error(f"❌ Status HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_comprehensive_analysis_display():
    """Test de l'affichage amélioré de l'analyse complète"""
    logger.info("🧪 Test de l'affichage d'analyse complète amélioré")
    
    try:
        response = requests.get("http://localhost:8000/analyze-comprehensive-project/basic2", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            logger.info("✅ Réponse d'analyse complète reçue")
            
            if 'analysis' in data and 'analysis_results' in data['analysis']:
                results = data['analysis']['analysis_results']
                
                # Test des anomalies
                if 'anomalies' in results:
                    anomalies = results['anomalies']
                    logger.info(f"🚨 Anomalies: {anomalies.get('status')}")
                    if anomalies.get('data'):
                        total = anomalies['data'].get('total_anomalies', 0)
                        logger.info(f"   Total: {total} anomalies")
                
                # Test de la classification
                if 'classification' in results:
                    classification = results['classification']
                    logger.info(f"🏢 Classification: {classification.get('status')}")
                    if classification.get('data'):
                        building_type = classification['data'].get('building_type')
                        confidence = classification['data'].get('confidence', 0) * 100
                        logger.info(f"   Type: {building_type} ({confidence:.1f}%)")
                
                # Test PMR
                if 'pmr' in results:
                    pmr = results['pmr']
                    logger.info(f"♿ PMR: {pmr.get('status')}")
                    if pmr.get('data'):
                        total_checks = pmr['data'].get('total_checks', 0)
                        logger.info(f"   Vérifications: {total_checks}")
                
                return True
            else:
                logger.warning("⚠️ Structure d'analyse inattendue")
                return False
        else:
            logger.error(f"❌ Status HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_frontend_pages():
    """Test des pages frontend"""
    logger.info("🧪 Test des pages frontend")
    
    pages_to_test = [
        ("Page d'analyse", "http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed"),
        ("Page d'accueil viewer", "http://localhost:8081/xeokit-bim-viewer/app/home.html"),
    ]
    
    results = {}
    
    for page_name, url in pages_to_test:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # Vérifications spécifiques
                checks = []
                if "analysis" in url:
                    checks = [
                        ("displayClassificationResults", "Fonction d'affichage classification"),
                        ("displayAnalysisResults", "Fonction d'affichage analyse"),
                        ("metric-card", "Cartes de métriques"),
                        ("Classification du Bâtiment", "Section classification"),
                    ]
                else:
                    checks = [
                        ("xeokit", "Référence XeoKit"),
                        ("basic2", "Projet basic2"),
                    ]
                
                page_ok = True
                for check, description in checks:
                    if check.lower() in content.lower():
                        logger.info(f"   ✅ {description}")
                    else:
                        logger.warning(f"   ⚠️ {description} - Non trouvé")
                        page_ok = False
                
                results[page_name] = page_ok
                logger.info(f"{'✅' if page_ok else '⚠️'} {page_name}: {'OK' if page_ok else 'Problèmes détectés'}")
            else:
                logger.error(f"❌ {page_name}: Status {response.status_code}")
                results[page_name] = False
                
        except Exception as e:
            logger.error(f"❌ {page_name}: Erreur {e}")
            results[page_name] = False
    
    return results

def main():
    """Test principal des améliorations d'affichage"""
    logger.info("🚀 Tests des améliorations d'affichage")
    
    tests = [
        ("Classification améliorée", test_classification_display),
        ("Analyse complète améliorée", test_comprehensive_analysis_display),
        ("Pages frontend", test_frontend_pages)
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
        elif isinstance(result, dict):
            success_count = sum(1 for r in result.values() if r)
            total_count = len(result)
            logger.info(f"📊 {test_name}: {success_count}/{total_count} réussis")
            results[test_name] = success_count == total_count
        else:
            logger.error(f"❌ {test_name}: ÉCHEC")
    
    # Résumé final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES AMÉLIORATIONS")
    logger.info(f"{'='*50}")
    
    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    
    logger.info(f"✅ Tests réussis: {success_count}/{total_count}")
    
    if success_count == total_count:
        logger.info("🎉 TOUTES LES AMÉLIORATIONS FONCTIONNENT!")
        logger.info("🔗 URLs de test:")
        logger.info("   - Classification: http://localhost:8000/classify-building-project/basic2")
        logger.info("   - Analyse complète: http://localhost:8000/analyze-comprehensive-project/basic2")
        logger.info("   - Interface: http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed")
    else:
        logger.warning(f"⚠️ {total_count - success_count} amélioration(s) ont des problèmes")
    
    return results

if __name__ == "__main__":
    main()
