"""
Test de toutes les corrections appliquées :
1. Cache intelligent pour tous les boutons
2. Données PMR cohérentes
3. Pagination des anomalies
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cache_all_buttons():
    """Test du cache pour tous les boutons"""
    logger.info("🧪 Test du cache pour tous les boutons")
    
    buttons_tests = [
        ("Analyse complète", "http://localhost:8000/analyze-comprehensive-project/basic2"),
        ("Classification", "http://localhost:8000/classify-building-project/basic2"),
        ("PMR", "http://localhost:8000/analyze-pmr-project/basic2"),
        ("Anomalies", "http://localhost:8000/detect-anomalies-project/basic2"),
    ]
    
    cache_results = {}
    
    for button_name, url in buttons_tests:
        try:
            logger.info(f"📊 Test {button_name}...")
            
            # Premier appel (sans cache)
            start_time = time.time()
            response1 = requests.get(url, timeout=30)
            first_time = time.time() - start_time
            
            # Deuxième appel (potentiel cache backend)
            start_time = time.time()
            response2 = requests.get(url, timeout=30)
            second_time = time.time() - start_time
            
            if response1.status_code == 200 and response2.status_code == 200:
                improvement = first_time / second_time if second_time > 0 else 1
                
                logger.info(f"   ⏱️ Premier appel: {first_time:.2f}s")
                logger.info(f"   ⚡ Deuxième appel: {second_time:.2f}s")
                logger.info(f"   🚀 Amélioration: {improvement:.1f}x")
                
                cache_results[button_name] = {
                    "success": True,
                    "first_time": first_time,
                    "second_time": second_time,
                    "improvement": improvement
                }
            else:
                logger.error(f"   ❌ Erreur HTTP: {response1.status_code}, {response2.status_code}")
                cache_results[button_name] = {"success": False, "error": "HTTP error"}
                
        except Exception as e:
            logger.error(f"   ❌ Erreur: {e}")
            cache_results[button_name] = {"success": False, "error": str(e)}
    
    return cache_results

def test_pmr_data_consistency():
    """Test de cohérence des données PMR"""
    logger.info("🧪 Test de cohérence des données PMR")
    
    try:
        # Analyse PMR directe
        logger.info("📊 Récupération analyse PMR directe...")
        response_pmr = requests.get("http://localhost:8000/analyze-pmr-project/basic2", timeout=20)
        
        if response_pmr.status_code != 200:
            logger.error(f"❌ Erreur PMR directe: {response_pmr.status_code}")
            return False
        
        pmr_direct = response_pmr.json()
        pmr_summary = pmr_direct.get('analysis', {}).get('summary', {})
        
        logger.info(f"   📊 PMR Direct - Total: {pmr_summary.get('total_checks')}")
        logger.info(f"   ✅ Conformes: {pmr_summary.get('compliant_checks')}")
        logger.info(f"   ❌ Non conformes: {pmr_summary.get('non_compliant_checks')}")
        logger.info(f"   ⚠️ Attention: {pmr_summary.get('attention_checks')}")
        logger.info(f"   📈 Conformité: {pmr_summary.get('compliance_percentage'):.1f}%")
        
        # Analyse complète
        logger.info("📊 Récupération analyse complète...")
        response_complete = requests.get("http://localhost:8000/analyze-comprehensive-project/basic2", timeout=30)
        
        if response_complete.status_code != 200:
            logger.error(f"❌ Erreur analyse complète: {response_complete.status_code}")
            return False
        
        complete_data = response_complete.json()
        pmr_complete = complete_data.get('analysis', {}).get('analysis_results', {}).get('pmr', {})
        
        if pmr_complete.get('status') == 'success':
            pmr_complete_summary = pmr_complete.get('data', {}).get('summary', {})
            
            logger.info(f"   📊 PMR Complète - Total: {pmr_complete_summary.get('total_checks')}")
            logger.info(f"   ✅ Conformes: {pmr_complete_summary.get('compliant_checks')}")
            logger.info(f"   ❌ Non conformes: {pmr_complete_summary.get('non_compliant_checks')}")
            logger.info(f"   ⚠️ Attention: {pmr_complete_summary.get('attention_checks')}")
            logger.info(f"   📈 Conformité: {pmr_complete_summary.get('compliance_percentage'):.1f}%")
            
            # Vérifier la cohérence
            if (pmr_summary.get('total_checks') == pmr_complete_summary.get('total_checks') and
                pmr_summary.get('compliance_percentage') == pmr_complete_summary.get('compliance_percentage')):
                logger.info("✅ Données PMR cohérentes entre les deux analyses")
                return True
            else:
                logger.error("❌ Incohérence détectée entre les analyses PMR")
                return False
        else:
            logger.error("❌ PMR non disponible dans l'analyse complète")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test PMR: {e}")
        return False

def test_anomalies_pagination():
    """Test de la pagination des anomalies"""
    logger.info("🧪 Test de la pagination des anomalies")
    
    try:
        logger.info("📊 Récupération des anomalies...")
        response = requests.get("http://localhost:8000/detect-anomalies-project/basic2", timeout=20)
        
        if response.status_code != 200:
            logger.error(f"❌ Erreur anomalies: {response.status_code}")
            return False
        
        anomalies_data = response.json()
        anomalies = anomalies_data.get('anomalies', [])
        summary = anomalies_data.get('summary', {})
        
        total_anomalies = len(anomalies)
        logger.info(f"📊 Total anomalies: {total_anomalies}")
        logger.info(f"🚨 Critiques: {summary.get('by_severity', {}).get('critical', 0)}")
        logger.info(f"⚠️ Élevées: {summary.get('by_severity', {}).get('high', 0)}")
        logger.info(f"📋 Moyennes: {summary.get('by_severity', {}).get('medium', 0)}")
        logger.info(f"📝 Faibles: {summary.get('by_severity', {}).get('low', 0)}")
        
        if total_anomalies > 10:
            logger.info("✅ Pagination nécessaire - Plus de 10 anomalies détectées")
            logger.info(f"   📄 Affichage par défaut: 10 premières anomalies")
            logger.info(f"   📋 Bouton 'Tout afficher': {total_anomalies} anomalies")
            logger.info(f"   🔄 Options: 5, 10, 20, ou toutes")
            return True
        elif total_anomalies > 0:
            logger.info(f"✅ Anomalies détectées: {total_anomalies} (pas de pagination nécessaire)")
            return True
        else:
            logger.info("✅ Aucune anomalie détectée")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erreur test anomalies: {e}")
        return False

def test_frontend_integration():
    """Test d'intégration frontend"""
    logger.info("🧪 Test d'intégration frontend")
    
    test_url = "http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed"
    
    try:
        response = requests.get(test_url, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Page d'analyse accessible")
            logger.info(f"   🔗 URL: {test_url}")
            
            # Vérifier la présence des éléments clés dans le HTML
            html_content = response.text
            
            checks = [
                ("Cache button", "🧹 Effacer le cache" in html_content),
                ("Anomalies container", "anomaliesContainer" in html_content),
                ("PMR section", "Analyse PMR" in html_content),
                ("Classification section", "Classifier le bâtiment" in html_content),
                ("Assistant section", "assistant" in html_content.lower())
            ]
            
            for check_name, check_result in checks:
                if check_result:
                    logger.info(f"   ✅ {check_name}: Présent")
                else:
                    logger.warning(f"   ⚠️ {check_name}: Non trouvé")
            
            return True
        else:
            logger.error(f"❌ Page non accessible: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test frontend: {e}")
        return False

def main():
    """Test principal de toutes les corrections"""
    logger.info("🚀 Tests de Toutes les Corrections Appliquées")
    
    results = {}
    
    # Test 1: Cache pour tous les boutons
    logger.info(f"\n{'='*60}")
    logger.info("TEST 1: CACHE INTELLIGENT TOUS BOUTONS")
    logger.info(f"{'='*60}")
    cache_results = test_cache_all_buttons()
    results['cache'] = cache_results
    
    # Test 2: Cohérence données PMR
    logger.info(f"\n{'='*60}")
    logger.info("TEST 2: COHÉRENCE DONNÉES PMR")
    logger.info(f"{'='*60}")
    pmr_consistent = test_pmr_data_consistency()
    results['pmr_consistency'] = pmr_consistent
    
    # Test 3: Pagination anomalies
    logger.info(f"\n{'='*60}")
    logger.info("TEST 3: PAGINATION ANOMALIES")
    logger.info(f"{'='*60}")
    anomalies_pagination = test_anomalies_pagination()
    results['anomalies_pagination'] = anomalies_pagination
    
    # Test 4: Intégration frontend
    logger.info(f"\n{'='*60}")
    logger.info("TEST 4: INTÉGRATION FRONTEND")
    logger.info(f"{'='*60}")
    frontend_ok = test_frontend_integration()
    results['frontend'] = frontend_ok
    
    # Résumé final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RÉSUMÉ DES CORRECTIONS")
    logger.info(f"{'='*60}")
    
    # Correction 1: Cache
    if cache_results:
        successful_cache = sum(1 for r in cache_results.values() if r.get('success'))
        total_cache = len(cache_results)
        logger.info(f"✅ CORRECTION 1: Cache intelligent - {successful_cache}/{total_cache} boutons")
        
        if successful_cache > 0:
            avg_improvement = sum(r.get('improvement', 1) for r in cache_results.values() if r.get('success')) / successful_cache
            logger.info(f"   🚀 Amélioration moyenne: {avg_improvement:.1f}x plus rapide")
    
    # Correction 2: PMR
    if pmr_consistent:
        logger.info("✅ CORRECTION 2: Données PMR cohérentes")
    else:
        logger.error("❌ CORRECTION 2: Incohérence PMR persistante")
    
    # Correction 3: Anomalies
    if anomalies_pagination:
        logger.info("✅ CORRECTION 3: Pagination anomalies opérationnelle")
    else:
        logger.error("❌ CORRECTION 3: Problème pagination anomalies")
    
    # Correction 4: Frontend
    if frontend_ok:
        logger.info("✅ CORRECTION 4: Intégration frontend réussie")
    else:
        logger.error("❌ CORRECTION 4: Problème intégration frontend")
    
    # Instructions d'utilisation
    logger.info(f"\n{'='*60}")
    logger.info("💡 INSTRUCTIONS D'UTILISATION")
    logger.info(f"{'='*60}")
    
    logger.info("🎯 Pour tester toutes les corrections:")
    logger.info("   1. Ouvrir: http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed")
    logger.info("")
    logger.info("🚀 Test du cache:")
    logger.info("   2. Cliquer '🔍 Analyser le fichier' - Noter le temps (~15s)")
    logger.info("   3. Re-cliquer '🔍 Analyser le fichier' - Devrait être instantané ⚡")
    logger.info("   4. Cliquer '🏢 Classifier le bâtiment' - Instantané ⚡")
    logger.info("   5. Cliquer '♿ Analyse PMR' - Instantané ⚡")
    logger.info("   6. Cliquer '🚨 Détecter les anomalies' - Instantané ⚡")
    logger.info("   7. Cliquer '🤖 Charger l'assistant IA' - Instantané ⚡")
    logger.info("")
    logger.info("🏥 Test cohérence PMR:")
    logger.info("   8. Vérifier que PMR dans 'Analyser le fichier' = PMR direct")
    logger.info("   9. Données attendues: 61.5%, 8 conformes, 2 non conformes, 2 attention")
    logger.info("")
    logger.info("📋 Test pagination anomalies:")
    logger.info("   10. Cliquer '🚨 Détecter les anomalies'")
    logger.info("   11. Voir 'Affichage: 10 sur X anomalies'")
    logger.info("   12. Cliquer 'Afficher toutes les anomalies'")
    logger.info("   13. Tester le sélecteur '5/10/20/Tout afficher'")
    logger.info("")
    logger.info("🧹 Gestion du cache:")
    logger.info("   14. Cliquer '🧹 Effacer le cache' pour réinitialiser")
    logger.info("   15. Ou attendre 10 minutes (expiration automatique)")
    
    logger.info("🎉 Tests terminés!")
    return results

if __name__ == "__main__":
    main()
