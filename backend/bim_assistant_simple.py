"""
Assistant BIM Simple - Version sans dépendances externes
Fournit des réponses rapides basées sur l'analyse IFC sans IA complexe
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
from datetime import datetime

from ifc_analyzer import IFCAnalyzer
from anomaly_detector import IFCAnomalyDetector

logger = logging.getLogger(__name__)

class SimpleBIMAssistant:
    """Assistant BIM simple sans dépendances IA externes"""

    def __init__(self):
        """Initialise l'assistant simple"""
        self.ifc_file_path = None
        self.analysis_data = None
        self.anomalies_data = None
        self.conversation_history = []
        self.model_summary = None
        
        # Base de connaissances simple pour les réponses
        self.knowledge_base = {
            "surfaces": {
                "keywords": ["surface", "aire", "m2", "m²", "superficie"],
                "response_template": "La surface totale du bâtiment est de {total_floor_area} m². Les murs représentent {total_wall_area} m², les fenêtres {total_window_area} m² et les portes {total_door_area} m²."
            },
            "etages": {
                "keywords": ["étage", "niveau", "storey", "floor"],
                "response_template": "Le bâtiment compte {total_storeys} étage(s). Voici les détails : {storey_details}"
            },
            "espaces": {
                "keywords": ["espace", "pièce", "room", "space"],
                "response_template": "Le bâtiment contient {total_spaces} espace(s). Types d'espaces identifiés : {space_types}"
            },
            "elements": {
                "keywords": ["élément", "composant", "element", "mur", "poutre", "colonne"],
                "response_template": "Le modèle contient {total_elements} éléments au total. Éléments structurels : {beams} poutres, {columns} colonnes, {walls} murs."
            },
            "anomalies": {
                "keywords": ["anomalie", "erreur", "problème", "défaut"],
                "response_template": "J'ai détecté {total_anomalies} anomalie(s) dans le modèle. Les principales catégories sont : {anomaly_categories}"
            },
            "materiaux": {
                "keywords": ["matériau", "material", "béton", "acier", "bois"],
                "response_template": "Le modèle utilise {total_materials} matériau(x) différent(s). Matériaux principaux : {material_list}"
            }
        }
        
        logger.info("🤖 Assistant BIM Simple initialisé (réponses rapides)")

    def load_ifc_model(self, ifc_file_path: str) -> Dict[str, Any]:
        """Charge et analyse un modèle IFC"""
        try:
            self.ifc_file_path = ifc_file_path
            logger.info(f"📂 Chargement du modèle IFC: {ifc_file_path}")
            
            # Analyser le fichier IFC
            analyzer = IFCAnalyzer(ifc_file_path)
            self.analysis_data = analyzer.generate_full_analysis()
            
            # Détecter les anomalies
            try:
                anomaly_detector = IFCAnomalyDetector(ifc_file_path)
                anomalies_list = anomaly_detector.detect_all_anomalies()
                self.anomalies_data = {
                    "total_anomalies": len(anomalies_list),
                    "anomalies": [
                        {
                            "type": anomaly.anomaly_type,
                            "severity": anomaly.severity.value,
                            "description": anomaly.description
                        } for anomaly in anomalies_list[:10]  # Limiter à 10 pour la performance
                    ]
                }
            except Exception as e:
                logger.warning(f"Erreur détection anomalies: {e}")
                self.anomalies_data = {"total_anomalies": 0, "anomalies": []}
            
            # Générer le résumé
            self.model_summary = self._generate_model_summary()
            
            logger.info("✅ Modèle IFC chargé et analysé avec succès")
            return self.model_summary
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            raise

    def _generate_model_summary(self) -> Dict[str, Any]:
        """Génère un résumé du modèle chargé"""
        if not self.analysis_data:
            return {"error": "Aucune donnée d'analyse disponible"}
        
        building_metrics = self.analysis_data.get("building_metrics", {})
        project_info = self.analysis_data.get("project_info", {})
        
        return {
            "project_name": project_info.get("project_name", "Projet BIM"),
            "total_elements": project_info.get("total_elements", 0),
            "surfaces": building_metrics.get("surfaces", {}),
            "storeys": building_metrics.get("storeys", {}),
            "spaces": building_metrics.get("spaces", {}),
            "structural_elements": building_metrics.get("structural_elements", {}),
            "materials": building_metrics.get("materials", {}),
            "anomalies_count": self.anomalies_data.get("total_anomalies", 0),
            "analysis_timestamp": datetime.now().isoformat()
        }

    def ask_question(self, question: str) -> str:
        """Répond à une question sur le modèle BIM"""
        if not self.analysis_data:
            return "❌ Aucun modèle IFC n'est chargé. Veuillez d'abord charger un fichier IFC."
        
        # Ajouter à l'historique
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "type": "user"
        })
        
        try:
            # Analyser la question et générer une réponse
            response = self._generate_response(question)
            
            # Ajouter la réponse à l'historique
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "response": response,
                "type": "assistant"
            })
            
            return response
            
        except Exception as e:
            error_response = f"❌ Erreur lors de la génération de la réponse: {str(e)}"
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "response": error_response,
                "type": "error"
            })
            return error_response

    def _generate_response(self, question: str) -> str:
        """Génère une réponse basée sur la question et les données d'analyse"""
        question_lower = question.lower()
        
        # Rechercher dans la base de connaissances
        for category, knowledge in self.knowledge_base.items():
            if any(keyword in question_lower for keyword in knowledge["keywords"]):
                return self._format_response(category, knowledge["response_template"])
        
        # Questions générales
        if any(word in question_lower for word in ["résumé", "summary", "général", "overview"]):
            return self._generate_general_summary()
        
        if any(word in question_lower for word in ["aide", "help", "que", "what", "comment", "how"]):
            return self._generate_help_response()
        
        # Réponse par défaut
        return self._generate_default_response(question)

    def _format_response(self, category: str, template: str) -> str:
        """Formate une réponse avec les données du modèle"""
        try:
            building_metrics = self.analysis_data.get("building_metrics", {})
            project_info = self.analysis_data.get("project_info", {})
            
            format_data = {
                # Surfaces
                "total_floor_area": round(building_metrics.get("surfaces", {}).get("total_floor_area", 0)),
                "total_wall_area": round(building_metrics.get("surfaces", {}).get("total_wall_area", 0)),
                "total_window_area": round(building_metrics.get("surfaces", {}).get("total_window_area", 0)),
                "total_door_area": round(building_metrics.get("surfaces", {}).get("total_door_area", 0)),
                
                # Étages
                "total_storeys": building_metrics.get("storeys", {}).get("total_storeys", 0),
                "storey_details": ", ".join([f"{s['name']} ({s['elevation']:.1f}m)" for s in building_metrics.get("storeys", {}).get("storey_details", [])[:3]]),
                
                # Espaces
                "total_spaces": building_metrics.get("spaces", {}).get("total_spaces", 0),
                "space_types": ", ".join(list(building_metrics.get("spaces", {}).get("space_types", {}).keys())[:5]),
                
                # Éléments
                "total_elements": project_info.get("total_elements", 0),
                "beams": building_metrics.get("structural_elements", {}).get("beams", 0),
                "columns": building_metrics.get("structural_elements", {}).get("columns", 0),
                "walls": building_metrics.get("structural_elements", {}).get("walls", 0),
                
                # Anomalies
                "total_anomalies": self.anomalies_data.get("total_anomalies", 0),
                "anomaly_categories": ", ".join(list(set([a["type"] for a in self.anomalies_data.get("anomalies", [])]))),
                
                # Matériaux
                "total_materials": building_metrics.get("materials", {}).get("total_materials", 0),
                "material_list": ", ".join(list(building_metrics.get("materials", {}).get("material_details", {}).keys())[:5])
            }
            
            return template.format(**format_data)
            
        except Exception as e:
            logger.error(f"Erreur formatage réponse: {e}")
            return f"❌ Erreur lors du formatage de la réponse pour {category}"

    def _generate_general_summary(self) -> str:
        """Génère un résumé général du modèle"""
        if not self.model_summary:
            return "❌ Aucun résumé disponible"
        
        return f"""📊 **Résumé du Modèle BIM**

🏗️ **Projet:** {self.model_summary.get('project_name', 'Non défini')}
📐 **Éléments totaux:** {self.model_summary.get('total_elements', 0):,}
🏢 **Étages:** {self.model_summary.get('storeys', {}).get('total_storeys', 0)}
🏠 **Espaces:** {self.model_summary.get('spaces', {}).get('total_spaces', 0)}
📏 **Surface totale:** {round(self.model_summary.get('surfaces', {}).get('total_floor_area', 0)):,} m²
🚨 **Anomalies détectées:** {self.model_summary.get('anomalies_count', 0)}

💡 Posez-moi des questions spécifiques sur les surfaces, étages, espaces, éléments ou anomalies !"""

    def _generate_help_response(self) -> str:
        """Génère une réponse d'aide"""
        return """🤖 **Assistant BIM - Questions que vous pouvez poser:**

📐 **Surfaces:** "Quelle est la surface totale ?" "Combien de m² de murs ?"
🏢 **Étages:** "Combien d'étages ?" "Quels sont les niveaux ?"
🏠 **Espaces:** "Combien d'espaces ?" "Quels types de pièces ?"
🔧 **Éléments:** "Combien d'éléments ?" "Nombre de poutres/colonnes ?"
🚨 **Anomalies:** "Y a-t-il des problèmes ?" "Quelles anomalies ?"
🧱 **Matériaux:** "Quels matériaux sont utilisés ?"
📊 **Résumé:** "Donne-moi un résumé général"

💡 **Astuce:** Posez des questions en français, je comprends le contexte BIM !"""

    def _generate_default_response(self, question: str) -> str:
        """Génère une réponse par défaut"""
        return f"""🤔 Je n'ai pas trouvé d'information spécifique pour: "{question}"

💡 **Suggestions:**
- Demandez des informations sur les surfaces, étages, espaces
- Posez des questions sur les éléments structurels
- Demandez un résumé général du modèle
- Tapez "aide" pour voir toutes les possibilités

📊 **Données disponibles:** {len(self.analysis_data)} catégories d'analyse"""

    def get_suggested_questions(self) -> List[str]:
        """Retourne des questions suggérées"""
        if not self.analysis_data:
            return ["Chargez d'abord un fichier IFC pour obtenir des suggestions."]
        
        suggestions = [
            "Quelle est la surface totale du bâtiment ?",
            "Combien d'étages compte le bâtiment ?",
            "Quels types d'espaces sont présents ?",
            "Y a-t-il des anomalies dans le modèle ?",
            "Combien d'éléments structurels ?",
            "Donne-moi un résumé général",
            "Quels matériaux sont utilisés ?",
            "Quelle est la hauteur du bâtiment ?"
        ]
        
        return suggestions

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique de conversation"""
        return self.conversation_history

    def clear_conversation(self):
        """Efface l'historique de conversation"""
        self.conversation_history = []
        logger.info("🧹 Historique de conversation effacé")

    def get_model_summary(self) -> Dict[str, Any]:
        """Retourne le résumé du modèle"""
        return self.model_summary or {"error": "Aucun modèle chargé"}

    def generate_quick_insights(self) -> List[str]:
        """Génère des insights rapides sur le modèle"""
        if not self.analysis_data:
            return ["Aucun modèle chargé"]
        
        insights = []
        building_metrics = self.analysis_data.get("building_metrics", {})
        
        # Insights sur les surfaces
        surfaces = building_metrics.get("surfaces", {})
        if surfaces.get("total_floor_area", 0) > 1000:
            insights.append(f"🏢 Grand bâtiment: {round(surfaces['total_floor_area']):,} m² de surface")
        
        # Insights sur les étages
        storeys = building_metrics.get("storeys", {})
        if storeys.get("total_storeys", 0) > 5:
            insights.append(f"🏗️ Bâtiment de grande hauteur: {storeys['total_storeys']} étages")
        
        # Insights sur les anomalies
        if self.anomalies_data.get("total_anomalies", 0) > 0:
            insights.append(f"⚠️ {self.anomalies_data['total_anomalies']} anomalie(s) détectée(s)")
        
        # Insights sur la complexité
        total_elements = self.analysis_data.get("project_info", {}).get("total_elements", 0)
        if total_elements > 1000:
            insights.append(f"🔧 Modèle complexe: {total_elements:,} éléments")
        
        return insights if insights else ["📊 Modèle BIM standard analysé"]
