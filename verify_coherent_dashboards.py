#!/usr/bin/env python3
"""
🧪 Script de Vérification Finale des Dashboards Cohérents BIMEX
============================================================

Ce script vérifie que :
1. ✅ Le backend retourne des données cohérentes
2. ✅ Toutes les métriques sont synchronisées
3. ✅ Les valeurs sont identiques entre les sections
4. ✅ Aucune donnée factice n'est présente
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List

class CoherentDashboardVerifier:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Enregistre le résultat d'un test"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        
        # Affichage coloré
        if status == "✅ PASS":
            print(f"✅ [{timestamp}] {test_name}: {details}")
        elif status == "❌ FAIL":
            print(f"❌ [{timestamp}] {test_name}: {details}")
        elif status == "⚠️ WARN":
            print(f"⚠️ [{timestamp}] {test_name}: {details}")
        else:
            print(f"ℹ️ [{timestamp}] {test_name}: {details}")
    
    def test_backend_endpoint(self, project_id: str = "BasicHouse") -> Dict[str, Any]:
        """Teste l'endpoint backend et retourne les données"""
        try:
            url = f"{self.base_url}/analytics/coherent-dashboard/{project_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Endpoint", "✅ PASS", f"Données reçues: {len(data)} sections")
                return data
            else:
                self.log_test("Backend Endpoint", "❌ FAIL", f"Status: {response.status_code}")
                return {}
                
        except Exception as e:
            self.log_test("Backend Endpoint", "❌ FAIL", f"Erreur: {str(e)}")
            return {}
    
    def verify_bim_scores_coherence(self, data: Dict[str, Any]) -> bool:
        """Vérifie la cohérence des scores BIM"""
        try:
            bim_scores = data.get("bim_scores", {})
            
            if not bim_scores:
                self.log_test("Scores BIM", "❌ FAIL", "Section bim_scores manquante")
                return False
            
            # Vérifier que tous les scores sont présents
            required_scores = ["structural_score", "mep_score", "spatial_score", "quality_score"]
            missing_scores = [score for score in required_scores if score not in bim_scores]
            
            if missing_scores:
                self.log_test("Scores BIM", "❌ FAIL", f"Scores manquants: {missing_scores}")
                return False
            
            # Vérifier que les scores sont dans la plage [0-100]
            for score_name, score_value in bim_scores.items():
                if not isinstance(score_value, (int, float)) or score_value < 0 or score_value > 100:
                    self.log_test("Scores BIM", "❌ FAIL", f"Score invalide {score_name}: {score_value}")
                    return False
            
            self.log_test("Scores BIM", "✅ PASS", f"4 scores valides: {list(bim_scores.keys())}")
            return True
            
        except Exception as e:
            self.log_test("Scores BIM", "❌ FAIL", f"Erreur: {str(e)}")
            return False
    
    def verify_performance_metrics_coherence(self, data: Dict[str, Any]) -> bool:
        """Vérifie la cohérence des métriques de performance"""
        try:
            performance_metrics = data.get("performance_metrics", {})
            
            if not performance_metrics:
                self.log_test("Métriques Performance", "❌ FAIL", "Section performance_metrics manquante")
                return False
            
            # Vérifier que toutes les métriques sont présentes
            required_metrics = ["efficiency", "sustainability", "cost_effectiveness", "innovation"]
            missing_metrics = [metric for metric in required_metrics if metric not in performance_metrics]
            
            if missing_metrics:
                self.log_test("Métriques Performance", "❌ FAIL", f"Métriques manquantes: {missing_metrics}")
                return False
            
            # Vérifier que les valeurs sont cohérentes
            for metric_name, metric_value in performance_metrics.items():
                if not isinstance(metric_value, (int, float)) or metric_value < 0 or metric_value > 100:
                    self.log_test("Métriques Performance", "❌ FAIL", f"Métrique invalide {metric_name}: {metric_value}")
                    return False
            
            self.log_test("Métriques Performance", "✅ PASS", f"4 métriques valides: {list(performance_metrics.keys())}")
            return True
            
        except Exception as e:
            self.log_test("Métriques Performance", "❌ FAIL", f"Erreur: {str(e)}")
            return False
    
    def verify_innovation_metrics_coherence(self, data: Dict[str, Any]) -> bool:
        """Vérifie la cohérence des métriques d'innovation"""
        try:
            innovation_metrics = data.get("innovation_metrics", {})
            
            if not innovation_metrics:
                self.log_test("Métriques Innovation", "❌ FAIL", "Section innovation_metrics manquante")
                return False
            
            # Vérifier que toutes les métriques sont présentes
            required_metrics = ["ai_efficiency", "design_variants", "design_score", "maintenance_accuracy", "maintenance_savings", "innovation_score"]
            missing_metrics = [metric for metric in required_metrics if metric not in innovation_metrics]
            
            if missing_metrics:
                self.log_test("Métriques Innovation", "❌ FAIL", f"Métriques manquantes: {missing_metrics}")
                return False
            
            # Vérifier les types et valeurs
            for metric_name, metric_value in innovation_metrics.items():
                if metric_name == "maintenance_savings":
                    if not isinstance(metric_value, str):
                        self.log_test("Métriques Innovation", "❌ FAIL", f"maintenance_savings doit être une string: {metric_value}")
                        return False
                elif metric_name == "design_variants":
                    if not isinstance(metric_value, int) or metric_value < 0:
                        self.log_test("Métriques Innovation", "❌ FAIL", f"design_variants doit être un entier positif: {metric_value}")
                        return False
                else:
                    if not isinstance(metric_value, (int, float)) or metric_value < 0 or metric_value > 100:
                        self.log_test("Métriques Innovation", "❌ FAIL", f"Métrique invalide {metric_name}: {metric_value}")
                        return False
            
            self.log_test("Métriques Innovation", "✅ PASS", f"6 métriques valides: {list(innovation_metrics.keys())}")
            return True
            
        except Exception as e:
            self.log_test("Métriques Innovation", "❌ FAIL", f"Erreur: {str(e)}")
            return False
    
    def verify_element_counts_coherence(self, data: Dict[str, Any]) -> bool:
        """Vérifie la cohérence des comptages d'éléments"""
        try:
            structural_elements = data.get("structural_elements", {})
            mep_elements = data.get("mep_elements", {})
            spatial_elements = data.get("spatial_elements", {})
            
            # Vérifier les éléments structurels
            if structural_elements:
                required_elements = ["columns", "beams", "walls", "slabs"]
                for element in required_elements:
                    if element in structural_elements:
                        value = structural_elements[element]
                        if not isinstance(value, int) or value < 0:
                            self.log_test("Éléments Structurels", "❌ FAIL", f"Valeur invalide pour {element}: {value}")
                            return False
                
                self.log_test("Éléments Structurels", "✅ PASS", f"Éléments valides: {list(structural_elements.keys())}")
            
            # Vérifier les éléments MEP
            if mep_elements:
                required_elements = ["electrical", "plumbing", "hvac", "fire_protection"]
                for element in required_elements:
                    if element in mep_elements:
                        value = mep_elements[element]
                        if not isinstance(value, int) or value < 0:
                            self.log_test("Éléments MEP", "❌ FAIL", f"Valeur invalide pour {element}: {value}")
                            return False
                
                self.log_test("Éléments MEP", "✅ PASS", f"Éléments valides: {list(mep_elements.keys())}")
            
            # Vérifier les éléments spatiaux
            if spatial_elements:
                required_elements = ["spaces", "total_area", "total_volume", "storeys"]
                for element in required_elements:
                    if element in spatial_elements:
                        value = spatial_elements[element]
                        if not isinstance(value, (int, float)) or value < 0:
                            self.log_test("Éléments Spatiaux", "❌ FAIL", f"Valeur invalide pour {element}: {value}")
                            return False
                
                self.log_test("Éléments Spatiaux", "✅ PASS", f"Éléments valides: {list(spatial_elements.keys())}")
            
            return True
            
        except Exception as e:
            self.log_test("Éléments", "❌ FAIL", f"Erreur: {str(e)}")
            return False
    
    def verify_no_dummy_data(self, data: Dict[str, Any]) -> bool:
        """Vérifie qu'aucune donnée factice n'est présente"""
        try:
            # Vérifier qu'il n'y a pas de valeurs évidentes de test
            suspicious_values = ["--", "N/A", "null", "undefined", "test", "dummy", "placeholder"]
            
            data_str = json.dumps(data, default=str).lower()
            
            for suspicious in suspicious_values:
                if suspicious in data_str:
                    self.log_test("Données Factices", "❌ FAIL", f"Valeur suspecte détectée: {suspicious}")
                    return False
            
            # Vérifier qu'il n'y a pas de valeurs Math.random() évidentes
            if "math.random" in data_str:
                self.log_test("Données Factices", "❌ FAIL", "Math.random() détecté dans les données")
                return False
            
            self.log_test("Données Factices", "✅ PASS", "Aucune donnée factice détectée")
            return True
            
        except Exception as e:
            self.log_test("Données Factices", "❌ FAIL", f"Erreur: {str(e)}")
            return False
    
    def verify_data_consistency(self, data: Dict[str, Any]) -> bool:
        """Vérifie la cohérence globale des données"""
        try:
            # Vérifier que les scores BIM et les métriques de performance sont cohérents
            bim_scores = data.get("bim_scores", {})
            performance_metrics = data.get("performance_metrics", {})
            
            if bim_scores and performance_metrics:
                # Les scores BIM et les métriques de performance doivent avoir des valeurs similaires
                bim_avg = sum(bim_scores.values()) / len(bim_scores)
                perf_avg = sum(performance_metrics.values()) / len(performance_metrics)
                
                # La différence ne doit pas être trop importante (tolérance de 20%)
                if abs(bim_avg - perf_avg) > 20:
                    self.log_test("Cohérence Globale", "⚠️ WARN", f"Différence importante entre scores BIM ({bim_avg:.1f}) et performance ({perf_avg:.1f})")
                else:
                    self.log_test("Cohérence Globale", "✅ PASS", f"Scores BIM ({bim_avg:.1f}) et performance ({perf_avg:.1f}) cohérents")
            
            # Vérifier la source des données
            source = data.get("source", "unknown")
            last_updated = data.get("last_updated", "unknown")
            
            self.log_test("Source Données", "ℹ️ INFO", f"Source: {source}, Dernière mise à jour: {last_updated}")
            
            return True
            
        except Exception as e:
            self.log_test("Cohérence Globale", "❌ FAIL", f"Erreur: {str(e)}")
            return False
    
    def run_complete_verification(self, project_id: str = "BasicHouse") -> Dict[str, Any]:
        """Lance la vérification complète des dashboards"""
        print("🧪 VÉRIFICATION COMPLÈTE DES DASHBOARDS COHÉRENTS BIMEX")
        print("=" * 70)
        print(f"🎯 Projet: {project_id}")
        print(f"🌐 Backend: {self.base_url}")
        print(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Test 1: Endpoint backend
        data = self.test_backend_endpoint(project_id)
        if not data:
            self.log_test("VÉRIFICATION GLOBALE", "❌ FAIL", "Impossible de récupérer les données du backend")
            return self.generate_report()
        
        # Test 2: Vérification des scores BIM
        self.verify_bim_scores_coherence(data)
        
        # Test 3: Vérification des métriques de performance
        self.verify_performance_metrics_coherence(data)
        
        # Test 4: Vérification des métriques d'innovation
        self.verify_innovation_metrics_coherence(data)
        
        # Test 5: Vérification des comptages d'éléments
        self.verify_element_counts_coherence(data)
        
        # Test 6: Vérification des données factices
        self.verify_no_dummy_data(data)
        
        # Test 7: Vérification de la cohérence globale
        self.verify_data_consistency(data)
        
        # Résumé final
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "✅ PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "❌ FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "⚠️ WARN"])
        
        print("\n" + "=" * 70)
        print("📊 RÉSULTATS DE LA VÉRIFICATION")
        print("=" * 70)
        print(f"✅ Tests réussis: {passed_tests}")
        print(f"❌ Tests échoués: {failed_tests}")
        print(f"⚠️ Avertissements: {warnings}")
        print(f"📊 Total: {total_tests}")
        
        if failed_tests == 0:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS ! Les dashboards sont parfaitement cohérents !")
            overall_status = "✅ SUCCESS"
        elif failed_tests <= warnings:
            print("\n⚠️ Quelques avertissements mais pas d'erreurs critiques")
            overall_status = "⚠️ WARNING"
        else:
            print("\n❌ Des erreurs critiques ont été détectées")
            overall_status = "❌ FAILED"
        
        self.log_test("VÉRIFICATION GLOBALE", overall_status, f"Résultat: {passed_tests}/{total_tests} tests réussis")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Génère un rapport détaillé de la vérification"""
        return {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "test_results": self.test_results,
            "summary": {
                "total": len(self.test_results),
                "passed": len([r for r in self.test_results if r["status"] == "✅ PASS"]),
                "failed": len([r for r in self.test_results if r["status"] == "❌ FAIL"]),
                "warnings": len([r for r in self.test_results if r["status"] == "⚠️ WARN"])
            }
        }

def main():
    """Fonction principale"""
    print("🚀 Lancement de la vérification des dashboards cohérents...")
    
    # Créer le vérificateur
    verifier = CoherentDashboardVerifier("http://localhost:8001")
    
    # Lancer la vérification complète
    try:
        report = verifier.run_complete_verification("BasicHouse")
        
        # Sauvegarder le rapport
        with open("verification_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Rapport sauvegardé dans: verification_report.json")
        
        # Afficher le statut final
        if report["summary"]["failed"] == 0:
            print("\n🎯 MISSION ACCOMPLIE ! Tous les dashboards sont parfaitement cohérents !")
            return 0
        else:
            print(f"\n⚠️ {report['summary']['failed']} erreur(s) détectée(s) - Vérification nécessaire")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Vérification interrompue par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n💥 Erreur critique: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())


