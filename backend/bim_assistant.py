"""
Assistant IA conversationnel pour l'analyse BIM
Permet de dialoguer avec les fichiers IFC via un chatbot intelligent
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
try:
    # Option 1: Ollama (Recommandé)
    from langchain.llms import Ollama
    from langchain.embeddings import OllamaEmbeddings
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    # Option 2: Hugging Face Transformers
    from langchain.llms import HuggingFacePipeline
    from langchain.embeddings import HuggingFaceEmbeddings
    from transformers import pipeline
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False

from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
import os
from dotenv import load_dotenv

from ifc_analyzer import IFCAnalyzer
from anomaly_detector import IFCAnomalyDetector

# Charger les variables d'environnement
load_dotenv()

logger = logging.getLogger(__name__)

class BIMAssistant:
    """Assistant IA pour l'analyse conversationnelle de fichiers BIM"""

    def __init__(self, model_type: str = "ollama", model_name: str = "llama3.1:8b"):
        """
        Initialise l'assistant BIM avec différents backends IA

        Args:
            model_type: Type de modèle ("ollama", "huggingface", "openai")
            model_name: Nom du modèle à utiliser
        """
        self.model_type = model_type
        self.model_name = model_name

        # Initialiser le LLM selon le type choisi
        self.llm, self.embeddings = self._initialize_llm_and_embeddings()

        # Mémoire conversationnelle
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Base de connaissances vectorielle
        self.vectorstore = None
        self.qa_chain = None
        
        # Données du modèle actuel
        self.current_ifc_data = None
        self.current_file_path = None
        
        # Contexte BIM spécialisé
        self.bim_context = self._create_bim_context()

    def _initialize_llm_and_embeddings(self):
        """Initialise le LLM et les embeddings selon le type choisi"""

        if self.model_type == "ollama" and OLLAMA_AVAILABLE:
            try:
                # Vérifier qu'Ollama est disponible
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    logger.info(f"Utilisation d'Ollama avec le modèle {self.model_name}")
                    llm = Ollama(
                        model=self.model_name,
                        temperature=0.1,
                        base_url="http://localhost:11434"
                    )
                    embeddings = OllamaEmbeddings(
                        model=self.model_name,
                        base_url="http://localhost:11434"
                    )
                    return llm, embeddings
                else:
                    logger.warning("Ollama non disponible, passage à Hugging Face")
            except Exception as e:
                logger.warning(f"Erreur Ollama: {e}, passage à Hugging Face")

        if self.model_type == "huggingface" and HUGGINGFACE_AVAILABLE:
            try:
                logger.info("Utilisation de Hugging Face Transformers")

                # Utiliser un modèle léger et performant
                model_name = "microsoft/DialoGPT-medium"  # Ou "distilbert-base-uncased"

                # Pipeline pour la génération de texte
                pipe = pipeline(
                    "text-generation",
                    model=model_name,
                    max_length=512,
                    temperature=0.1,
                    do_sample=True
                )

                llm = HuggingFacePipeline(pipeline=pipe)
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

                return llm, embeddings

            except Exception as e:
                logger.warning(f"Erreur Hugging Face: {e}")

        # Fallback: Assistant simple sans LLM externe
        logger.warning("Aucun LLM externe disponible, utilisation du mode simple")
        return None, None

    def _create_bim_context(self) -> str:
        """Crée le contexte spécialisé BIM pour l'assistant"""
        return """
        Vous êtes un assistant expert en BIM (Building Information Modeling) et en analyse de fichiers IFC.
        
        Votre rôle est d'aider les utilisateurs à comprendre et analyser leurs modèles BIM en répondant à leurs questions
        de manière claire et précise.
        
        Connaissances spécialisées:
        - Format IFC (Industry Foundation Classes) et ses entités
        - Éléments de construction: murs (IfcWall), dalles (IfcSlab), poutres (IfcBeam), colonnes (IfcColumn)
        - Espaces (IfcSpace) et leur analyse
        - Ouvertures: portes (IfcDoor), fenêtres (IfcWindow)
        - Matériaux et propriétés des éléments
        - Métriques de bâtiment: surfaces, volumes, ratios
        - Détection d'anomalies et problèmes de qualité BIM
        - Classification de bâtiments
        
        Instructions:
        1. Répondez toujours en français
        2. Soyez précis et technique quand nécessaire, mais restez accessible
        3. Utilisez les données du modèle IFC chargé pour répondre aux questions
        4. Si vous ne trouvez pas l'information dans les données, dites-le clairement
        5. Proposez des analyses complémentaires quand c'est pertinent
        6. Expliquez les termes techniques BIM si nécessaire
        """
    
    def load_ifc_model(self, ifc_file_path: str) -> Dict[str, Any]:
        """
        Charge un modèle IFC et prépare l'assistant pour les questions
        
        Args:
            ifc_file_path: Chemin vers le fichier IFC
            
        Returns:
            Dictionnaire avec le résumé du chargement
        """
        try:
            logger.info(f"Chargement du modèle IFC: {ifc_file_path}")
            
            # Analyser le fichier IFC
            analyzer = IFCAnalyzer(ifc_file_path)
            self.current_ifc_data = analyzer.generate_full_analysis()
            self.current_file_path = ifc_file_path
            
            # Détecter les anomalies
            anomaly_detector = IFCAnomalyDetector(ifc_file_path)
            anomalies = anomaly_detector.detect_all_anomalies()
            anomaly_summary = anomaly_detector.get_anomaly_summary()
            
            # Ajouter les anomalies aux données
            self.current_ifc_data["anomalies"] = {
                "anomalies_list": [anomaly.__dict__ for anomaly in anomalies],
                "summary": anomaly_summary
            }
            
            # Créer la base de connaissances vectorielle
            self._create_vector_store()
            
            # Créer la chaîne de Q&A
            self._create_qa_chain()
            
            # Résumé du chargement
            project_info = self.current_ifc_data.get("project_info", {})
            metrics = self.current_ifc_data.get("building_metrics", {})
            
            summary = {
                "status": "success",
                "file_name": Path(ifc_file_path).name,
                "project_name": project_info.get("project_name", "Non défini"),
                "building_name": project_info.get("building_name", "Non défini"),
                "total_elements": project_info.get("total_elements", 0),
                "total_storeys": metrics.get("storeys", {}).get("total_storeys", 0),
                "total_spaces": metrics.get("spaces", {}).get("total_spaces", 0),
                "total_anomalies": anomaly_summary.get("total_anomalies", 0),
                "file_size_mb": round(project_info.get("file_size_mb", 0), 2)
            }
            
            logger.info("Modèle IFC chargé avec succès")
            return summary
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle IFC: {e}")
            raise
    
    def _create_vector_store(self):
        """Crée la base de connaissances vectorielle à partir des données IFC"""
        if not self.current_ifc_data:
            raise ValueError("Aucun modèle IFC chargé")
        
        # Convertir les données IFC en documents textuels
        documents = []
        
        # Informations du projet
        project_info = self.current_ifc_data.get("project_info", {})
        project_text = f"""
        Informations du projet:
        - Nom du projet: {project_info.get('project_name', 'Non défini')}
        - Nom du bâtiment: {project_info.get('building_name', 'Non défini')}
        - Description: {project_info.get('building_description', 'Non défini')}
        - Schema IFC: {project_info.get('schema', 'Non défini')}
        - Nombre total d'éléments: {project_info.get('total_elements', 0)}
        - Taille du fichier: {project_info.get('file_size_mb', 0):.2f} MB
        """
        documents.append(Document(page_content=project_text, metadata={"type": "project_info"}))
        
        # Métriques du bâtiment
        metrics = self.current_ifc_data.get("building_metrics", {})
        
        # Surfaces
        surfaces = metrics.get("surfaces", {})
        surfaces_text = f"""
        Surfaces du bâtiment:
        - Surface totale des planchers: {surfaces.get('total_floor_area', 0):.2f} m²
        - Surface totale des murs: {surfaces.get('total_wall_area', 0):.2f} m²
        - Surface totale des fenêtres: {surfaces.get('total_window_area', 0):.2f} m²
        - Surface totale des portes: {surfaces.get('total_door_area', 0):.2f} m²
        - Surface totale des toitures: {surfaces.get('total_roof_area', 0):.2f} m²
        """
        documents.append(Document(page_content=surfaces_text, metadata={"type": "surfaces"}))
        
        # Volumes
        volumes = metrics.get("volumes", {})
        volumes_text = f"""
        Volumes du bâtiment:
        - Volume total des espaces: {volumes.get('total_space_volume', 0):.2f} m³
        - Volume structurel: {volumes.get('structural_volume', 0):.2f} m³
        - Volume total du bâtiment: {volumes.get('total_building_volume', 0):.2f} m³
        """
        documents.append(Document(page_content=volumes_text, metadata={"type": "volumes"}))
        
        # Étages
        storeys = metrics.get("storeys", {})
        storeys_text = f"""
        Étages du bâtiment:
        - Nombre total d'étages: {storeys.get('total_storeys', 0)}
        """
        
        for storey in storeys.get("storey_details", []):
            storeys_text += f"""
        - Étage '{storey.get('name', 'Sans nom')}': 
          Élévation: {storey.get('elevation', 'Non définie')} m
          Nombre d'éléments: {storey.get('elements_count', 0)}
          Description: {storey.get('description', 'Aucune')}
            """
        
        documents.append(Document(page_content=storeys_text, metadata={"type": "storeys"}))
        
        # Espaces
        spaces = metrics.get("spaces", {})
        spaces_text = f"""
        Espaces du bâtiment:
        - Nombre total d'espaces: {spaces.get('total_spaces', 0)}
        - Types d'espaces: {', '.join(f"{k}: {v}" for k, v in spaces.get('space_types', {}).items())}
        """
        
        for space in spaces.get("space_details", []):
            spaces_text += f"""
        - Espace '{space.get('name', 'Sans nom')}':
          Type: {space.get('type', 'Non défini')}
          Surface: {space.get('area', 0):.2f} m²
          Volume: {space.get('volume', 0):.2f} m³
            """
        
        documents.append(Document(page_content=spaces_text, metadata={"type": "spaces"}))
        
        # Ouvertures
        openings = metrics.get("openings", {})
        openings_text = f"""
        Ouvertures du bâtiment:
        - Nombre total de fenêtres: {openings.get('total_windows', 0)}
        - Nombre total de portes: {openings.get('total_doors', 0)}
        - Ratio fenêtres/murs: {openings.get('window_wall_ratio', 0):.3f}
        """
        documents.append(Document(page_content=openings_text, metadata={"type": "openings"}))
        
        # Éléments structurels
        structural = metrics.get("structural_elements", {})
        structural_text = f"""
        Éléments structurels:
        - Nombre de poutres: {structural.get('beams', 0)}
        - Nombre de colonnes: {structural.get('columns', 0)}
        - Nombre de murs: {structural.get('walls', 0)}
        - Nombre de dalles: {structural.get('slabs', 0)}
        - Nombre de fondations: {structural.get('foundations', 0)}
        """
        documents.append(Document(page_content=structural_text, metadata={"type": "structural"}))
        
        # Matériaux
        materials = metrics.get("materials", {})
        materials_text = f"""
        Matériaux utilisés:
        - Nombre total de matériaux: {materials.get('total_materials', 0)}
        - Liste des matériaux: {', '.join([mat.get('name', 'Sans nom') for mat in materials.get('material_list', [])])}
        """
        documents.append(Document(page_content=materials_text, metadata={"type": "materials"}))
        
        # Anomalies
        anomalies_data = self.current_ifc_data.get("anomalies", {})
        anomaly_summary = anomalies_data.get("summary", {})
        anomalies_text = f"""
        Anomalies détectées:
        - Nombre total d'anomalies: {anomaly_summary.get('total_anomalies', 0)}
        - Anomalies critiques: {anomaly_summary.get('by_severity', {}).get('critical', 0)}
        - Anomalies importantes: {anomaly_summary.get('by_severity', {}).get('high', 0)}
        - Anomalies moyennes: {anomaly_summary.get('by_severity', {}).get('medium', 0)}
        - Anomalies mineures: {anomaly_summary.get('by_severity', {}).get('low', 0)}
        - Problèmes les plus fréquents: {', '.join([f"{issue[0]} ({issue[1]})" for issue in anomaly_summary.get('most_common_issues', [])])}
        """
        documents.append(Document(page_content=anomalies_text, metadata={"type": "anomalies"}))
        
        # Créer le vector store
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        split_documents = text_splitter.split_documents(documents)
        
        self.vectorstore = FAISS.from_documents(
            split_documents,
            self.embeddings
        )
        
        logger.info(f"Base de connaissances créée avec {len(split_documents)} chunks")
    
    def _create_qa_chain(self):
        """Crée la chaîne de question-réponse"""
        if not self.vectorstore:
            raise ValueError("Base de connaissances non créée")
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 5}),
            memory=self.memory,
            return_source_documents=True,
            verbose=True
        )
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Pose une question sur le modèle IFC chargé
        
        Args:
            question: Question de l'utilisateur
            
        Returns:
            Dictionnaire avec la réponse et les métadonnées
        """
        if not self.qa_chain:
            raise ValueError("Aucun modèle IFC chargé ou chaîne Q&A non initialisée")
        
        try:
            # Enrichir la question avec le contexte BIM
            enriched_question = f"""
            {self.bim_context}
            
            Fichier IFC analysé: {Path(self.current_file_path).name if self.current_file_path else 'Non défini'}
            
            Question de l'utilisateur: {question}
            
            Répondez en utilisant les données du modèle IFC chargé. Si l'information n'est pas disponible dans les données,
            dites-le clairement et proposez des analyses complémentaires si pertinent.
            """
            
            # Obtenir la réponse
            result = self.qa_chain({"question": enriched_question})
            
            response = {
                "answer": result["answer"],
                "source_documents": [
                    {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ],
                "question": question,
                "file_analyzed": Path(self.current_file_path).name if self.current_file_path else None
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la question: {e}")
            raise
    
    def get_suggested_questions(self) -> List[str]:
        """Retourne une liste de questions suggérées basées sur le modèle chargé"""
        if not self.current_ifc_data:
            return [
                "Chargez d'abord un fichier IFC pour obtenir des suggestions de questions."
            ]
        
        suggestions = [
            "Quelle est la surface totale habitable de ce bâtiment ?",
            "Combien d'étages compte ce bâtiment ?",
            "Quels sont les matériaux principaux utilisés ?",
            "Y a-t-il des anomalies détectées dans ce modèle ?",
            "Quel est le ratio fenêtres/murs de ce bâtiment ?",
            "Combien d'espaces différents sont définis ?",
            "Quels sont les éléments structurels principaux ?",
            "Y a-t-il des problèmes de connectivité entre les éléments ?",
            "Quelle est la complexité de ce modèle BIM ?",
            "Ce bâtiment respecte-t-il les bonnes pratiques BIM ?"
        ]
        
        # Ajouter des suggestions spécifiques basées sur les données
        metrics = self.current_ifc_data.get("building_metrics", {})
        
        if metrics.get("anomalies", {}).get("summary", {}).get("total_anomalies", 0) > 0:
            suggestions.append("Quelles sont les anomalies les plus critiques ?")
        
        if metrics.get("spaces", {}).get("total_spaces", 0) > 10:
            suggestions.append("Pouvez-vous analyser la répartition des espaces ?")
        
        if metrics.get("storeys", {}).get("total_storeys", 0) > 3:
            suggestions.append("Comment sont répartis les éléments par étage ?")
        
        return suggestions
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique de la conversation"""
        if not self.memory.chat_memory.messages:
            return []
        
        history = []
        messages = self.memory.chat_memory.messages
        
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                history.append({
                    "question": messages[i].content,
                    "answer": messages[i + 1].content,
                    "timestamp": getattr(messages[i], 'timestamp', None)
                })
        
        return history
    
    def clear_conversation(self):
        """Efface l'historique de la conversation"""
        self.memory.clear()
        logger.info("Historique de conversation effacé")
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Retourne un résumé du modèle actuellement chargé"""
        if not self.current_ifc_data:
            return {"status": "no_model_loaded"}
        
        project_info = self.current_ifc_data.get("project_info", {})
        metrics = self.current_ifc_data.get("building_metrics", {})
        anomalies = self.current_ifc_data.get("anomalies", {}).get("summary", {})
        
        return {
            "status": "model_loaded",
            "file_path": self.current_file_path,
            "file_name": Path(self.current_file_path).name if self.current_file_path else None,
            "project_name": project_info.get("project_name"),
            "building_name": project_info.get("building_name"),
            "schema": project_info.get("schema"),
            "total_elements": project_info.get("total_elements"),
            "file_size_mb": project_info.get("file_size_mb"),
            "key_metrics": {
                "total_floor_area": metrics.get("surfaces", {}).get("total_floor_area"),
                "total_storeys": metrics.get("storeys", {}).get("total_storeys"),
                "total_spaces": metrics.get("spaces", {}).get("total_spaces"),
                "total_anomalies": anomalies.get("total_anomalies"),
                "window_wall_ratio": metrics.get("openings", {}).get("window_wall_ratio")
            }
        }
    
    def generate_quick_insights(self) -> List[str]:
        """Génère des insights rapides sur le modèle chargé"""
        if not self.current_ifc_data:
            return ["Aucun modèle chargé"]
        
        insights = []
        metrics = self.current_ifc_data.get("building_metrics", {})
        project_info = self.current_ifc_data.get("project_info", {})
        
        # Insights sur la taille
        floor_area = metrics.get("surfaces", {}).get("total_floor_area", 0)
        if floor_area > 0:
            if floor_area < 100:
                insights.append("🏠 Petit bâtiment (< 100 m²)")
            elif floor_area < 500:
                insights.append("🏢 Bâtiment de taille moyenne (100-500 m²)")
            elif floor_area < 2000:
                insights.append("🏬 Grand bâtiment (500-2000 m²)")
            else:
                insights.append("🏭 Très grand bâtiment (> 2000 m²)")
        
        # Insights sur les étages
        storeys = metrics.get("storeys", {}).get("total_storeys", 0)
        if storeys == 1:
            insights.append("📐 Bâtiment de plain-pied")
        elif storeys <= 3:
            insights.append(f"🏘️ Bâtiment de {storeys} étages (faible hauteur)")
        else:
            insights.append(f"🏗️ Bâtiment de {storeys} étages (hauteur importante)")
        
        # Insights sur les anomalies
        total_anomalies = self.current_ifc_data.get("anomalies", {}).get("summary", {}).get("total_anomalies", 0)
        if total_anomalies == 0:
            insights.append("✅ Aucune anomalie détectée - Modèle de bonne qualité")
        elif total_anomalies < 5:
            insights.append("⚠️ Quelques anomalies mineures détectées")
        else:
            insights.append(f"🚨 {total_anomalies} anomalies détectées - Révision recommandée")
        
        # Insights sur la complexité
        total_elements = project_info.get("total_elements", 0)
        if total_elements < 100:
            insights.append("🔧 Modèle simple (< 100 éléments)")
        elif total_elements < 1000:
            insights.append("⚙️ Modèle de complexité moyenne")
        else:
            insights.append("🔩 Modèle complexe (> 1000 éléments)")
        
        return insights
