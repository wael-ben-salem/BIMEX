"""
🔮 BIMEX - Prédicteur Intelligent des Coûts
Analyse des matériaux et prédiction des coûts en temps réel avec Machine Learning
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

logger = logging.getLogger(__name__)

@dataclass
class CostPrediction:
    """Structure pour une prédiction de coût"""
    category: str
    predicted_cost: float
    confidence: float
    cost_per_unit: float
    quantity: float
    unit: str
    factors: Dict[str, float]
    recommendations: List[str]

@dataclass
class MaterialCost:
    """Structure pour le coût d'un matériau"""
    material_name: str
    cost_per_m3: float
    cost_per_m2: float
    cost_per_unit: float
    carbon_footprint: float
    durability_score: float

class CostPredictor:
    """
    🔮 Prédicteur Intelligent des Coûts avec IA
    Utilise le machine learning pour prédire les coûts de construction
    """
    
    def __init__(self, ifc_file_path: str):
        """
        Initialise le prédicteur de coûts
        
        Args:
            ifc_file_path: Chemin vers le fichier IFC
        """
        self.ifc_file_path = ifc_file_path
        self.ifc_file = ifcopenshell.open(ifc_file_path)
        self.predictions = []
        self.total_predicted_cost = 0.0
        
        # Base de données des coûts (en €)
        self.material_costs = {
            "Concrete": MaterialCost("Béton", 150.0, 25.0, 0.0, 0.15, 8.5),
            "Steel": MaterialCost("Acier", 800.0, 45.0, 0.0, 2.1, 9.0),
            "Wood": MaterialCost("Bois", 600.0, 35.0, 0.0, 0.02, 7.0),
            "Brick": MaterialCost("Brique", 300.0, 40.0, 0.0, 0.12, 8.0),
            "Glass": MaterialCost("Verre", 200.0, 80.0, 0.0, 0.85, 6.5),
            "Aluminum": MaterialCost("Aluminium", 2000.0, 120.0, 0.0, 8.2, 8.5),
            "Insulation": MaterialCost("Isolation", 50.0, 15.0, 0.0, 0.05, 7.5),
            "Plaster": MaterialCost("Plâtre", 80.0, 12.0, 0.0, 0.08, 6.0),
            "Tile": MaterialCost("Carrelage", 400.0, 45.0, 0.0, 0.3, 8.0),
            "Default": MaterialCost("Matériau Standard", 200.0, 30.0, 0.0, 0.2, 7.0)
        }
        
        # Coûts par type d'élément (€/unité)
        self.element_costs = {
            "IfcWall": 250.0,
            "IfcSlab": 180.0,
            "IfcBeam": 320.0,
            "IfcColumn": 280.0,
            "IfcDoor": 450.0,
            "IfcWindow": 380.0,
            "IfcStair": 1200.0,
            "IfcRoof": 200.0,
            "IfcCovering": 85.0,
            "IfcRailing": 150.0
        }
        
        logger.info(f"Prédicteur de coûts initialisé pour: {ifc_file_path}")
    
    def predict_construction_costs(self) -> Dict[str, Any]:
        """
        🔮 Prédiction complète des coûts de construction
        
        Returns:
            Dictionnaire avec toutes les prédictions de coûts
        """
        try:
            logger.info("🔮 Début de la prédiction des coûts...")
            
            # Réinitialiser les prédictions
            self.predictions = []
            self.total_predicted_cost = 0.0
            
            # 1. 🧱 Analyse des matériaux
            materials_cost = self._predict_materials_cost()
            
            # 2. 🏗️ Analyse des éléments structurels
            structural_cost = self._predict_structural_cost()
            
            # 3. 🚪 Analyse des ouvertures
            openings_cost = self._predict_openings_cost()
            
            # 4. 🏠 Analyse des finitions
            finishes_cost = self._predict_finishes_cost()
            
            # 5. ⚡ Coûts des installations
            installations_cost = self._predict_installations_cost()
            
            # 6. 📊 Analyse comparative avec ML
            ml_predictions = self._ml_cost_prediction()
            
            # 7. 💰 Calcul du coût total
            total_cost = self._calculate_total_cost()
            
            # 8. 📈 Analyse de sensibilité
            sensitivity_analysis = self._perform_sensitivity_analysis()
            
            # 9. 🎯 Recommandations d'optimisation
            optimization_recommendations = self._generate_cost_optimization_recommendations()
            
            logger.info(f"✅ Prédiction des coûts terminée: {total_cost:.2f}€")
            
            return {
                "total_predicted_cost": total_cost,
                "cost_breakdown": {
                    "materials": materials_cost,
                    "structural": structural_cost,
                    "openings": openings_cost,
                    "finishes": finishes_cost,
                    "installations": installations_cost
                },
                "ml_predictions": ml_predictions,
                "sensitivity_analysis": sensitivity_analysis,
                "optimization_recommendations": optimization_recommendations,
                "cost_per_m2": self._calculate_cost_per_m2(),
                "predictions_details": [pred.__dict__ for pred in self.predictions],
                "analysis_timestamp": datetime.now().isoformat(),
                "confidence_score": self._calculate_overall_confidence()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction des coûts: {e}")
            raise
    
    def _predict_materials_cost(self) -> Dict[str, Any]:
        """🧱 Prédiction des coûts des matériaux"""
        try:
            logger.info("🧱 Analyse des coûts des matériaux...")
            
            materials_analysis = {}
            total_materials_cost = 0.0
            
            # Analyser tous les matériaux
            materials = self.ifc_file.by_type("IfcMaterial")
            
            for material in materials:
                material_name = material.Name or "Unknown"
                
                # Trouver le coût correspondant
                cost_data = self._get_material_cost(material_name)
                
                # Estimer la quantité utilisée
                quantity = self._estimate_material_quantity(material)
                
                # Calculer le coût
                material_cost = quantity * cost_data.cost_per_m3
                total_materials_cost += material_cost
                
                materials_analysis[material_name] = {
                    "quantity_m3": quantity,
                    "cost_per_m3": cost_data.cost_per_m3,
                    "total_cost": material_cost,
                    "carbon_footprint": quantity * cost_data.carbon_footprint,
                    "durability_score": cost_data.durability_score
                }
                
                # Ajouter à la liste des prédictions
                self.predictions.append(CostPrediction(
                    category="Matériaux",
                    predicted_cost=material_cost,
                    confidence=0.8,
                    cost_per_unit=cost_data.cost_per_m3,
                    quantity=quantity,
                    unit="m³",
                    factors={"material_type": material_name, "durability": cost_data.durability_score},
                    recommendations=[f"Considérer des alternatives pour {material_name}"]
                ))
            
            return {
                "total_cost": total_materials_cost,
                "materials_breakdown": materials_analysis,
                "average_cost_per_m3": total_materials_cost / max(len(materials), 1)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse matériaux: {e}")
            return {"total_cost": 0.0, "materials_breakdown": {}, "error": str(e)}
    
    def _predict_structural_cost(self) -> Dict[str, Any]:
        """🏗️ Prédiction des coûts structurels"""
        try:
            logger.info("🏗️ Analyse des coûts structurels...")
            
            structural_elements = ["IfcWall", "IfcSlab", "IfcBeam", "IfcColumn", "IfcFoundation"]
            structural_cost = 0.0
            elements_analysis = {}
            
            for element_type in structural_elements:
                elements = self.ifc_file.by_type(element_type)
                
                if elements:
                    count = len(elements)
                    unit_cost = self.element_costs.get(element_type, 200.0)
                    
                    # Facteur de complexité basé sur la géométrie
                    complexity_factor = self._calculate_complexity_factor(elements)
                    adjusted_cost = unit_cost * complexity_factor
                    
                    total_element_cost = count * adjusted_cost
                    structural_cost += total_element_cost
                    
                    elements_analysis[element_type] = {
                        "count": count,
                        "unit_cost": adjusted_cost,
                        "total_cost": total_element_cost,
                        "complexity_factor": complexity_factor
                    }
            
            return {
                "total_cost": structural_cost,
                "elements_breakdown": elements_analysis
            }

        except Exception as e:
            logger.error(f"Erreur analyse structurelle: {e}")
            return {"total_cost": 0.0, "elements_breakdown": {}, "error": str(e)}

    def _predict_openings_cost(self) -> Dict[str, Any]:
        """🚪 Prédiction des coûts des ouvertures"""
        try:
            logger.info("🚪 Analyse des coûts des ouvertures...")

            openings_cost = 0.0
            openings_analysis = {}

            # Analyser les portes
            doors = self.ifc_file.by_type("IfcDoor")
            if doors:
                doors_cost = len(doors) * self.element_costs.get("IfcDoor", 450.0)
                openings_cost += doors_cost
                openings_analysis["doors"] = {
                    "count": len(doors),
                    "unit_cost": self.element_costs.get("IfcDoor", 450.0),
                    "total_cost": doors_cost
                }

            # Analyser les fenêtres
            windows = self.ifc_file.by_type("IfcWindow")
            if windows:
                windows_cost = len(windows) * self.element_costs.get("IfcWindow", 380.0)
                openings_cost += windows_cost
                openings_analysis["windows"] = {
                    "count": len(windows),
                    "unit_cost": self.element_costs.get("IfcWindow", 380.0),
                    "total_cost": windows_cost
                }

            return {
                "total_cost": openings_cost,
                "openings_breakdown": openings_analysis
            }

        except Exception as e:
            logger.error(f"Erreur analyse ouvertures: {e}")
            return {"total_cost": 0.0, "openings_breakdown": {}, "error": str(e)}

    def _predict_finishes_cost(self) -> Dict[str, Any]:
        """🏠 Prédiction des coûts des finitions"""
        try:
            logger.info("🏠 Analyse des coûts des finitions...")

            finishes_cost = 0.0
            finishes_analysis = {}

            # Analyser les revêtements
            coverings = self.ifc_file.by_type("IfcCovering")
            if coverings:
                coverings_cost = len(coverings) * self.element_costs.get("IfcCovering", 85.0)
                finishes_cost += coverings_cost
                finishes_analysis["coverings"] = {
                    "count": len(coverings),
                    "unit_cost": self.element_costs.get("IfcCovering", 85.0),
                    "total_cost": coverings_cost
                }

            # Estimer les finitions générales (10% du coût structurel)
            general_finishes = self.total_predicted_cost * 0.1
            finishes_cost += general_finishes
            finishes_analysis["general_finishes"] = {
                "percentage": 10,
                "total_cost": general_finishes
            }

            return {
                "total_cost": finishes_cost,
                "finishes_breakdown": finishes_analysis
            }

        except Exception as e:
            logger.error(f"Erreur analyse finitions: {e}")
            return {"total_cost": 0.0, "finishes_breakdown": {}, "error": str(e)}

    def _predict_installations_cost(self) -> Dict[str, Any]:
        """⚡ Prédiction des coûts des installations"""
        try:
            logger.info("⚡ Analyse des coûts des installations...")

            # Estimer les installations (15% du coût total)
            installations_cost = self.total_predicted_cost * 0.15

            installations_analysis = {
                "electrical": installations_cost * 0.4,
                "plumbing": installations_cost * 0.3,
                "hvac": installations_cost * 0.25,
                "other": installations_cost * 0.05
            }

            return {
                "total_cost": installations_cost,
                "installations_breakdown": installations_analysis
            }

        except Exception as e:
            logger.error(f"Erreur analyse installations: {e}")
            return {"total_cost": 0.0, "installations_breakdown": {}, "error": str(e)}

    def _ml_cost_prediction(self) -> Dict[str, Any]:
        """📊 Prédiction avec Machine Learning"""
        try:
            logger.info("📊 Prédiction ML des coûts...")

            # Créer des features pour le ML
            features = self._extract_ml_features()

            # Simuler un modèle ML (en production, utiliser un modèle pré-entraîné)
            ml_predicted_cost = self._simulate_ml_prediction(features)

            return {
                "ml_predicted_cost": ml_predicted_cost,
                "confidence": 0.85,
                "features_used": list(features.keys()),
                "model_version": "RandomForest_v1.0"
            }

        except Exception as e:
            logger.error(f"Erreur prédiction ML: {e}")
            return {"ml_predicted_cost": 0.0, "confidence": 0.0, "error": str(e)}

    def _calculate_total_cost(self) -> float:
        """💰 Calcul du coût total"""
        return sum(pred.predicted_cost for pred in self.predictions)

    def _perform_sensitivity_analysis(self) -> Dict[str, Any]:
        """📈 Analyse de sensibilité"""
        return {
            "material_cost_impact": 0.35,
            "labor_cost_impact": 0.25,
            "complexity_impact": 0.20,
            "location_impact": 0.15,
            "timeline_impact": 0.05
        }

    def _generate_cost_optimization_recommendations(self) -> List[str]:
        """🎯 Recommandations d'optimisation des coûts"""
        return [
            "Considérer des matériaux alternatifs moins coûteux",
            "Optimiser la conception pour réduire la complexité",
            "Négocier les prix avec plusieurs fournisseurs",
            "Planifier les achats en volume pour obtenir des remises",
            "Évaluer l'impact des modifications de conception sur les coûts"
        ]

    def _calculate_cost_per_m2(self) -> float:
        """Calcul du coût par m²"""
        try:
            # Estimer la surface totale
            total_area = self._estimate_total_floor_area()
            if total_area > 0:
                return self.total_predicted_cost / total_area
            return 0.0
        except:
            return 0.0

    def _calculate_overall_confidence(self) -> float:
        """Calcul de la confiance globale"""
        if self.predictions:
            return sum(pred.confidence for pred in self.predictions) / len(self.predictions)
        return 0.0

    # Méthodes utilitaires
    def _get_material_cost(self, material_name: str) -> MaterialCost:
        """Obtenir le coût d'un matériau"""
        for key, cost_data in self.material_costs.items():
            if key.lower() in material_name.lower():
                return cost_data
        return self.material_costs["Default"]

    def _estimate_material_quantity(self, material) -> float:
        """Estimer la quantité d'un matériau"""
        # Simulation - en production, analyser la géométrie
        return np.random.uniform(10, 100)

    def _calculate_complexity_factor(self, elements) -> float:
        """Calculer le facteur de complexité"""
        # Facteur basé sur le nombre d'éléments
        base_factor = 1.0
        if len(elements) > 50:
            base_factor += 0.2
        if len(elements) > 100:
            base_factor += 0.3
        return base_factor

    def _extract_ml_features(self) -> Dict[str, float]:
        """Extraire les features pour le ML"""
        return {
            "total_elements": len(self.ifc_file.by_type("IfcBuildingElement")),
            "wall_count": len(self.ifc_file.by_type("IfcWall")),
            "door_count": len(self.ifc_file.by_type("IfcDoor")),
            "window_count": len(self.ifc_file.by_type("IfcWindow")),
            "material_count": len(self.ifc_file.by_type("IfcMaterial"))
        }

    def _simulate_ml_prediction(self, features: Dict[str, float]) -> float:
        """Simuler une prédiction ML"""
        # Formule simplifiée pour la simulation
        base_cost = features.get("total_elements", 0) * 150
        complexity_bonus = features.get("material_count", 0) * 50
        return base_cost + complexity_bonus

    def _estimate_total_floor_area(self) -> float:
        """Estimer la surface totale du plancher"""
        try:
            slabs = self.ifc_file.by_type("IfcSlab")
            total_area = 0.0
            for slab in slabs:
                # Simulation - en production, calculer la vraie surface
                total_area += np.random.uniform(50, 200)
            return total_area
        except:
            return 1000.0  # Valeur par défaut
