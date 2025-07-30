"""
Test rapide des corrections appliquées
"""

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_comprehensive_analysis_structure():
    """Test de la structure de réponse de l'analyse complète"""
    logger.info("🧪 Test de la structure de réponse")
    
    try:
        response = requests.get("http://localhost:8000/analyze-comprehensive-project/basic2", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            logger.info("✅ Réponse reçue avec succès")
            logger.info(f"📊 Status: {data.get('status')}")
            
            if 'analysis' in data:
                analysis = data['analysis']
                logger.info(f"📋 Clés d'analyse: {list(analysis.keys())}")
                
                if 'analysis_results' in analysis:
                    results = analysis['analysis_results']
                    logger.info(f"🔍 Modules d'analyse: {list(results.keys())}")
                    
                    # Vérifier chaque module
                    for module, result in results.items():
                        status = result.get('status', 'unknown')
                        logger.info(f"   {module}: {status}")
                        
                        if status == 'error':
                            logger.error(f"❌ Erreur dans {module}: {result.get('message', 'Inconnue')}")
                    
                    return True
                else:
                    logger.error("❌ Pas de 'analysis_results' dans la réponse")
                    return False
            else:
                logger.error("❌ Pas de 'analysis' dans la réponse")
                return False
        else:
            logger.error(f"❌ Status HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def test_classification_fix():
    """Test de la correction de classification"""
    logger.info("🧪 Test de la correction de classification")
    
    try:
        response = requests.get("http://localhost:8000/classify-building-project/basic2", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            note = data.get('note', '')
            
            logger.info(f"📝 Note reçue: {note[:100]}...")
            
            if 'Classification IA terminée' in note:
                logger.info("✅ Classification IA fonctionnelle!")
                return True
            elif 'Classification complète disponible après entraînement' in note:
                logger.error("❌ Ancienne note encore présente")
                return False
            else:
                logger.warning("⚠️ Note différente de celle attendue")
                return False
        else:
            logger.error(f"❌ Status HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        return False

def main():
    """Test principal"""
    logger.info("🚀 Tests rapides des corrections")
    
    tests = [
        ("Structure analyse complète", test_comprehensive_analysis_structure),
        ("Correction classification", test_classification_fix)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*40}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*40}")
        
        result = test_func()
        results[test_name] = result
        
        if result:
            logger.info(f"✅ {test_name}: SUCCÈS")
        else:
            logger.error(f"❌ {test_name}: ÉCHEC")
    
    # Résumé
    logger.info(f"\n{'='*40}")
    logger.info("📊 RÉSUMÉ")
    logger.info(f"{'='*40}")
    
    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    
    logger.info(f"✅ Tests réussis: {success_count}/{total_count}")
    
    if success_count == total_count:
        logger.info("🎉 TOUTES LES CORRECTIONS FONCTIONNENT!")
    else:
        logger.warning("⚠️ Certaines corrections ont échoué")
    
    return results

if __name__ == "__main__":
    main()
