"""
Analyseur IFC Complet - Inspiré du PMRAnalyzer
Combine la détection d'anomalies, la classification de bâtiment et l'analyse PMR
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit
from datetime import datetime
import json

# Importer les analyseurs existants
from pmr_analyzer import PMRAnalyzer
from anomaly_detector import IFCAnomalyDetector
from building_classifier import BuildingClassifier
from ifc_analyzer import IFCAnalyzer

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types d'analyse disponibles"""
    ANOMALIES = "anomalies"
    PMR = "pmr"
    CLASSIFICATION = "classification"
    METRICS = "metrics"
    COMPREHENSIVE = "comprehensive"

@dataclass
class AnalysisResult:
    """Résultat d'une analyse complète"""
    analysis_type: AnalysisType
    file_path: str
    timestamp: str
    success: bool
    data: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

class ComprehensiveIFCAnalyzer:
    """
    Analyseur IFC complet qui combine tous les types d'analyses
    Suit le même principe que PMRAnalyzer mais pour une analyse globale
    """
    
    def __init__(self, ifc_file_path: str):
        """
        Initialise l'analyseur complet avec gestion d'erreurs robuste

        Args:
            ifc_file_path: Chemin vers le fichier IFC
        """
        self.ifc_file_path = ifc_file_path
        self.ifc_file = None
        self.results = {}
        self.errors = []
        self.warnings = []
        self.file_corrupted = False

        logger.info(f"Initialisation de l'analyseur IFC complet pour: {ifc_file_path}")

        # Essayer de charger le fichier IFC avec gestion d'erreurs
        try:
            self.ifc_file = ifcopenshell.open(ifc_file_path)
            logger.info(f"✅ Fichier IFC chargé avec succès")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Erreur lors du chargement du fichier IFC: {error_msg}")

            if "Type held at index" in error_msg and "class Blank" in error_msg:
                self.file_corrupted = True
                self.errors.append("Fichier IFC corrompu ou mal formé")
                logger.error("🔍 DIAGNOSTIC: Fichier IFC corrompu détecté")
            else:
                self.errors.append(f"Erreur de chargement IFC: {error_msg}")
                raise
    
    def analyze_comprehensive(self) -> Dict[str, Any]:
        """
        🚨 Détecter les anomalies 🏢 Classifier le bâtiment 📄 Générer un rapport ♿ Analyse PMR
        Analyse complète similaire au principe du PMRAnalyzer
        
        Returns:
            Dictionnaire avec tous les résultats d'analyse
        """
        try:
            logger.info("🚀 Début de l'analyse IFC complète")
            
            # Réinitialiser les résultats
            self.results = {}
            self.errors = []
            self.warnings = []
            
            # 1. 📊 ANALYSE DES MÉTRIQUES DE BASE (comme PMRAnalyzer._check_door_widths)
            metrics_result = self._analyze_basic_metrics()
            self.results['metrics'] = metrics_result
            
            # 2. 🚨 DÉTECTION D'ANOMALIES (comme PMRAnalyzer._check_corridor_widths)
            anomalies_result = self._detect_anomalies()
            self.results['anomalies'] = anomalies_result
            
            # 3. 🏢 CLASSIFICATION DU BÂTIMENT (comme PMRAnalyzer._check_elevator_presence)
            classification_result = self._classify_building()
            self.results['classification'] = classification_result
            
            # 4. ♿ ANALYSE PMR (comme PMRAnalyzer._check_ramp_slopes)
            pmr_result = self._analyze_pmr_compliance()
            self.results['pmr'] = pmr_result
            
            # 5. 📄 GÉNÉRATION DU RÉSUMÉ (comme PMRAnalyzer._generate_pmr_summary)
            summary = self._generate_comprehensive_summary()
            
            logger.info(f"✅ Analyse IFC complète terminée avec {len(self.results)} modules")
            
            # EXTRACTION DES SCORES DYNAMIQUES
            metrics_data = self.results.get('metrics', {}).get('data', {})
            building_metrics = metrics_data.get('building_metrics', {})
            structural_score = building_metrics.get('structural_score')
            mep_score = building_metrics.get('mep_score')
            spatial_score = building_metrics.get('spatial_score')
            quality_score = building_metrics.get('quality_score')
            
            return {
                "analysis_results": self.results,
                "summary": summary,
                "analysis_timestamp": datetime.now().isoformat(),
                "file_analyzed": self.ifc_file_path,
                "analyzer_version": "ComprehensiveIFCAnalyzer v1.0",
                "errors": self.errors,
                "warnings": self.warnings,
                "structural_score": structural_score,
                "mep_score": mep_score,
                "spatial_score": spatial_score,
                "quality_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse IFC complète: {e}")
            self.errors.append(str(e))
            raise
    
    def _analyze_basic_metrics(self) -> Dict[str, Any]:
        """📊 Analyse des métriques de base (inspiré de PMRAnalyzer._check_door_widths)"""
        try:
            logger.info("📊 Analyse des métriques de base...")
            
            # Utiliser l'IFCAnalyzer existant
            ifc_analyzer = IFCAnalyzer(self.ifc_file_path)
            analysis_data = ifc_analyzer.generate_full_analysis()
            
            return {
                "status": "success",
                "data": analysis_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Erreur analyse métriques: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_anomalies(self) -> Dict[str, Any]:
        """🚨 Détection d'anomalies (inspiré de PMRAnalyzer._check_corridor_widths)"""
        try:
            logger.info("🚨 Détection d'anomalies...")
            
            # Utiliser l'IFCAnomalyDetector existant
            if IFCAnomalyDetector:
                detector = IFCAnomalyDetector(self.ifc_file_path)
                anomalies_list = detector.detect_all_anomalies()

                # Convertir la liste d'anomalies en dictionnaire
                anomalies_data = {
                    "total_anomalies": len(anomalies_list),
                    "anomalies_by_severity": {},
                    "anomalies_by_type": {},
                    "anomalies_details": []
                }

                # Grouper par sévérité
                for anomaly in anomalies_list:
                    severity = anomaly.severity.value
                    if severity not in anomalies_data["anomalies_by_severity"]:
                        anomalies_data["anomalies_by_severity"][severity] = 0
                    anomalies_data["anomalies_by_severity"][severity] += 1

                    # Grouper par type d'élément
                    element_type = anomaly.element_type
                    if element_type not in anomalies_data["anomalies_by_type"]:
                        anomalies_data["anomalies_by_type"][element_type] = 0
                    anomalies_data["anomalies_by_type"][element_type] += 1

                    # Ajouter les détails
                    anomalies_data["anomalies_details"].append({
                        "id": anomaly.id,
                        "element_id": anomaly.element_id,
                        "element_type": anomaly.element_type,
                        "element_name": anomaly.element_name,
                        "anomaly_type": anomaly.anomaly_type,  # 🔧 CORRECTION: anomaly_type au lieu de category
                        "description": anomaly.description,
                        "severity": severity,
                        "suggested_fix": anomaly.suggested_fix,
                        "location": anomaly.location,
                        "additional_data": anomaly.additional_data
                    })
                
                return {
                    "status": "success",
                    "data": anomalies_data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                warning_msg = "IFCAnomalyDetector non disponible"
                logger.warning(warning_msg)
                self.warnings.append(warning_msg)
                return {
                    "status": "warning",
                    "message": warning_msg,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            error_msg = f"Erreur détection anomalies: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _classify_building(self) -> Dict[str, Any]:
        """🏢 Classification du bâtiment (inspiré de PMRAnalyzer._check_elevator_presence)"""
        try:
            logger.info("🏢 Classification du bâtiment...")
            
            # Utiliser le BuildingClassifier existant
            if BuildingClassifier:
                classifier = BuildingClassifier()
                
                # 🔧 CORRECTION: classify_building attend un chemin de fichier, pas des données
                classification_data = classifier.classify_building(self.ifc_file_path)
                
                return {
                    "status": "success",
                    "data": classification_data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                warning_msg = "BuildingClassifier non disponible"
                logger.warning(warning_msg)
                self.warnings.append(warning_msg)
                return {
                    "status": "warning",
                    "message": warning_msg,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            error_msg = f"Erreur classification: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_pmr_compliance(self) -> Dict[str, Any]:
        """♿ Analyse PMR (inspiré de PMRAnalyzer._check_ramp_slopes)"""
        try:
            logger.info("♿ Analyse PMR...")
            
            # Utiliser le PMRAnalyzer existant
            pmr_analyzer = PMRAnalyzer(self.ifc_file_path)
            pmr_data = pmr_analyzer.analyze_pmr_compliance()
            
            return {
                "status": "success",
                "data": pmr_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Erreur analyse PMR: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_comprehensive_summary(self) -> Dict[str, Any]:
        """📄 Génération du résumé complet (inspiré de PMRAnalyzer._generate_pmr_summary)"""
        try:
            logger.info("📄 Génération du résumé complet...")
            
            # Compter les succès et erreurs
            successful_analyses = len([r for r in self.results.values() if r.get('status') == 'success'])
            failed_analyses = len([r for r in self.results.values() if r.get('status') == 'error'])
            warning_analyses = len([r for r in self.results.values() if r.get('status') == 'warning'])
            
            # Score global de qualité
            total_analyses = len(self.results)
            quality_score = (successful_analyses / total_analyses * 100) if total_analyses > 0 else 0
            
            # Déterminer le statut global
            if failed_analyses == 0:
                if warning_analyses == 0:
                    global_status = "EXCELLENT"
                else:
                    global_status = "BON_AVEC_RESERVES"
            else:
                global_status = "PROBLEMES_DETECTES"
            
            # Recommandations principales
            recommendations = self._generate_main_recommendations()
            
            return {
                "total_analyses": total_analyses,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "warning_analyses": warning_analyses,
                "quality_score": round(quality_score, 1),
                "global_status": global_status,
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "main_recommendations": recommendations,
                "analysis_completeness": f"{successful_analyses}/{total_analyses} modules analysés avec succès"
            }
            
        except Exception as e:
            error_msg = f"Erreur génération résumé: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return {
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_main_recommendations(self) -> List[str]:
        """Génère les recommandations principales basées sur les résultats"""
        recommendations = []
        
        # Recommandations basées sur les erreurs
        if self.errors:
            recommendations.append(f"Corriger {len(self.errors)} erreur(s) d'analyse détectée(s)")
        
        # Recommandations basées sur les anomalies
        if 'anomalies' in self.results and self.results['anomalies'].get('status') == 'success':
            anomaly_data = self.results['anomalies'].get('data', {})
            if isinstance(anomaly_data, dict) and 'total_anomalies' in anomaly_data:
                total_anomalies = anomaly_data['total_anomalies']
                if total_anomalies > 0:
                    recommendations.append(f"Traiter {total_anomalies} anomalie(s) détectée(s)")
        
        # Recommandations basées sur PMR
        if 'pmr' in self.results and self.results['pmr'].get('status') == 'success':
            pmr_data = self.results['pmr'].get('data', {})
            if isinstance(pmr_data, dict) and 'summary' in pmr_data:
                pmr_summary = pmr_data['summary']
                if pmr_summary.get('priority_issues_count', 0) > 0:
                    recommendations.append(f"Corriger {pmr_summary['priority_issues_count']} non-conformité(s) PMR prioritaire(s)")
        
        # Recommandation par défaut
        if not recommendations:
            recommendations.append("Le modèle BIM présente une bonne qualité globale")
        
        return recommendations
    
    def export_analysis_report(self) -> Dict[str, Any]:
        """Exporte un rapport d'analyse formaté (similaire à PMRAnalyzer.export_pmr_report)"""
        if not self.results:
            return {"error": "Aucune analyse effectuée"}
        
        return {
            "comprehensive_analysis": self.results,
            "summary": self._generate_comprehensive_summary(),
            "export_timestamp": datetime.now().isoformat(),
            "file_analyzed": self.ifc_file_path
        }
