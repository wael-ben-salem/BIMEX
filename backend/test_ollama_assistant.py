"""
Test de l'assistant Ollama optimisé pour des réponses rapides
"""

import requests
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama_availability():
    """Test de disponibilité d'Ollama"""
    logger.info("🧪 Test de disponibilité d'Ollama")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            logger.info(f"✅ Ollama disponible avec {len(models)} modèle(s): {model_names}")
            return True, model_names
        else:
            logger.error(f"❌ Ollama répond avec status {response.status_code}")
            return False, []
    except Exception as e:
        logger.error(f"❌ Ollama non accessible: {e}")
        return False, []

def test_assistant_loading():
    """Test du chargement de l'assistant"""
    logger.info("🧪 Test du chargement de l'assistant")
    
    try:
        response = requests.get(
            "http://localhost:8000/assistant/load-project/basic2?session_id=test_session",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Assistant chargé: {data.get('status')}")
            
            if data.get('status') == 'success':
                summary = data.get('model_summary', {})
                logger.info(f"📊 Projet: {summary.get('project_name')}")
                logger.info(f"📐 Éléments: {summary.get('total_elements')}")
                logger.info(f"🏢 Étages: {summary.get('total_storeys')}")
                logger.info(f"🚨 Anomalies: {summary.get('total_anomalies')}")
                return True
            else:
                logger.error(f"❌ Erreur chargement: {data.get('message')}")
                return False
        else:
            logger.error(f"❌ Status HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur test chargement: {e}")
        return False

def test_quick_responses():
    """Test des réponses rapides"""
    logger.info("🧪 Test des réponses rapides")
    
    quick_questions = [
        "Quelle est la surface totale ?",
        "Combien d'étages ?",
        "Nombre d'espaces ?",
        "Y a-t-il des anomalies ?",
        "Combien de fenêtres ?",
        "Résumé du bâtiment"
    ]
    
    results = {}
    
    for question in quick_questions:
        try:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/assistant/ask",
                json={
                    "question": question,
                    "session_id": "test_session"
                },
                timeout=15
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                model_used = data.get('model_used', '')
                
                logger.info(f"✅ Q: {question}")
                logger.info(f"   R: {answer[:100]}...")
                logger.info(f"   ⏱️ Temps: {response_time:.2f}s ({model_used})")
                
                results[question] = {
                    "success": True,
                    "response_time": response_time,
                    "answer_length": len(answer),
                    "model_used": model_used
                }
            else:
                logger.error(f"❌ Q: {question} - Status {response.status_code}")
                results[question] = {"success": False, "response_time": response_time}
                
        except Exception as e:
            logger.error(f"❌ Q: {question} - Erreur: {e}")
            results[question] = {"success": False, "error": str(e)}
    
    return results

def test_cache_performance():
    """Test des performances du cache"""
    logger.info("🧪 Test des performances du cache")
    
    test_question = "Quelle est la surface totale ?"
    
    # Premier appel (sans cache)
    start_time = time.time()
    response1 = requests.post(
        "http://localhost:8000/assistant/ask",
        json={"question": test_question, "session_id": "test_session"},
        timeout=15
    )
    first_time = time.time() - start_time
    
    # Deuxième appel (avec cache)
    start_time = time.time()
    response2 = requests.post(
        "http://localhost:8000/assistant/ask",
        json={"question": test_question, "session_id": "test_session"},
        timeout=15
    )
    second_time = time.time() - start_time
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        logger.info(f"⏱️ Premier appel: {first_time:.2f}s")
        logger.info(f"⚡ Deuxième appel (cache): {second_time:.2f}s")
        logger.info(f"🚀 Amélioration: {(first_time/second_time):.1f}x plus rapide")
        
        return {
            "first_time": first_time,
            "second_time": second_time,
            "improvement": first_time / second_time if second_time > 0 else 0
        }
    
    return None

def test_conversation_history():
    """Test de l'historique de conversation"""
    logger.info("🧪 Test de l'historique de conversation")
    
    try:
        response = requests.get(
            "http://localhost:8000/assistant/history/test_session",
            timeout=10
        )
        
        if response.status_code == 200:
            history = response.json()
            logger.info(f"📚 Historique: {len(history)} entrée(s)")
            
            for i, entry in enumerate(history[-3:]):  # Dernières 3 entrées
                logger.info(f"   {i+1}. Q: {entry.get('question', '')[:50]}...")
                logger.info(f"      R: {entry.get('answer', '')[:50]}...")
                logger.info(f"      ⏱️: {entry.get('response_time', 'N/A')}")
            
            return len(history)
        else:
            logger.error(f"❌ Erreur historique: Status {response.status_code}")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Erreur test historique: {e}")
        return 0

def main():
    """Test principal de l'assistant Ollama optimisé"""
    logger.info("🚀 Tests de l'Assistant Ollama Optimisé")
    
    # Test 1: Disponibilité Ollama
    logger.info(f"\n{'='*50}")
    logger.info("TEST 1: DISPONIBILITÉ OLLAMA")
    logger.info(f"{'='*50}")
    ollama_available, models = test_ollama_availability()
    
    if not ollama_available:
        logger.error("❌ Ollama non disponible - Tests interrompus")
        logger.info("💡 Démarrez Ollama: ollama serve")
        return
    
    # Test 2: Chargement assistant
    logger.info(f"\n{'='*50}")
    logger.info("TEST 2: CHARGEMENT ASSISTANT")
    logger.info(f"{'='*50}")
    assistant_loaded = test_assistant_loading()
    
    if not assistant_loaded:
        logger.error("❌ Assistant non chargé - Tests interrompus")
        return
    
    # Test 3: Réponses rapides
    logger.info(f"\n{'='*50}")
    logger.info("TEST 3: RÉPONSES RAPIDES")
    logger.info(f"{'='*50}")
    quick_results = test_quick_responses()
    
    # Test 4: Performance cache
    logger.info(f"\n{'='*50}")
    logger.info("TEST 4: PERFORMANCE CACHE")
    logger.info(f"{'='*50}")
    cache_results = test_cache_performance()
    
    # Test 5: Historique
    logger.info(f"\n{'='*50}")
    logger.info("TEST 5: HISTORIQUE CONVERSATION")
    logger.info(f"{'='*50}")
    history_count = test_conversation_history()
    
    # Résumé final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RÉSUMÉ DES PERFORMANCES")
    logger.info(f"{'='*50}")
    
    if quick_results:
        success_count = sum(1 for r in quick_results.values() if r.get('success'))
        avg_time = sum(r.get('response_time', 0) for r in quick_results.values() if r.get('success')) / max(success_count, 1)
        
        logger.info(f"✅ Questions réussies: {success_count}/{len(quick_results)}")
        logger.info(f"⏱️ Temps moyen: {avg_time:.2f}s")
        
        # Analyser les types de réponses
        cache_responses = sum(1 for r in quick_results.values() if 'cache' in r.get('model_used', ''))
        quick_responses = sum(1 for r in quick_results.values() if 'rapide' in r.get('model_used', ''))
        
        logger.info(f"⚡ Réponses cache: {cache_responses}")
        logger.info(f"🚀 Réponses rapides: {quick_responses}")
    
    if cache_results:
        logger.info(f"🚀 Amélioration cache: {cache_results['improvement']:.1f}x plus rapide")
    
    logger.info(f"📚 Entrées historique: {history_count}")
    
    # Recommandations
    logger.info(f"\n{'='*50}")
    logger.info("💡 RECOMMANDATIONS")
    logger.info(f"{'='*50}")
    
    if ollama_available:
        logger.info("✅ Ollama fonctionne correctement")
        if models:
            logger.info(f"🤖 Modèles disponibles: {', '.join(models[:3])}")
    
    if assistant_loaded:
        logger.info("✅ Assistant BIM Ollama opérationnel")
    
    if quick_results and success_count > 0:
        if avg_time < 2.0:
            logger.info("🚀 Performances excellentes (< 2s)")
        elif avg_time < 5.0:
            logger.info("⚡ Performances bonnes (< 5s)")
        else:
            logger.info("⏳ Performances à améliorer (> 5s)")
            logger.info("💡 Suggestions: Modèle plus petit, plus de RAM, SSD")
    
    logger.info("🎉 Tests terminés!")

if __name__ == "__main__":
    main()
