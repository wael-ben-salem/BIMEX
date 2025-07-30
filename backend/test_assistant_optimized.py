"""
Test de l'assistant IA optimisé pour des réponses rapides et intelligentes
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_assistant_loading():
    """Test du chargement de l'assistant"""
    logger.info("🧪 Test du chargement de l'assistant")
    
    try:
        session_id = f"test_session_{int(time.time())}"
        
        start_time = time.time()
        response = requests.get(
            f"http://localhost:8000/assistant/load-project/basic2?session_id={session_id}",
            timeout=30
        )
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Assistant chargé en {load_time:.2f}s")
            logger.info(f"   Status: {data.get('status')}")
            
            if 'model_summary' in data:
                summary = data['model_summary']
                logger.info(f"   📊 Projet: {summary.get('project_name')}")
                logger.info(f"   📐 Éléments: {summary.get('total_elements')}")
                logger.info(f"   🏢 Étages: {summary.get('key_metrics', {}).get('total_storeys')}")
                logger.info(f"   🚨 Anomalies: {summary.get('key_metrics', {}).get('total_anomalies')}")
            
            return session_id, True
        else:
            logger.error(f"❌ Erreur chargement: {response.status_code}")
            return None, False
            
    except Exception as e:
        logger.error(f"❌ Erreur test chargement: {e}")
        return None, False

def test_quick_responses(session_id):
    """Test des réponses rapides optimisées"""
    logger.info("🧪 Test des réponses rapides optimisées")
    
    # Questions qui devraient avoir des réponses pré-calculées RAPIDES
    quick_questions = [
        "Quelle est la surface totale habitable de ce bâtiment ?",
        "Combien d'étages compte ce bâtiment ?",
        "Quel est le ratio fenêtres/murs ?",
        "Quelles améliorations recommandes-tu pour ce modèle ?",
        "Peux-tu analyser la performance énergétique potentielle ?",
        "Y a-t-il des anomalies dans ce modèle ?",
        "Quelle est la qualité de ce modèle BIM ?"
    ]
    
    results = {}
    
    for question in quick_questions:
        try:
            logger.info(f"❓ Question: {question}")
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/assistant/ask",
                json={
                    "question": question,
                    "session_id": session_id
                },
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                model_used = data.get('model_used', '')
                
                # Vérifier si c'est une réponse rapide (cache ou pré-calculée)
                is_fast = 'cache' in model_used or 'rapide' in model_used or response_time < 1.0
                speed_indicator = "⚡" if is_fast else "🤖"
                
                logger.info(f"   {speed_indicator} Réponse ({response_time:.2f}s): {answer[:100]}...")
                logger.info(f"   📊 Modèle: {model_used}")
                
                results[question] = {
                    "success": True,
                    "response_time": response_time,
                    "answer": answer,
                    "model_used": model_used,
                    "is_fast": is_fast
                }
            else:
                logger.error(f"   ❌ Erreur HTTP: {response.status_code}")
                results[question] = {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"   ❌ Erreur: {e}")
            results[question] = {"success": False, "error": str(e)}
    
    return results

def test_complex_questions(session_id):
    """Test des questions complexes qui nécessitent l'IA"""
    logger.info("🧪 Test des questions complexes")
    
    complex_questions = [
        "Compare les performances de ce bâtiment avec les standards",
        "Explique-moi les problèmes d'accessibilité détectés",
        "Quels sont les risques énergétiques de ce bâtiment ?",
        "Comment améliorer la conformité PMR de ce modèle ?"
    ]
    
    results = {}
    
    for question in complex_questions:
        try:
            logger.info(f"❓ Question complexe: {question}")
            
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/assistant/ask",
                json={
                    "question": question,
                    "session_id": session_id
                },
                timeout=20
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                model_used = data.get('model_used', '')
                
                logger.info(f"   🤖 Réponse IA ({response_time:.2f}s): {answer[:150]}...")
                logger.info(f"   📊 Modèle: {model_used}")
                
                results[question] = {
                    "success": True,
                    "response_time": response_time,
                    "answer": answer,
                    "model_used": model_used
                }
            else:
                logger.error(f"   ❌ Erreur HTTP: {response.status_code}")
                results[question] = {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"   ❌ Erreur: {e}")
            results[question] = {"success": False, "error": str(e)}
    
    return results

