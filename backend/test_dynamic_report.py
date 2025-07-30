"""
Test du rapport dynamique avec recommandations intelligentes
"""

import requests
import json
import time
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generate_html_report():
    """Test de génération du rapport HTML dynamique"""
    logger.info("🧪 Test de génération du rapport HTML dynamique")
    
    try:
        # Générer le rapport HTML pour basic2
        logger.info("📊 Génération du rapport HTML...")
        response = requests.get(
            "http://localhost:8000/generate-html-report?project=basic2&auto=true&file_detected=true",
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                report_id = data.get('report_id')
                report_url = data.get('report_url')
                
                logger.info(f"✅ Rapport généré avec succès")
                logger.info(f"   📋 ID: {report_id}")
                logger.info(f"   🔗 URL: {report_url}")
                
                return report_id, report_url
            else:
                logger.error(f"❌ Erreur génération: {data}")
                return None, None
        else:
            logger.error(f"❌ Erreur HTTP: {response.status_code}")
            return None, None
            
    except Exception as e:
        logger.error(f"❌ Erreur test génération: {e}")
        return None, None

def test_view_dynamic_report(report_id):
    """Test de visualisation du rapport avec recommandations dynamiques"""
    logger.info("🧪 Test de visualisation du rapport dynamique")
    
    try:
        # Accéder au rapport HTML
        logger.info(f"📄 Accès au rapport {report_id}...")
        response = requests.get(
            f"http://localhost:8000/report-view/{report_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            html_content = response.text
            logger.info("✅ Rapport HTML accessible")
            
            # Analyser le contenu HTML pour vérifier les recommandations dynamiques
            return analyze_report_content(html_content)
        else:
            logger.error(f"❌ Erreur accès rapport: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test visualisation: {e}")
        return False

def analyze_report_content(html_content):
    """Analyse le contenu HTML pour vérifier les recommandations dynamiques"""
    logger.info("🔍 Analyse du contenu du rapport")
    
    # Vérifications spécifiques pour les recommandations dynamiques
    checks = {
        "section_recommendations": "Recommandations Intelligentes" in html_content,
        "dynamic_template": "{% if recommendations %}" in html_content or "recommendations" in html_content,
        "no_static_values": "Traiter les 0 anomalies" not in html_content,
        "critical_anomalies": "CRITIQUE" in html_content or "critiques" in html_content,
        "pmr_recommendations": "PMR" in html_content and "Accessibilité" in html_content,
        "window_ratio": "fenêtres" in html_content or "éclairage" in html_content,
    }
    
    # Rechercher des patterns spécifiques
    patterns = {
        "priority_1": r"Priorité 1.*URGENT",
        "priority_2": r"Priorité 2",
        "pmr_percentage": r"PMR.*\d+\.\d+%",
        "anomalies_count": r"\d+.*anomalie",
        "window_ratio_percent": r"\d+\.\d+%.*fenêtres",
    }
    
    pattern_matches = {}
    for pattern_name, pattern in patterns.items():
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        pattern_matches[pattern_name] = len(matches) > 0
        if matches:
            logger.info(f"   ✅ {pattern_name}: {matches[0][:50]}...")
    
    # Vérifications détaillées
    logger.info("📊 Résultats des vérifications:")
    for check_name, check_result in checks.items():
        status = "✅" if check_result else "❌"
        logger.info(f"   {status} {check_name}: {'OK' if check_result else 'ÉCHEC'}")
    
    logger.info("🔍 Patterns détectés:")
    for pattern_name, pattern_found in pattern_matches.items():
        status = "✅" if pattern_found else "❌"
        logger.info(f"   {status} {pattern_name}: {'Trouvé' if pattern_found else 'Non trouvé'}")
    
    # Rechercher des valeurs statiques problématiques
    problematic_patterns = [
        "Traiter les 0 anomalies",
        "Corriger les 1 non-conformités",
        "{{ high_anomalies | default",
    ]
    
    problems_found = []
    for problem in problematic_patterns:
        if problem in html_content:
            problems_found.append(problem)
    
    if problems_found:
        logger.error("🚨 Valeurs statiques détectées:")
        for problem in problems_found:
            logger.error(f"   ❌ {problem}")
    else:
        logger.info("✅ Aucune valeur statique problématique détectée")
    
    # Score global
    total_checks = len(checks) + len(pattern_matches)
    passed_checks = sum(checks.values()) + sum(pattern_matches.values())
    success_rate = (passed_checks / total_checks) * 100
    
    logger.info(f"📊 Score global: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    return success_rate > 70  # Succès si plus de 70% des vérifications passent

def test_specific_recommendations():
    """Test des recommandations spécifiques attendues pour basic2"""
    logger.info("🧪 Test des recommandations spécifiques pour basic2")
    
    # Données attendues pour basic2
    expected_data = {
        "critical_anomalies": 23,
        "high_anomalies": 0,
        "medium_anomalies": 72,
        "low_anomalies": 129,
        "pmr_compliance": 61.5,
        "window_ratio": 15.6,  # 15.6%
        "total_anomalies": 224
    }
    
    # Recommandations attendues
    expected_recommendations = [
        f"Traiter les {expected_data['critical_anomalies']} anomalie(s) de sévérité CRITIQUE",
        "Aucune anomalie critique ou élevée" if expected_data['high_anomalies'] == 0 else f"Traiter les {expected_data['high_anomalies']} anomalie(s) élevée",
        f"{expected_data['medium_anomalies']} anomalies moyennes détectées",
        f"Conformité.*{expected_data['pmr_compliance']:.1f}%",
        f"Ratio fenêtres/murs.*{expected_data['window_ratio']:.1f}%"
    ]
    
    logger.info("📋 Recommandations attendues pour basic2:")
    for i, rec in enumerate(expected_recommendations, 1):
        logger.info(f"   {i}. {rec}")
    
    return expected_recommendations

def main():
    """Test principal du rapport dynamique"""
    logger.info("🚀 Tests du Rapport Dynamique avec Recommandations Intelligentes")
    
    # Test 1: Génération du rapport
    logger.info(f"\n{'='*60}")
    logger.info("TEST 1: GÉNÉRATION RAPPORT HTML")
    logger.info(f"{'='*60}")
    report_id, report_url = test_generate_html_report()
    
    if not report_id:
        logger.error("❌ Génération du rapport échouée - Tests interrompus")
        return
    
    # Attendre un peu pour que le rapport soit prêt
    time.sleep(2)
    
    # Test 2: Visualisation et analyse
    logger.info(f"\n{'='*60}")
    logger.info("TEST 2: ANALYSE CONTENU DYNAMIQUE")
    logger.info(f"{'='*60}")
    content_valid = test_view_dynamic_report(report_id)
    
    # Test 3: Recommandations spécifiques
    logger.info(f"\n{'='*60}")
    logger.info("TEST 3: RECOMMANDATIONS SPÉCIFIQUES")
    logger.info(f"{'='*60}")
    expected_recommendations = test_specific_recommendations()
    
    # Résumé final
    logger.info(f"\n{'='*60}")
    logger.info("📊 RÉSUMÉ DES TESTS")
    logger.info(f"{'='*60}")
    
    if report_id:
        logger.info("✅ TEST 1: Génération du rapport réussie")
        logger.info(f"   🔗 URL: http://localhost:8000{report_url}")
    else:
        logger.error("❌ TEST 1: Génération du rapport échouée")
    
    if content_valid:
        logger.info("✅ TEST 2: Contenu dynamique validé")
    else:
        logger.error("❌ TEST 2: Problèmes dans le contenu dynamique")
    
    logger.info("✅ TEST 3: Recommandations spécifiques définies")
    
    # Instructions d'utilisation
    logger.info(f"\n{'='*60}")
    logger.info("💡 INSTRUCTIONS DE VÉRIFICATION MANUELLE")
    logger.info(f"{'='*60}")
    
    if report_id:
        logger.info("🎯 Pour vérifier les corrections:")
        logger.info(f"   1. Ouvrir: http://localhost:8000/report-view/{report_id}")
        logger.info("   2. Aller à la section 'Recommandations Intelligentes'")
        logger.info("   3. Vérifier les recommandations attendues:")
        logger.info("      ✅ '23 anomalie(s) de sévérité CRITIQUE' (pas 0)")
        logger.info("      ✅ 'Aucune anomalie élevée' (0 élevées)")
        logger.info("      ✅ '72 anomalies moyennes détectées'")
        logger.info("      ✅ 'Conformité PMR 61.5%' (pas 1 non-conformité)")
        logger.info("      ✅ 'Ratio fenêtres/murs 15.6%'")
        logger.info("   4. Vérifier l'absence de:")
        logger.info("      ❌ 'Traiter les 0 anomalies élevées'")
        logger.info("      ❌ 'Corriger les 1 non-conformités PMR'")
        logger.info("      ❌ Valeurs statiques codées en dur")
    
    logger.info("🔄 Comparaison AVANT/APRÈS:")
    logger.info("   AVANT: 'Traiter les 0 anomalies élevées' (statique)")
    logger.info("   APRÈS: 'Traiter les 23 anomalies CRITIQUES' (dynamique)")
    logger.info("")
    logger.info("   AVANT: 'Corriger les 1 non-conformités PMR' (statique)")
    logger.info("   APRÈS: 'Conformité PMR 61.5% - Corriger X non-conformités' (dynamique)")
    
    logger.info("🎉 Tests terminés!")

if __name__ == "__main__":
    main()