def analyze_performance(quick_results, complex_results):
    """Analyse des performances de l'assistant"""
    logger.info("📊 Analyse des performances")
    
    # Analyser les réponses rapides
    quick_successful = [r for r in quick_results.values() if r.get('success')]
    if quick_successful:
        avg_quick_time = sum(r['response_time'] for r in quick_successful) / len(quick_successful)
        fast_responses = sum(1 for r in quick_successful if r.get('is_fast'))
        
        logger.info(f"⚡ Réponses rapides:")
        logger.info(f"   ✅ Succès: {len(quick_successful)}/{len(quick_results)}")
        logger.info(f"   ⏱️ Temps moyen: {avg_quick_time:.2f}s")
        logger.info(f"   🚀 Réponses instantanées: {fast_responses}/{len(quick_successful)}")
    
    # Analyser les réponses complexes
    complex_successful = [r for r in complex_results.values() if r.get('success')]
    if complex_successful:
        avg_complex_time = sum(r['response_time'] for r in complex_successful) / len(complex_successful)
        
        logger.info(f"🤖 Réponses complexes:")
        logger.info(f"   ✅ Succès: {len(complex_successful)}/{len(complex_results)}")
        logger.info(f"   ⏱️ Temps moyen: {avg_complex_time:.2f}s")
    
    # Recommandations
    logger.info("💡 Recommandations:")
    if quick_successful and avg_quick_time < 2.0:
        logger.info("   ✅ Réponses rapides excellentes (< 2s)")
    elif quick_successful and avg_quick_time < 5.0:
        logger.info("   ⚡ Réponses rapides bonnes (< 5s)")
    else:
        logger.info("   ⏳ Réponses rapides à optimiser")
    
    if complex_successful and avg_complex_time < 10.0:
        logger.info("   ✅ Réponses complexes acceptables (< 10s)")
    elif complex_successful:
        logger.info("   ⏳ Réponses complexes lentes - Vérifier Ollama")

def main():
    """Test principal de l'assistant optimisé"""
    logger.info("🚀 Tests de l'Assistant IA Optimisé")
    
    # Test 1: Chargement de l'assistant
    logger.info(f"\n{'='*60}")
    logger.info("TEST 1: CHARGEMENT ASSISTANT")
    logger.info(f"{'='*60}")
    session_id, loaded = test_assistant_loading()
    
    if not loaded:
        logger.error("❌ Assistant non chargé - Tests interrompus")
        return
    
    # Test 2: Réponses rapides
    logger.info(f"\n{'='*60}")
    logger.info("TEST 2: RÉPONSES RAPIDES OPTIMISÉES")
    logger.info(f"{'='*60}")
    quick_results = test_quick_responses(session_id)
    
    # Test 3: Questions complexes
    logger.info(f"\n{'='*60}")
    logger.info("TEST 3: QUESTIONS COMPLEXES")
    logger.info(f"{'='*60}")
    complex_results = test_complex_questions(session_id)
    
    # Analyse finale
    logger.info(f"\n{'='*60}")
    logger.info("📊 ANALYSE DES PERFORMANCES")
    logger.info(f"{'='*60}")
    analyze_performance(quick_results, complex_results)
    
    # Instructions d'utilisation
    logger.info(f"\n{'='*60}")
    logger.info("💡 INSTRUCTIONS D'UTILISATION")
    logger.info(f"{'='*60}")
    
    logger.info("🎯 Pour tester l'assistant optimisé:")
    logger.info("   1. Ouvrir: http://localhost:8000/analysis?project=basic2&auto=true&file_detected=true&step=detailed")
    logger.info("   2. Cliquer '🤖 Charger l'assistant IA'")
    logger.info("   3. Tester les questions rapides:")
    logger.info("      - 'Quelle est la surface totale ?'")
    logger.info("      - 'Quelles améliorations recommandes-tu ?'")
    logger.info("      - 'Quel est le ratio fenêtres/murs ?'")
    logger.info("   4. Tester les questions complexes:")
    logger.info("      - 'Analyse la performance énergétique'")
    logger.info("      - 'Comment améliorer la conformité PMR ?'")
    
    logger.info("⚡ Réponses attendues:")
    logger.info("   - Questions simples: < 2s (pré-calculées)")
    logger.info("   - Questions complexes: < 8s (Ollama optimisé)")
    logger.info("   - Cache: < 0.1s (instantané)")
    
    logger.info("🎉 Tests terminés!")

if __name__ == "__main__":
    main()
