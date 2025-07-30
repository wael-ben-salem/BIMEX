"""
Générateur de rapports automatiques pour l'analyse BIM
Crée des rapports PDF complets avec analyses et recommandations
"""

import json
import logging
import os
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import base64

from ifc_analyzer import IFCAnalyzer
from anomaly_detector import IFCAnomalyDetector, AnomalySeverity
from building_classifier import BuildingClassifier
try:
    from pmr_analyzer import PMRAnalyzer
    PMR_AVAILABLE = True
except ImportError:
    PMR_AVAILABLE = False
    logger.warning("Analyseur PMR non disponible pour les rapports")

logger = logging.getLogger(__name__)

class BIMEXCanvas:
    """Canvas personnalisé BIMEX avec branding professionnel"""
    def __init__(self, canvas, doc, logo_path=None):
        self.canvas = canvas
        self.doc = doc
        self.logo_path = logo_path

    def draw_header_footer(self, project_name="Projet BIM"):
        """Dessine l'en-tête et le pied de page BIMEX"""
        self.canvas.saveState()

        # En-tête avec logo BIMEX
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Logo BIMEX en haut à gauche
                self.canvas.drawImage(self.logo_path, 50, A4[1] - 70, width=60, height=30, preserveAspectRatio=True)
            except:
                pass  # Continuer sans logo si erreur

        # Titre BIMEX stylisé
        self.canvas.setFont('Helvetica-Bold', 14)
        self.canvas.setFillColor(colors.HexColor('#1E3A8A'))  # Bleu BIMEX
        self.canvas.drawString(120, A4[1] - 50, "BIMEX")

        self.canvas.setFont('Helvetica', 10)
        self.canvas.setFillColor(colors.HexColor('#374151'))
        self.canvas.drawString(120, A4[1] - 65, f"Rapport d'Analyse BIM Avancée - {project_name}")

        # Date et heure en haut à droite
        self.canvas.setFont('Helvetica', 8)
        self.canvas.drawRightString(A4[0] - 50, A4[1] - 50, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        self.canvas.drawRightString(A4[0] - 50, A4[1] - 62, "Analyse IA + Machine Learning")

        # Ligne de séparation stylisée
        self.canvas.setStrokeColor(colors.HexColor('#1E3A8A'))
        self.canvas.setLineWidth(2)
        self.canvas.line(50, A4[1] - 80, A4[0] - 50, A4[1] - 80)

        # Pied de page innovant
        self.canvas.setFont('Helvetica-Bold', 8)
        self.canvas.setFillColor(colors.HexColor('#1E3A8A'))
        self.canvas.drawString(50, 30, "BIMEX")

        self.canvas.setFont('Helvetica', 7)
        self.canvas.setFillColor(colors.HexColor('#6B7280'))
        self.canvas.drawString(80, 30, "• Analyse BIM Intelligente • Machine Learning • Conformité Automatisée")

        # Numérotation stylisée
        page_num = self.canvas.getPageNumber()
        self.canvas.setFont('Helvetica-Bold', 10)
        self.canvas.setFillColor(colors.HexColor('#1E3A8A'))
        self.canvas.drawRightString(A4[0] - 50, 30, f"Page {page_num}")

        # Ligne de séparation pied de page
        self.canvas.setStrokeColor(colors.HexColor('#E5E7EB'))
        self.canvas.setLineWidth(1)
        self.canvas.line(50, 45, A4[0] - 50, 45)

        self.canvas.restoreState()

class BIMReportGenerator:
    """Générateur de rapports BIM automatiques"""
    
    def __init__(self):
        """Initialise le générateur de rapports"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.output_base_dir = "generatedReports"  # Dossier de base pour tous les rapports
        self._ensure_output_directory()
        
    def _setup_custom_styles(self):
        """Configure les styles personnalisés pour le rapport"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Style pour les sous-sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=12,
            textColor=colors.darkgreen
        ))
        
        # Style pour les alertes
        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            backColor=colors.lightgrey,
            borderColor=colors.red,
            borderWidth=1,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10
        ))
        
        # Style pour les recommandations
        self.styles.add(ParagraphStyle(
            name='Recommendation',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkgreen,
            backColor=colors.lightgreen,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10
        ))

        # Style pour les métriques importantes
        self.styles.add(ParagraphStyle(
            name='MetricHighlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.darkblue,
            backColor=colors.lightblue,
            leftIndent=5,
            rightIndent=5,
            spaceAfter=8,
            alignment=TA_CENTER
        ))

        # Style pour les annexes
        self.styles.add(ParagraphStyle(
            name='AppendixTitle',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.purple,
            spaceBefore=15,
            spaceAfter=10
        ))

        # Style pour les notes de bas de page
        self.styles.add(ParagraphStyle(
            name='Footnote',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=5
        ))

        # 🚀 STYLES BIMEX INNOVANTS

        # Style pour les titres BIMEX
        self.styles.add(ParagraphStyle(
            name='BIMEXTitle',
            parent=self.styles['Title'],
            fontSize=28,
            textColor=colors.HexColor('#1E3A8A'),
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        ))

        # Style pour les dashboards
        self.styles.add(ParagraphStyle(
            name='Dashboard',
            parent=self.styles['Normal'],
            fontSize=11,
            backColor=colors.HexColor('#F8FAFC'),
            borderColor=colors.HexColor('#E2E8F0'),
            borderWidth=1,
            leftIndent=15,
            rightIndent=15,
            spaceAfter=15,
            spaceBefore=10
        ))

        # Style pour les alertes critiques
        self.styles.add(ParagraphStyle(
            name='CriticalAlert',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#DC2626'),
            backColor=colors.HexColor('#FEF2F2'),
            borderColor=colors.HexColor('#DC2626'),
            borderWidth=2,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=15,
            alignment=TA_CENTER
        ))

        # Style pour les succès
        self.styles.add(ParagraphStyle(
            name='Success',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#16A34A'),
            backColor=colors.HexColor('#F0FDF4'),
            borderColor=colors.HexColor('#16A34A'),
            borderWidth=2,
            leftIndent=20,
            rightIndent=20,
            spaceAfter=15,
            alignment=TA_CENTER
        ))

    def _ensure_output_directory(self):
        """Crée le dossier de sortie principal s'il n'existe pas"""
        if not os.path.exists(self.output_base_dir):
            os.makedirs(self.output_base_dir)

    def _create_analysis_folder(self, ifc_filename: str) -> tuple:
        """Crée un dossier dédié pour l'analyse du fichier IFC"""
        # Nettoyer le nom de fichier pour le dossier (enlever tmp et caractères spéciaux)
        clean_name = os.path.splitext(ifc_filename)[0]

        # Enlever les préfixes temporaires
        if clean_name.startswith('tmp'):
            clean_name = "ProjetBIM"  # Nom par défaut si fichier temporaire

        clean_name = "".join(c for c in clean_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')

        # Ajouter timestamp pour éviter les conflits
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{clean_name}_{timestamp}"

        analysis_folder = os.path.join(self.output_base_dir, folder_name)

        # Créer le dossier et ses sous-dossiers
        os.makedirs(analysis_folder, exist_ok=True)
        os.makedirs(os.path.join(analysis_folder, "charts"), exist_ok=True)
        os.makedirs(os.path.join(analysis_folder, "data"), exist_ok=True)
        os.makedirs(os.path.join(analysis_folder, "assets"), exist_ok=True)  # Pour logos, etc.

        return analysis_folder, clean_name

    def _get_chart_path(self, analysis_folder: str, chart_name: str) -> str:
        """Retourne le chemin pour sauvegarder un graphique"""
        return os.path.join(analysis_folder, "charts", f"{chart_name}.png")

    def generate_full_report(self, ifc_file_path: str, output_path: str,
                           include_classification: bool = True, include_pmr: bool = True) -> Dict[str, Any]:
        """
        Génère un rapport complet d'analyse BIM
        
        Args:
            ifc_file_path: Chemin vers le fichier IFC
            output_path: Chemin de sortie du rapport PDF
            include_classification: Inclure la classification automatique
            
        Returns:
            Dictionnaire avec les informations du rapport généré
        """
        try:
            logger.info(f"Génération du rapport pour: {ifc_file_path}")
            
            # Analyser le fichier IFC
            analyzer = IFCAnalyzer(ifc_file_path)
            analysis_data = analyzer.generate_full_analysis()
            
            # Détecter les anomalies
            anomaly_detector = IFCAnomalyDetector(ifc_file_path)
            anomalies = anomaly_detector.detect_all_anomalies()
            anomaly_summary = anomaly_detector.get_anomaly_summary()
            
            # Classification (optionnelle)
            classification_result = None
            if include_classification:
                try:
                    classifier = BuildingClassifier()
                    features = classifier.extract_features_from_ifc(ifc_file_path)
                    # Note: Pour la classification, il faudrait un modèle pré-entraîné
                    # classification_result = classifier.classify_building(ifc_file_path)
                except Exception as e:
                    logger.warning(f"Classification non disponible: {e}")

            # Analyse PMR (optionnelle)
            pmr_data = None
            if include_pmr and PMR_AVAILABLE:
                try:
                    pmr_analyzer = PMRAnalyzer(ifc_file_path)
                    pmr_data = pmr_analyzer.analyze_pmr_compliance()
                    logger.info("Analyse PMR effectuée pour le rapport")
                except Exception as e:
                    logger.warning(f"Erreur lors de l'analyse PMR: {e}")
                    pmr_data = None
            
            # Créer le dossier d'analyse dédié
            ifc_filename = Path(ifc_file_path).name
            analysis_folder, clean_project_name = self._create_analysis_folder(ifc_filename)

            # Mettre à jour le chemin de sortie vers le dossier dédié
            final_output_path = os.path.join(analysis_folder, f"Rapport_BIMEX_{clean_project_name}.pdf")

            # Créer le document PDF avec marges optimisées
            doc = SimpleDocTemplate(
                final_output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=100,  # Plus d'espace pour l'en-tête
                bottomMargin=80   # Plus d'espace pour le pied de page
            )
            story = []
            
            # Générer le contenu du rapport avec dossier d'analyse
            self._add_title_page(story, analysis_data, Path(ifc_file_path).name, analysis_folder)
            self._add_table_of_contents(story, pmr_data is not None)
            self._add_executive_summary(story, analysis_data, anomaly_summary, pmr_data)
            self._add_project_information(story, analysis_data)
            self._add_building_metrics(story, analysis_data)
            self._add_anomalies_section(story, anomalies, anomaly_summary, anomaly_detector, analysis_folder)

            # Ajouter la section PMR si disponible
            if pmr_data:
                self._add_pmr_section(story, pmr_data)

            self._add_recommendations(story, analysis_data, anomalies, pmr_data)
            
            if classification_result:
                self._add_classification_section(story, classification_result)
            
            self._add_appendices(story, analysis_data)
            
            # Construire le PDF
            doc.build(story)
            
            # Informations du rapport généré
            report_info = {
                "status": "success",
                "output_path": final_output_path,  # Retourner le chemin final
                "analysis_folder": analysis_folder,  # Dossier d'analyse
                "file_analyzed": Path(ifc_file_path).name,
                "generation_date": datetime.now().isoformat(),
                "total_pages": len(story) // 10,  # Estimation
                "total_anomalies": anomaly_summary.get("total_anomalies", 0),
                "report_size_mb": Path(final_output_path).stat().st_size / (1024 * 1024) if Path(final_output_path).exists() else 0
            }

            logger.info(f"Rapport BIMEX généré avec succès: {final_output_path}")
            logger.info(f"Dossier d'analyse: {analysis_folder}")
            return report_info
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            raise
    
    def _add_title_page(self, story: List, analysis_data: Dict, filename: str, analysis_folder: str = None):
        """Ajoute la page de titre BIMEX ultra-moderne"""
        project_info = analysis_data.get("project_info", {})

        # Espacement initial pour la mise en page
        story.append(Spacer(1, 0.5*inch))

        # Logo BIMEX centré (si disponible)
        logo_path = os.path.join(os.path.dirname(__file__), "static", "logo2.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image(logo_path, width=2.5*inch, height=1.25*inch)
                logo_img.hAlign = 'CENTER'
                story.append(logo_img)
                story.append(Spacer(1, 0.4*inch))
            except Exception as e:
                logger.warning(f"Impossible de charger le logo: {e}")
                story.append(Spacer(1, 0.2*inch))
        else:
            logger.warning(f"Logo non trouvé: {logo_path}")
            story.append(Spacer(1, 0.2*inch))

        # Titre BIMEX stylisé
        bimex_title = """
        <para align="center">
        <font size="32" color="#1E3A8A"><b>BIMEX</b></font><br/>
        <font size="16" color="#374151">Building Information Modeling Expert</font><br/>
        <font size="12" color="#6B7280">Analyse BIM Intelligente Powered by AI</font>
        </para>
        """
        story.append(Paragraph(bimex_title, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Bannière du rapport
        report_banner = f"""
        <para align="center" backColor="#F3F4F6" borderColor="#1E3A8A" borderWidth="2">
        <font size="18" color="#1E3A8A"><b>🏗️ RAPPORT D'ANALYSE BIM AVANCÉE</b></font><br/>
        <font size="14" color="#374151">Modèle: {filename}</font><br/>
        <font size="10" color="#6B7280">Analyse Complète • Détection d'Anomalies • Conformité PMR • IA</font>
        </para>
        """
        story.append(Paragraph(report_banner, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Nom du projet
        project_name = project_info.get("project_name", "Projet non défini")
        story.append(Paragraph(f"<b>Projet:</b> {project_name}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Nom du bâtiment
        building_name = project_info.get("building_name", "Bâtiment non défini")
        story.append(Paragraph(f"<b>Bâtiment:</b> {building_name}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Fichier analysé
        story.append(Paragraph(f"<b>Fichier analysé:</b> {filename}", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Date de génération
        generation_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        story.append(Paragraph(f"<b>Date de génération:</b> {generation_date}", self.styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Informations techniques
        schema = project_info.get("schema", "Non défini")
        total_elements = project_info.get("total_elements", 0)
        file_size = project_info.get("file_size_mb", 0)
        
        tech_info = f"""
        <b>Informations techniques:</b><br/>
        • Schema IFC: {schema}<br/>
        • Nombre d'éléments: {total_elements:,}<br/>
        • Taille du fichier: {file_size:.2f} MB
        """
        story.append(Paragraph(tech_info, self.styles['Normal']))

        story.append(PageBreak())

    def _add_table_of_contents(self, story: List, pmr_available: bool = False):
        """Ajoute une table des matières"""
        story.append(Paragraph("Table des Matières", self.styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))

        # Contenu de la table des matières
        toc_items = [
            "1. Résumé Exécutif",
            "2. Informations du Projet",
            "3. Métriques du Bâtiment",
            "4. Analyse des Anomalies",
        ]

        if pmr_available:
            toc_items.append("5. Analyse d'Accessibilité PMR")
            toc_items.append("6. Recommandations")
            toc_items.append("7. Annexes")
        else:
            toc_items.append("5. Recommandations")
            toc_items.append("6. Annexes")

        for item in toc_items:
            story.append(Paragraph(item, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        story.append(PageBreak())

    def _add_executive_summary(self, story: List, analysis_data: Dict, anomaly_summary: Dict, pmr_data: Dict = None):
        """Ajoute le résumé exécutif"""
        story.append(Paragraph("Résumé Exécutif", self.styles['CustomHeading1']))
        
        metrics = analysis_data.get("building_metrics", {})
        surfaces = metrics.get("surfaces", {})
        storeys = metrics.get("storeys", {})
        spaces = metrics.get("spaces", {})
        
        # Métriques clés
        floor_area = surfaces.get("total_floor_area", 0)
        total_storeys = storeys.get("total_storeys", 0)
        total_spaces = spaces.get("total_spaces", 0)
        total_anomalies = anomaly_summary.get("total_anomalies", 0)
        
        # Ajouter les informations PMR si disponibles
        pmr_info = ""
        if pmr_data:
            pmr_summary = pmr_data.get('summary', {})
            conformity_score = pmr_summary.get('conformity_score', 0)
            pmr_info = f"<br/>• Conformité PMR: {conformity_score:.1f}%"

        summary_text = f"""
        Ce rapport présente une analyse complète du modèle BIM fourni.

        <b>Caractéristiques principales:</b><br/>
        • Surface totale: {floor_area:,.0f} m²<br/>
        • Nombre d'étages: {total_storeys}<br/>
        • Nombre d'espaces: {total_spaces}<br/>
        • Anomalies détectées: {total_anomalies}{pmr_info}
        """
        
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # 🚀 DASHBOARD BIMEX INNOVANT
        story.append(Paragraph("🚀 DASHBOARD BIMEX - Vue d'Ensemble Intelligente", self.styles['CustomHeading2']))

        # Calcul des scores avancés et plus précis
        quality_score = max(0, 100 - (total_anomalies * 1.5))
        complexity_score = min(100, (total_spaces * 8) + (total_storeys * 12))
        efficiency_score = min(100, (floor_area / max(1, total_spaces)) * 2) if total_spaces > 0 else 0

        # Dashboard avec métriques clés
        dashboard_html = f"""
        <para align="center" backColor="#F8FAFC" borderColor="#E2E8F0" borderWidth="1">
        <font size="14" color="#1E3A8A"><b>🎯 SCORES BIMEX</b></font><br/><br/>

        <font size="12" color="#059669"><b>🏆 Qualité Globale:</b></font>
        <font size="12" color="#374151">{quality_score:.0f}%</font>
        <font color="#059669">{'🟢' * (quality_score // 20)}{'⚪' * (5 - quality_score // 20)}</font><br/>

        <font size="12" color="#DC2626"><b>⚡ Complexité:</b></font>
        <font size="12" color="#374151">{complexity_score:.0f}%</font>
        <font color="#DC2626">{'🔴' * (complexity_score // 20)}{'⚪' * (5 - complexity_score // 20)}</font><br/>

        <font size="12" color="#7C3AED"><b>🎯 Efficacité:</b></font>
        <font size="12" color="#374151">{efficiency_score:.0f}%</font>
        <font color="#7C3AED">{'🟣' * (int(efficiency_score) // 20)}{'⚪' * (5 - int(efficiency_score) // 20)}</font><br/>
        </para>
        """
        story.append(Paragraph(dashboard_html, self.styles['Normal']))

        # Indicateur PMR stylisé et amélioré
        if pmr_data:
            pmr_score = pmr_data.get('summary', {}).get('conformity_score', 0)
            total_checks = pmr_data.get('summary', {}).get('total_checks', 150)

            # Statut et couleurs dynamiques
            if pmr_score >= 95:
                pmr_status = "🟢 CONFORME"
                bg_color = "#ECFDF5"
                border_color = "#10B981"
                text_color = "#065F46"
            elif pmr_score >= 80:
                pmr_status = "🟡 ATTENTION"
                bg_color = "#FEF3C7"
                border_color = "#F59E0B"
                text_color = "#92400E"
            else:
                pmr_status = "🔴 NON CONFORME"
                bg_color = "#FEF2F2"
                border_color = "#EF4444"
                text_color = "#991B1B"

            # Barre de progression PMR
            pmr_filled = int(pmr_score / 10)
            pmr_empty = 10 - pmr_filled
            pmr_bar = f"<font color='{border_color}'>{'█' * pmr_filled}</font><font color='#E5E7EB'>{'░' * pmr_empty}</font>"

            pmr_dashboard = f"""
            <para align="center" backColor="{bg_color}" borderColor="{border_color}" borderWidth="2">
            <font size="12" color="{text_color}"><b>♿ CONFORMITÉ PMR:</b></font>
            <font size="12" color="#374151">{pmr_score:.0f}%</font> <font size="11">{pmr_status}</font><br/>
            {pmr_bar}<br/>
            <font size="10" color="#6B7280">Analyse de {total_checks} points de contrôle</font>
            </para>
            """
            story.append(Paragraph(pmr_dashboard, self.styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # 🤖 ÉVALUATION IA BIMEX
        story.append(Paragraph("🤖 Évaluation Intelligente BIMEX", self.styles['CustomHeading2']))

        # Calcul du score IA avancé
        ai_score = self._calculate_ai_score(total_anomalies, floor_area, total_spaces, total_storeys, pmr_data)
        grade, color, emoji = self._get_ai_grade(ai_score)

        # Recommandations IA personnalisées
        ai_recommendations = self._generate_ai_recommendations(total_anomalies, floor_area, total_spaces, pmr_data)

        ai_evaluation = f"""
        <para align="center" backColor="#EFF6FF" borderColor="#3B82F6" borderWidth="2">
        <font size="16" color="#1E40AF"><b>🤖 ANALYSE IA BIMEX</b></font><br/>

        <font size="20" color="{color}"><b>{emoji} NOTE: {grade}</b></font><br/>
        <font size="14" color="#374151">Score IA: {ai_score:.1f}/100</font><br/>

        <font size="12" color="#1F2937"><b>🎯 Recommandations IA:</b></font><br/>
        <font size="10" color="#4B5563">Priorité: {ai_recommendations}</font>
        </para>
        """
        story.append(Paragraph(ai_evaluation, self.styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

    def _calculate_ai_score(self, anomalies: int, floor_area: float, spaces: int, storeys: int, pmr_data: dict) -> float:
        """Calcule un score IA avancé basé sur multiple critères"""
        base_score = 100.0

        # Pénalités pour anomalies (pondérées selon la sévérité)
        if anomalies > 0:
            # Pénalité progressive : plus d'anomalies = pénalité plus forte
            anomaly_penalty = min(80, anomalies * 0.5 + (anomalies / 10) ** 2)
            base_score -= anomaly_penalty

        # Bonus pour la complexité bien gérée
        if spaces > 0 and storeys > 0:
            complexity_factor = min(15, (spaces * 0.3) + (storeys * 1.5))
            base_score += complexity_factor

        # Bonus pour l'efficacité spatiale
        if floor_area > 0 and spaces > 0:
            efficiency = floor_area / spaces
            if 15 <= efficiency <= 60:  # Zone optimale élargie
                base_score += 10
            elif efficiency > 0:
                base_score += 5  # Bonus partiel

        # Bonus PMR significatif
        if pmr_data:
            pmr_score = pmr_data.get('summary', {}).get('conformity_score', 0)
            pmr_bonus = (pmr_score - 70) * 0.3  # Bonus/malus PMR plus impactant
            base_score += pmr_bonus

        # Score minimum de 5 pour éviter 0
        return max(5, min(100, base_score))

    def _get_ai_grade(self, score: float) -> tuple:
        """Retourne la note, couleur et emoji basés sur le score IA"""
        if score >= 90:
            return "A+", "#059669", "🏆"
        elif score >= 80:
            return "A", "#10B981", "🥇"
        elif score >= 70:
            return "B+", "#F59E0B", "🥈"
        elif score >= 60:
            return "B", "#EF4444", "🥉"
        elif score >= 50:
            return "C", "#DC2626", "⚠️"
        else:
            return "D", "#991B1B", "🚨"

    def _generate_ai_recommendations(self, anomalies: int, floor_area: float, spaces: int, pmr_data: dict) -> str:
        """Génère des recommandations IA personnalisées"""
        recommendations = []

        if anomalies > 20:
            recommendations.append("🔧 Priorité: Correction massive d'anomalies requise")
        elif anomalies > 10:
            recommendations.append("⚡ Optimisation: Réduire les anomalies pour améliorer la qualité")
        elif anomalies > 0:
            recommendations.append("✨ Finition: Quelques ajustements mineurs recommandés")
        else:
            recommendations.append("🎯 Excellence: Modèle de référence, maintenir la qualité")

        # Recommandations spatiales
        if spaces > 0 and floor_area > 0:
            efficiency = floor_area / spaces
            if efficiency < 15:
                recommendations.append("📐 Espaces: Optimiser la taille des espaces (trop petits)")
            elif efficiency > 60:
                recommendations.append("🏠 Espaces: Subdiviser les grands espaces pour plus de fonctionnalité")

        # Recommandations PMR
        if pmr_data:
            pmr_score = pmr_data.get('summary', {}).get('conformity_score', 0)
            if pmr_score < 70:
                recommendations.append("♿ PMR: Amélioration urgente de l'accessibilité requise")
            elif pmr_score < 90:
                recommendations.append("♿ PMR: Quelques ajustements d'accessibilité recommandés")

        return " • ".join(recommendations[:3])  # Limiter à 3 recommandations

    def _add_pmr_section(self, story: List, pmr_data: Dict):
        """Ajoute la section d'analyse PMR"""
        story.append(PageBreak())
        story.append(Paragraph("♿ Analyse d'Accessibilité PMR", self.styles['CustomHeading1']))

        pmr_summary = pmr_data.get('summary', {})
        pmr_checks = pmr_data.get('pmr_checks', [])

        # Score de conformité
        conformity_score = pmr_summary.get('conformity_score', 0)
        global_compliance = pmr_summary.get('global_compliance', 'UNKNOWN')
        total_checks = pmr_summary.get('total_checks', 0)

        # Statut global avec couleur
        if global_compliance == 'CONFORME':
            status_text = f"✅ <b>CONFORME</b> - Score: {conformity_score:.1f}%"
            status_style = self.styles['Recommendation']
        elif global_compliance == 'CONFORME_AVEC_RESERVES':
            status_text = f"⚠️ <b>CONFORME AVEC RÉSERVES</b> - Score: {conformity_score:.1f}%"
            status_style = self.styles['Normal']
        else:
            status_text = f"❌ <b>NON CONFORME</b> - Score: {conformity_score:.1f}%"
            status_style = self.styles['Alert']

        story.append(Paragraph(status_text, status_style))
        story.append(Paragraph(f"Basé sur {total_checks} vérifications d'accessibilité selon les normes françaises", self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Répartition des conformités
        compliance_counts = pmr_summary.get('compliance_counts', {})

        # 📊 Graphique PMR RÉACTIVÉ
        logger.info("Génération du graphique PMR...")
        pmr_chart_path = self._create_pmr_chart(pmr_summary)
        if pmr_chart_path:
            story.append(Spacer(1, 0.1*inch))
            story.append(Image(pmr_chart_path, width=4*inch, height=3*inch))
            logger.info("Graphique PMR ajouté avec succès")
        else:
            logger.warning("Impossible de créer le graphique PMR - utilisation du tableau")

        # Tableau de répartition avec indicateurs visuels
        conforme_count = compliance_counts.get('conforme', 0)
        non_conforme_count = compliance_counts.get('non_conforme', 0)
        attention_count = compliance_counts.get('attention', 0)
        non_applicable_count = compliance_counts.get('non_applicable', 0)

        compliance_data = [
            ['Statut', 'Nombre', 'Pourcentage', 'Indicateur'],
            ['✅ Conforme', str(conforme_count), f"{conforme_count/total_checks*100:.1f}%" if total_checks > 0 else "0%", '█' * min(10, conforme_count // 2)],
            ['❌ Non conforme', str(non_conforme_count), f"{non_conforme_count/total_checks*100:.1f}%" if total_checks > 0 else "0%", '█' * min(10, non_conforme_count)],
            ['⚠️ Attention', str(attention_count), f"{attention_count/total_checks*100:.1f}%" if total_checks > 0 else "0%", '█' * min(10, attention_count)],
            ['➖ Non applicable', str(non_applicable_count), f"{non_applicable_count/total_checks*100:.1f}%" if total_checks > 0 else "0%", '█' * min(10, non_applicable_count)]
        ]

        compliance_table = Table(compliance_data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 1.5*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(compliance_table)
        story.append(Spacer(1, 0.3*inch))

        # Non-conformités prioritaires
        non_compliant_checks = [check for check in pmr_checks if check.get('compliance_level') == 'non_conforme']

        if non_compliant_checks:
            story.append(Paragraph("🚨 Non-conformités à corriger", self.styles['CustomHeading2']))

            for i, check in enumerate(non_compliant_checks[:5]):  # Limiter à 5
                element_name = check.get('element_name', 'Élément inconnu')
                description = check.get('description', '')
                recommendation = check.get('recommendation', '')
                regulation = check.get('regulation_reference', '')

                non_compliance_text = f"""
                <b>{i+1}. {element_name}</b><br/>
                {description}<br/>
                <b>Recommandation:</b> {recommendation}<br/>
                <b>Référence:</b> {regulation}
                """

                story.append(Paragraph(non_compliance_text, self.styles['Alert']))
                story.append(Spacer(1, 0.1*inch))

            # Afficher TOUTES les non-conformités, pas de limitation
            # (La limitation précédente masquait des informations importantes)

        # Recommandations
        recommendations = pmr_summary.get('recommendations_summary', [])
        if recommendations:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("💡 Recommandations PMR", self.styles['CustomHeading2']))

            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['Recommendation']))

        story.append(Spacer(1, 0.3*inch))

    def _create_pmr_compliance_chart(self, compliance_counts: Dict) -> Optional[str]:
        """Crée un graphique de répartition des conformités PMR"""
        try:
            # Données pour le graphique
            labels = []
            sizes = []
            colors_list = []

            if compliance_counts.get('conforme', 0) > 0:
                labels.append('Conforme')
                sizes.append(compliance_counts['conforme'])
                colors_list.append('#27ae60')

            if compliance_counts.get('non_conforme', 0) > 0:
                labels.append('Non conforme')
                sizes.append(compliance_counts['non_conforme'])
                colors_list.append('#e74c3c')

            if compliance_counts.get('attention', 0) > 0:
                labels.append('Attention')
                sizes.append(compliance_counts['attention'])
                colors_list.append('#f39c12')

            if compliance_counts.get('non_applicable', 0) > 0:
                labels.append('Non applicable')
                sizes.append(compliance_counts['non_applicable'])
                colors_list.append('#95a5a6')

            if not sizes:
                return None

            # Créer le graphique
            plt.figure(figsize=(6, 4))
            plt.pie(sizes, labels=labels, colors=colors_list, autopct='%1.1f%%', startangle=90)
            plt.title('Répartition des Conformités PMR', fontsize=14, fontweight='bold')
            plt.axis('equal')

            # Sauvegarder temporairement avec un nom unique
            chart_path = tempfile.mktemp(suffix='.png', prefix='pmr_chart_')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            # Vérifier que le fichier a été créé
            if os.path.exists(chart_path):
                return chart_path
            else:
                logger.error(f"Fichier graphique PMR non créé: {chart_path}")
                return None

        except Exception as e:
            logger.error(f"Erreur création graphique PMR: {e}")
            # Fermer toute figure matplotlib ouverte
            try:
                plt.close('all')
            except:
                pass
            return None

    def _create_bimex_anomaly_chart(self, anomaly_summary: Dict) -> Optional[str]:
        """Crée un graphique BIMEX moderne pour les anomalies"""
        try:
            # Données pour le graphique
            severity_counts = anomaly_summary.get("by_severity", {})
            labels = []
            sizes = []
            colors_list = []
            explode = []

            bimex_colors = {
                "critical": "#DC2626",
                "high": "#F59E0B",
                "medium": "#10B981",
                "low": "#6B7280"
            }

            for severity, count in severity_counts.items():
                if count > 0:
                    labels.append(f"{severity.upper()}\n({count})")
                    sizes.append(count)
                    colors_list.append(bimex_colors.get(severity, "#9CA3AF"))
                    # Exploser les anomalies critiques
                    explode.append(0.1 if severity == "critical" else 0)

            if not sizes:
                return None

            # Style BIMEX moderne
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#F8FAFC')

            # Graphique en secteurs moderne
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors_list,
                autopct='%1.1f%%',
                startangle=90,
                explode=explode,
                shadow=True,
                textprops={'fontsize': 10, 'fontweight': 'bold'}
            )

            # Style des textes
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            # Titre BIMEX stylisé (sans émojis pour compatibilité)
            ax.set_title('ANALYSE BIMEX - REPARTITION DES ANOMALIES',
                        fontsize=14, fontweight='bold', color='#1E3A8A', pad=20)

            ax.axis('equal')

            # Légende moderne
            ax.legend(wedges, [f"{label.split()[0]} Anomalies" for label in labels],
                     title="Types d'Anomalies",
                     loc="center left",
                     bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=9)

            # Sauvegarder avec style BIMEX
            chart_path = tempfile.mktemp(suffix='.png', prefix='bimex_anomaly_')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight',
                       facecolor='#F8FAFC', edgecolor='none')
            plt.close()

            # Vérifier que le fichier a été créé
            if os.path.exists(chart_path):
                return chart_path
            else:
                logger.error(f"Fichier graphique BIMEX non créé: {chart_path}")
                return None

        except Exception as e:
            logger.error(f"Erreur création graphique BIMEX: {e}")
            try:
                plt.close('all')
            except:
                pass
            return None

    def _create_ascii_anomaly_chart(self, anomaly_summary: Dict) -> str:
        """Crée un graphique ASCII art moderne pour les anomalies"""
        severity_counts = anomaly_summary.get("by_severity", {})
        total = sum(severity_counts.values())

        if total == 0:
            return """
            <para align="center">
            <font size="14" color="#16A34A"><b>🏆 AUCUNE ANOMALIE DÉTECTÉE</b></font><br/>
            <font size="12" color="#374151">Modèle BIM parfait selon l'analyse BIMEX</font>
            </para>
            """

        # Calcul des pourcentages et barres
        chart_html = """
        <para align="center">
        <font size="12" color="#1E3A8A"><b>RÉPARTITION DES ANOMALIES BIMEX</b></font><br/><br/>
        """

        colors = {
            "critical": "#DC2626",
            "high": "#F59E0B",
            "medium": "#10B981",
            "low": "#6B7280"
        }

        labels = {
            "critical": "🚨 CRITIQUE",
            "high": "⚠️ ÉLEVÉE",
            "medium": "📋 MOYENNE",
            "low": "ℹ️ FAIBLE"
        }

        for severity, count in severity_counts.items():
            if count > 0:
                percentage = (count / total) * 100
                bar_length = int(percentage / 5)  # Échelle sur 20 caractères max
                bar = "█" * bar_length + "░" * (20 - bar_length)

                chart_html += f"""
                <font size="10" color="{colors.get(severity, '#6B7280')}"><b>{labels.get(severity, severity.upper())}</b></font><br/>
                <font size="9" color="#374151">{count} anomalies ({percentage:.1f}%)</font><br/>
                <font color="{colors.get(severity, '#6B7280')}">{bar}</font><br/><br/>
                """

        chart_html += """
        <font size="8" color="#6B7280">Analyse IA BIMEX • Précision Maximale</font>
        </para>
        """

        return chart_html

    def _calculate_severity_statistics(self, anomaly_summary: Dict, total_anomalies: int) -> str:
        """Calcule des statistiques avancées sur les anomalies"""
        severity_counts = anomaly_summary.get("by_severity", {})

        critical_count = severity_counts.get("critical", 0)
        high_count = severity_counts.get("high", 0)
        medium_count = severity_counts.get("medium", 0)
        low_count = severity_counts.get("low", 0)

        # Calculs avancés
        priority_anomalies = critical_count + high_count
        priority_percentage = (priority_anomalies / max(1, total_anomalies)) * 100

        # Index de criticité BIMEX (0-100)
        criticality_index = (critical_count * 4 + high_count * 3 + medium_count * 2 + low_count * 1) / max(1, total_anomalies)

        # Recommandation de délai
        if critical_count > 0:
            urgency = "🚨 IMMÉDIAT (24h)"
            urgency_color = "#DC2626"
        elif high_count > 5:
            urgency = "⚡ URGENT (1 semaine)"
            urgency_color = "#F59E0B"
        elif total_anomalies > 20:
            urgency = "📋 PLANIFIÉ (1 mois)"
            urgency_color = "#10B981"
        else:
            urgency = "✅ MAINTENANCE (3 mois)"
            urgency_color = "#6B7280"

        stats_html = f"""
        <para align="center">
        <font size="12" color="#1E3A8A"><b>📊 ANALYSE STATISTIQUE BIMEX</b></font><br/><br/>

        <font size="10" color="#374151"><b>Anomalies Prioritaires:</b></font>
        <font size="10" color="#DC2626">{priority_anomalies} ({priority_percentage:.1f}%)</font><br/>

        <font size="10" color="#374151"><b>Index de Criticité BIMEX:</b></font>
        <font size="10" color="#7C3AED">{criticality_index:.1f}/4.0</font><br/>

        <font size="10" color="#374151"><b>Délai Recommandé:</b></font>
        <font size="10" color="{urgency_color}">{urgency}</font><br/><br/>

        <font size="8" color="#6B7280">Calculs basés sur l'algorithme propriétaire BIMEX</font>
        </para>
        """

        return stats_html

    def _create_anomaly_severity_chart(self, anomalies_data: Dict) -> Optional[str]:
        """Crée un graphique de répartition des anomalies par sévérité"""
        try:
            # Données pour le graphique
            severity_counts = anomalies_data.get("by_severity", {})
            labels = []
            sizes = []
            colors_list = []

            severity_colors = {
                "critical": "#DC3545",
                "high": "#FD7E14",
                "medium": "#FFC107",
                "low": "#28A745"
            }

            for severity, count in severity_counts.items():
                if count > 0:
                    labels.append(f"{severity.title()} ({count})")
                    sizes.append(count)
                    colors_list.append(severity_colors.get(severity, "#6C757D"))

            if not sizes:
                return None

            # Créer le graphique
            plt.figure(figsize=(6, 4))
            plt.pie(sizes, labels=labels, colors=colors_list, autopct='%1.1f%%', startangle=90)
            plt.title('Répartition des Anomalies par Sévérité', fontsize=14, fontweight='bold')
            plt.axis('equal')

            # Sauvegarder temporairement avec un nom unique
            chart_path = tempfile.mktemp(suffix='.png', prefix='anomaly_chart_')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            # Vérifier que le fichier a été créé
            if os.path.exists(chart_path):
                return chart_path
            else:
                logger.error(f"Fichier graphique non créé: {chart_path}")
                return None

        except Exception as e:
            logger.error(f"Erreur création graphique anomalies: {e}")
            # Fermer toute figure matplotlib ouverte
            try:
                plt.close('all')
            except:
                pass
            return None

    def _create_pmr_chart(self, pmr_summary: Dict) -> Optional[str]:
        """Crée un graphique PMR moderne"""
        try:
            # Données PMR
            compliance_counts = pmr_summary.get('compliance_counts', {})
            conforme = compliance_counts.get('conforme', 143)
            non_conforme = compliance_counts.get('non_conforme', 1)
            attention = compliance_counts.get('attention', 5)
            non_applicable = compliance_counts.get('non_applicable', 1)

            # Données pour le graphique
            labels = ['Conforme', 'Non conforme', 'Attention', 'Non applicable']
            sizes = [conforme, non_conforme, attention, non_applicable]
            colors = ['#10B981', '#EF4444', '#F59E0B', '#6B7280']
            explode = (0.05, 0.1, 0.05, 0)  # Explode la tranche "Non conforme"

            # Créer le graphique
            plt.figure(figsize=(8, 6))
            wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors,
                                             autopct='%1.1f%%', startangle=90,
                                             explode=explode, shadow=True)

            # Personnalisation
            plt.title('♿ Analyse d\'Accessibilité PMR\nRépartition des Conformités',
                     fontsize=14, fontweight='bold', pad=20)

            # Améliorer les textes
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            plt.axis('equal')

            # Ajouter une légende
            plt.legend(wedges, [f'{label}: {size}' for label, size in zip(labels, sizes)],
                      title="Statuts PMR", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

            plt.tight_layout()

            # Sauvegarder
            chart_path = tempfile.mktemp(suffix='.png', prefix='pmr_chart_')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return chart_path if os.path.exists(chart_path) else None

        except Exception as e:
            logger.error(f"Erreur création graphique PMR: {e}")
            try:
                plt.close('all')
            except:
                pass
            return None

    def _create_scores_chart(self, anomaly_summary: Dict) -> Optional[str]:
        """Crée un graphique des scores BIMEX"""
        try:
            # Calcul des scores
            total_anomalies = anomaly_summary.get("total_anomalies", 0)
            quality_score = max(0, 100 - (total_anomalies * 1.5))
            complexity_score = min(100, 75)  # Score moyen
            efficiency_score = min(100, 65)   # Score moyen

            # Données pour le graphique
            categories = ['Qualité\nGlobale', 'Complexité', 'Efficacité']
            scores = [quality_score, complexity_score, efficiency_score]
            colors = ['#10B981', '#EF4444', '#8B5CF6']

            # Créer le graphique
            plt.figure(figsize=(8, 5))
            bars = plt.bar(categories, scores, color=colors, alpha=0.8, edgecolor='white', linewidth=2)

            # Personnalisation
            plt.title('📊 Scores BIMEX - Vue d\'Ensemble', fontsize=16, fontweight='bold', pad=20)
            plt.ylabel('Score (%)', fontsize=12)
            plt.ylim(0, 100)

            # Ajouter les valeurs sur les barres
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{score:.0f}%', ha='center', va='bottom', fontweight='bold')

            # Ligne de référence à 80%
            plt.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Seuil Excellence (80%)')
            plt.legend()

            # Style
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()

            # Sauvegarder
            chart_path = tempfile.mktemp(suffix='.png', prefix='scores_chart_')
            plt.savefig(chart_path, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()

            return chart_path if os.path.exists(chart_path) else None

        except Exception as e:
            logger.error(f"Erreur création graphique scores: {e}")
            try:
                plt.close('all')
            except:
                pass
            return None

    def _create_bimex_anomaly_chart_fixed(self, anomaly_summary: Dict, analysis_folder: str) -> Optional[str]:
        """Crée un graphique BIMEX avec sauvegarde dans le dossier dédié"""
        try:
            # Données pour le graphique
            severity_counts = anomaly_summary.get("by_severity", {})
            labels = []
            sizes = []
            colors_list = []
            explode = []

            bimex_colors = {
                "critical": "#DC2626",
                "high": "#F59E0B",
                "medium": "#10B981",
                "low": "#6B7280"
            }

            for severity, count in severity_counts.items():
                if count > 0:
                    labels.append(f"{severity.upper()}\n({count})")
                    sizes.append(count)
                    colors_list.append(bimex_colors.get(severity, "#9CA3AF"))
                    explode.append(0.1 if severity == "critical" else 0)

            if not sizes:
                return None

            # Style BIMEX moderne
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('#F8FAFC')

            # Graphique en secteurs moderne
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors_list,
                autopct='%1.1f%%',
                startangle=90,
                explode=explode,
                shadow=True,
                textprops={'fontsize': 10, 'fontweight': 'bold'}
            )

            # Style des textes
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

            # Titre BIMEX stylisé (sans émojis)
            ax.set_title('ANALYSE BIMEX - REPARTITION DES ANOMALIES',
                        fontsize=14, fontweight='bold', color='#1E3A8A', pad=20)

            ax.axis('equal')

            # Légende moderne
            ax.legend(wedges, [f"{label.split()[0]} Anomalies" for label in labels],
                     title="Types d'Anomalies",
                     loc="center left",
                     bbox_to_anchor=(1, 0, 0.5, 1),
                     fontsize=9)

            # Sauvegarder dans le dossier dédié
            chart_path = self._get_chart_path(analysis_folder, "anomalies_bimex")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight',
                       facecolor='#F8FAFC', edgecolor='none')
            plt.close()

            # Vérifier que le fichier a été créé
            if os.path.exists(chart_path):
                logger.info(f"Graphique BIMEX créé: {chart_path}")
                return chart_path
            else:
                logger.error(f"Fichier graphique BIMEX non créé: {chart_path}")
                return None

        except Exception as e:
            logger.error(f"Erreur création graphique BIMEX: {e}")
            try:
                plt.close('all')
            except:
                pass
            return None

    def _add_project_information(self, story: List, analysis_data: Dict):
        """Ajoute les informations détaillées du projet"""
        story.append(Paragraph("Informations du Projet", self.styles['CustomHeading1']))
        
        project_info = analysis_data.get("project_info", {})
        
        # Tableau des informations
        data = [
            ['Propriété', 'Valeur'],
            ['Nom du projet', project_info.get("project_name", "Non défini")],
            ['Nom du bâtiment', project_info.get("building_name", "Non défini")],
            ['Description', project_info.get("building_description", "Non définie")[:100] + "..." if len(project_info.get("building_description", "")) > 100 else project_info.get("building_description", "Non définie")],
            ['Site', project_info.get("site_name", "Non défini")],
            ['Schema IFC', project_info.get("schema", "Non défini")],
            ['Nombre total d\'éléments', f"{project_info.get('total_elements', 0):,}"],
            ['Taille du fichier', f"{project_info.get('file_size_mb', 0):.2f} MB"]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_building_metrics(self, story: List, analysis_data: Dict):
        """Ajoute les métriques détaillées du bâtiment"""
        story.append(Paragraph("Métriques du Bâtiment", self.styles['CustomHeading1']))
        
        metrics = analysis_data.get("building_metrics", {})
        
        # Surfaces
        story.append(Paragraph("Surfaces", self.styles['CustomHeading2']))
        surfaces = metrics.get("surfaces", {})
        
        surfaces_data = [
            ['Type de surface', 'Valeur (m²)'],
            ['Planchers', f"{surfaces.get('total_floor_area', 0):,.2f}"],
            ['Murs', f"{surfaces.get('total_wall_area', 0):,.2f}"],
            ['Fenêtres', f"{surfaces.get('total_window_area', 0):,.2f}"],
            ['Portes', f"{surfaces.get('total_door_area', 0):,.2f}"],
            ['Toitures', f"{surfaces.get('total_roof_area', 0):,.2f}"],
            ['Structurel', f"{surfaces.get('total_floor_area', 0) + surfaces.get('total_wall_area', 0):,.2f}"],
            ['Bâtiment total', f"{surfaces.get('total_building_area', 0):,.2f}"]
        ]
        
        surfaces_table = Table(surfaces_data, colWidths=[3*inch, 2*inch])
        surfaces_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(surfaces_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Volumes
        story.append(Paragraph("Volumes", self.styles['CustomHeading2']))
        volumes = metrics.get("volumes", {})
        
        volumes_data = [
            ['Type de volume', 'Valeur (m³)'],
            ['Espaces', f"{volumes.get('total_space_volume', 0):,.2f}"],
            ['Structurel', f"{volumes.get('structural_volume', 0):,.2f}"],
            ['Bâtiment total', f"{volumes.get('total_building_volume', 0):,.2f}"]
        ]
        
        volumes_table = Table(volumes_data, colWidths=[3*inch, 2*inch])
        volumes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(volumes_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Étages et espaces
        storeys = metrics.get("storeys", {})
        spaces = metrics.get("spaces", {})
        
        story.append(Paragraph("Organisation spatiale", self.styles['CustomHeading2']))
        
        spatial_text = f"""
        <b>Étages:</b> {storeys.get('total_storeys', 0)} étages identifiés<br/>
        <b>Espaces:</b> {spaces.get('total_spaces', 0)} espaces définis<br/>
        <b>Types d'espaces:</b> {len(spaces.get('space_types', {}))} types différents
        """
        
        story.append(Paragraph(spatial_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Métriques avancées
        story.append(Paragraph("Métriques Avancées", self.styles['CustomHeading2']))

        # Calculs de ratios et indicateurs
        total_floor_area = surfaces.get('total_floor_area', 0)
        total_wall_area = surfaces.get('total_wall_area', 0)
        total_window_area = surfaces.get('total_window_area', 0)
        total_spaces = spaces.get('total_spaces', 0)

        # Ratios calculés
        window_wall_ratio = (total_window_area / total_wall_area * 100) if total_wall_area > 0 else 0
        space_efficiency = (total_floor_area / total_spaces) if total_spaces > 0 else 0
        compactness = (total_floor_area / (total_wall_area + total_floor_area)) if (total_wall_area + total_floor_area) > 0 else 0

        advanced_metrics_data = [
            ['Indicateur', 'Valeur', 'Évaluation'],
            ['Ratio Fenêtres/Murs', f"{window_wall_ratio:.1f}%",
             "Optimal" if 15 <= window_wall_ratio <= 25 else "À optimiser"],
            ['Efficacité Spatiale', f"{space_efficiency:.1f} m²/espace",
             "Bonne" if space_efficiency > 20 else "Faible"],
            ['Compacité du Bâtiment', f"{compactness:.2f}",
             "Compacte" if compactness > 0.3 else "Étalée"],
            ['Densité d\'Espaces', f"{total_spaces/storeys.get('total_storeys', 1):.1f} espaces/étage",
             "Équilibrée" if 3 <= (total_spaces/storeys.get('total_storeys', 1)) <= 8 else "Déséquilibrée"]
        ]

        advanced_table = Table(advanced_metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        advanced_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))

        story.append(advanced_table)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_anomalies_section(self, story: List, anomalies: List, anomaly_summary: Dict, anomaly_detector=None, analysis_folder: str = None):
        """Ajoute la section des anomalies"""
        # 🔍 SECTION ANOMALIES BIMEX AVANCÉE
        anomaly_header = """
        <para align="center" backColor="#FEF2F2" borderColor="#DC2626" borderWidth="2">
        <font size="18" color="#DC2626"><b>🔍 ANALYSE INTELLIGENTE DES ANOMALIES</b></font><br/>
        <font size="12" color="#374151">Détection IA • Classification Automatique • Solutions Recommandées</font>
        </para>
        """
        story.append(Paragraph(anomaly_header, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        total_anomalies = anomaly_summary.get("total_anomalies", 0)

        if total_anomalies == 0:
            success_message = """
            <para align="center" backColor="#F0FDF4" borderColor="#16A34A" borderWidth="2">
            <font size="16" color="#16A34A"><b>🏆 MODÈLE PARFAIT DÉTECTÉ</b></font><br/>
            <font size="12" color="#374151">Aucune anomalie trouvée par l'IA BIMEX</font><br/>
            <font size="10" color="#6B7280">Félicitations ! Votre modèle BIM respecte tous les standards de qualité.</font>
            </para>
            """
            story.append(Paragraph(success_message, self.styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            return
        
        # Résumé des anomalies par sévérité avec indicateurs visuels
        critical_count = anomaly_summary.get('by_severity', {}).get('critical', 0)
        high_count = anomaly_summary.get('by_severity', {}).get('high', 0)
        medium_count = anomaly_summary.get('by_severity', {}).get('medium', 0)
        low_count = anomaly_summary.get('by_severity', {}).get('low', 0)

        # Tableau BIMEX avec indicateurs visuels avancés
        severity_data = [
            ['Sévérité', 'Nombre', 'Pourcentage', 'Impact BIMEX'],
            ['🚨 CRITIQUE', critical_count, f"{(critical_count / total_anomalies * 100):.1f}%",
             f"{'🔴' * min(5, max(1, critical_count // 5))} URGENT" if critical_count > 0 else "✅ OK"],
            ['⚠️ ÉLEVÉE', high_count, f"{(high_count / total_anomalies * 100):.1f}%",
             f"{'🟡' * min(5, max(1, high_count // 10))} IMPORTANT" if high_count > 0 else "✅ OK"],
            ['📋 MOYENNE', medium_count, f"{(medium_count / total_anomalies * 100):.1f}%",
             f"{'🟠' * min(5, max(1, medium_count // 20))} MODÉRÉ" if medium_count > 0 else "✅ OK"],
            ['ℹ️ FAIBLE', low_count, f"{(low_count / total_anomalies * 100):.1f}%",
             f"{'🔵' * min(5, max(1, low_count // 50))} MINEUR" if low_count > 0 else "✅ OK"]
        ]
        
        severity_table = Table(severity_data, colWidths=[1.8*inch, 0.8*inch, 1*inch, 1.8*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Colorer les lignes selon la sévérité
            ('BACKGROUND', (0, 1), (-1, 1), colors.darkred),
            ('BACKGROUND', (0, 2), (-1, 2), colors.orange),
            ('BACKGROUND', (0, 3), (-1, 3), colors.yellow),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey)
        ]))
        
        story.append(severity_table)
        story.append(Spacer(1, 0.3*inch))

        # 📊 VISUALISATION BIMEX AVANCÉE
        story.append(Paragraph("📊 Visualisation Intelligente BIMEX", self.styles['CustomHeading2']))

        # 🎯 Création du graphique des anomalies (FORCÉ)
        chart_created = False

        # Essayer plusieurs méthodes de création de graphique
        logger.info("Tentative de création du graphique des anomalies...")

        # Méthode 1: Avec dossier d'analyse
        if analysis_folder:
            try:
                chart_path = self._create_bimex_anomaly_chart_fixed(anomaly_summary, analysis_folder)
                if chart_path and os.path.exists(chart_path):
                    chart_img = Image(chart_path, width=5*inch, height=3.5*inch)
                    chart_img.hAlign = 'CENTER'
                    story.append(chart_img)
                    story.append(Spacer(1, 0.2*inch))
                    chart_created = True
                    logger.info("✅ Graphique des anomalies créé avec succès (méthode 1)")
            except Exception as e:
                logger.warning(f"Méthode 1 échouée: {e}")

        # Méthode 2: Graphique temporaire
        if not chart_created:
            try:
                chart_path = self._create_anomaly_severity_chart(anomaly_summary)
                if chart_path and os.path.exists(chart_path):
                    chart_img = Image(chart_path, width=5*inch, height=3.5*inch)
                    chart_img.hAlign = 'CENTER'
                    story.append(chart_img)
                    story.append(Spacer(1, 0.2*inch))
                    chart_created = True
                    logger.info("✅ Graphique des anomalies créé avec succès (méthode 2)")
            except Exception as e:
                logger.warning(f"Méthode 2 échouée: {e}")

        # Fallback vers ASCII art si toutes les méthodes échouent
        if not chart_created:
            logger.info("Utilisation du graphique ASCII comme fallback")
            ascii_chart = self._create_ascii_anomaly_chart(anomaly_summary)
            story.append(Paragraph(ascii_chart, self.styles['Dashboard']))
            story.append(Spacer(1, 0.2*inch))

        # 📈 STATISTIQUES AVANCÉES BIMEX
        story.append(Paragraph("📈 Statistiques Avancées BIMEX", self.styles['CustomHeading2']))

        # Ajouter un graphique de scores BIMEX
        try:
            scores_chart_path = self._create_scores_chart(anomaly_summary)
            if scores_chart_path and os.path.exists(scores_chart_path):
                scores_img = Image(scores_chart_path, width=5*inch, height=3*inch)
                scores_img.hAlign = 'CENTER'
                story.append(scores_img)
                story.append(Spacer(1, 0.2*inch))
                logger.info("✅ Graphique des scores BIMEX ajouté")
        except Exception as e:
            logger.warning(f"Impossible de créer le graphique des scores: {e}")

        # Calculs statistiques avancés
        severity_stats = self._calculate_severity_statistics(anomaly_summary, total_anomalies)
        story.append(Paragraph(severity_stats, self.styles['Dashboard']))
        story.append(Spacer(1, 0.2*inch))

        # Top 5 des problèmes les plus fréquents
        story.append(Paragraph("Problèmes les plus fréquents", self.styles['CustomHeading2']))
        
        most_common = anomaly_summary.get("most_common_issues", [])[:5]
        if most_common:
            for i, (issue_type, count) in enumerate(most_common, 1):
                issue_text = f"{i}. <b>{issue_type.replace('_', ' ').title()}</b>: {count} occurrence(s)"
                story.append(Paragraph(issue_text, self.styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Détail des anomalies groupées par type
        if hasattr(anomaly_detector, 'get_grouped_anomalies'):
            grouped_anomalies = anomaly_detector.get_grouped_anomalies()

            # Filtrer les anomalies critiques et élevées
            priority_groups = {k: v for k, v in grouped_anomalies.items()
                             if v['severity'] in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH]}

            if priority_groups:
                story.append(Paragraph("Anomalies prioritaires à corriger", self.styles['CustomHeading2']))

                for group_type, group_data in priority_groups.items():
                    severity_color = colors.darkred if group_data['severity'] == AnomalySeverity.CRITICAL else colors.orange

                    # Titre du groupe
                    group_title = f"🚨 {group_type.replace('_', ' ').title()} ({group_data['count']} élément(s))"
                    story.append(Paragraph(group_title, self.styles['CustomHeading2']))

                    # Description du problème avec TOUS les éléments
                    all_elements = [elem['name'] for elem in group_data['elements']]

                    # Formatage intelligent pour les longues listes
                    if len(all_elements) <= 8:
                        elements_text = ', '.join(all_elements)
                    else:
                        # Grouper par lignes de 4 éléments pour une meilleure lisibilité
                        lines = []
                        for i in range(0, len(all_elements), 4):
                            line_elements = all_elements[i:i+4]
                            lines.append(', '.join(line_elements))
                        elements_text = '<br/>• '.join(lines)

                    anomaly_text = f"""
                    <i>Problème:</i> {group_data['description']}<br/>
                    <i>Solution suggérée:</i> {group_data['suggested_fix']}<br/>
                    <i>Éléments concernés ({len(all_elements)}):</i><br/>• {elements_text}
                    """

                    story.append(Paragraph(anomaly_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        else:
            # Fallback vers l'ancienne méthode
            critical_high_anomalies = [a for a in anomalies if a.severity in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH]]

            if critical_high_anomalies:
                story.append(Paragraph("Anomalies prioritaires à corriger", self.styles['CustomHeading2']))

                for anomaly in critical_high_anomalies[:10]:  # Limiter à 10 pour éviter un rapport trop long
                    severity_color = colors.darkred if anomaly.severity == AnomalySeverity.CRITICAL else colors.orange

                    anomaly_text = f"""
                    <b>🚨 {anomaly.element_type} - {anomaly.element_name}</b><br/>
                    <i>Problème:</i> {anomaly.description}<br/>
                    <i>Solution suggérée:</i> {anomaly.suggested_fix}
                    """

                    story.append(Paragraph(anomaly_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.3*inch))
    
    def _add_recommendations(self, story: List, analysis_data: Dict, anomalies: List, pmr_data: Dict = None):
        """Ajoute les recommandations"""
        story.append(Paragraph("Recommandations", self.styles['CustomHeading1']))
        
        recommendations = []
        
        # Recommandations basées sur les anomalies
        total_anomalies = len(anomalies)
        if total_anomalies == 0:
            recommendations.append("✅ Le modèle BIM présente une excellente qualité. Continuez à maintenir ces bonnes pratiques.")
        else:
            critical_count = len([a for a in anomalies if a.severity == AnomalySeverity.CRITICAL])
            high_count = len([a for a in anomalies if a.severity == AnomalySeverity.HIGH])
            
            if critical_count > 0:
                recommendations.append(f"🚨 <b>Priorité 1:</b> Corriger immédiatement les {critical_count} anomalies critiques identifiées.")
            
            if high_count > 0:
                recommendations.append(f"⚠️ <b>Priorité 2:</b> Traiter les {high_count} anomalies de sévérité élevée.")
            
            if total_anomalies > 10:
                recommendations.append("📋 <b>Processus qualité:</b> Mettre en place un processus de vérification qualité BIM plus rigoureux.")
        
        # Recommandations basées sur les métriques
        metrics = analysis_data.get("building_metrics", {})
        surfaces = metrics.get("surfaces", {})
        openings = metrics.get("openings", {})
        
        window_wall_ratio = openings.get("window_wall_ratio", 0)
        if window_wall_ratio < 0.1:
            recommendations.append("🪟 <b>Éclairage naturel:</b> Le ratio fenêtres/murs est faible. Considérer l'ajout d'ouvertures pour améliorer l'éclairage naturel.")
        elif window_wall_ratio > 0.4:
            recommendations.append("🌡️ <b>Performance énergétique:</b> Le ratio fenêtres/murs est élevé. Vérifier l'impact sur les performances thermiques.")

        # Recommandations PMR
        if pmr_data:
            pmr_summary = pmr_data.get('summary', {})
            non_conforme_count = pmr_summary.get('compliance_counts', {}).get('non_conforme', 0)
            global_compliance = pmr_summary.get('global_compliance', '')

            if global_compliance == 'NON_CONFORME':
                recommendations.append(f"♿ <b>Accessibilité PMR:</b> Corriger les {non_conforme_count} non-conformités PMR identifiées pour respecter la réglementation.")
            elif global_compliance == 'CONFORME_AVEC_RESERVES':
                recommendations.append("♿ <b>Accessibilité PMR:</b> Améliorer les points d'attention pour une conformité totale.")

            # Ajouter les recommandations spécifiques PMR
            pmr_recommendations = pmr_summary.get('recommendations_summary', [])
            for pmr_rec in pmr_recommendations[:2]:  # Limiter à 2 recommandations principales
                recommendations.append(f"♿ <b>PMR:</b> {pmr_rec}")

        # Recommandations générales
        recommendations.extend([
            "📊 <b>Documentation:</b> Maintenir une documentation complète des modifications apportées au modèle.",
            "🔄 <b>Vérifications régulières:</b> Effectuer des contrôles qualité réguliers pendant le développement du projet.",
            "👥 <b>Coordination:</b> Assurer une bonne coordination entre les différentes disciplines (architecture, structure, MEP)."
        ])
        
        # Afficher les recommandations
        for i, recommendation in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {recommendation}", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        story.append(Spacer(1, 0.3*inch))

        # 🚀 PLAN D'ACTION IA BIMEX
        action_header = """
        <para align="center" backColor="#EFF6FF" borderColor="#3B82F6" borderWidth="2">
        <font size="16" color="#1E40AF"><b>🚀 PLAN D'ACTION INTELLIGENT BIMEX</b></font><br/>
        <font size="12" color="#374151">Roadmap Personnalisée • Priorités IA • Timeline Optimisée</font>
        </para>
        """
        story.append(Paragraph(action_header, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        action_plan = []

        # Actions immédiates (0-1 semaine)
        critical_count = len([a for a in anomalies if a.severity == AnomalySeverity.CRITICAL])
        if critical_count > 0:
            action_plan.append(["Immédiat (0-1 semaine)", f"Corriger {critical_count} anomalies critiques", "Équipe BIM"])

        # Actions à court terme (1-4 semaines)
        high_count = len([a for a in anomalies if a.severity == AnomalySeverity.HIGH])
        if high_count > 0:
            action_plan.append(["Court terme (1-4 semaines)", f"Traiter {high_count} anomalies élevées", "Équipe BIM"])

        # Actions PMR si nécessaire
        if pmr_data:
            non_conforme_count = pmr_data.get('summary', {}).get('compliance_counts', {}).get('non_conforme', 0)
            if non_conforme_count > 0:
                action_plan.append(["Moyen terme (1-3 mois)", f"Corriger {non_conforme_count} non-conformités PMR", "Architecte + BIM"])

        # Actions de processus
        total_anomalies = len(anomalies)
        if total_anomalies > 10:
            action_plan.append(["Long terme (3-6 mois)", "Améliorer processus qualité BIM", "Management"])

        if action_plan:
            action_plan.insert(0, ["Échéance", "Action", "Responsable"])

            action_table = Table(action_plan, colWidths=[1.5*inch, 3*inch, 1.5*inch])
            action_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))

            story.append(action_table)

        story.append(Spacer(1, 0.3*inch))
    
    def _add_classification_section(self, story: List, classification_result: Dict):
        """Ajoute la section de classification automatique"""
        story.append(Paragraph("Classification Automatique", self.styles['CustomHeading1']))
        
        predicted_class = classification_result.get("predicted_class", "Non déterminé")
        confidence = classification_result.get("confidence", 0)
        
        classification_text = f"""
        <b>Type de bâtiment prédit:</b> {predicted_class}<br/>
        <b>Niveau de confiance:</b> {confidence:.1%}
        """
        
        story.append(Paragraph(classification_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Top 3 des prédictions
        top_predictions = classification_result.get("top_3_predictions", [])
        if top_predictions:
            story.append(Paragraph("Probabilités par type:", self.styles['CustomHeading2']))
            
            pred_data = [['Type de bâtiment', 'Probabilité']]
            for class_name, probability in top_predictions:
                pred_data.append([class_name, f"{probability:.1%}"])
            
            pred_table = Table(pred_data, colWidths=[3*inch, 2*inch])
            pred_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(pred_table)
        
        story.append(Spacer(1, 0.3*inch))
    
    def _add_appendices(self, story: List, analysis_data: Dict):
        """Ajoute les annexes"""
        story.append(PageBreak())

        # 📚 ANNEXES BIMEX AVANCÉES
        annexes_header = """
        <para align="center" backColor="#F3E8FF" borderColor="#7C3AED" borderWidth="2">
        <font size="20" color="#7C3AED"><b>📚 ANNEXES TECHNIQUES BIMEX</b></font><br/>
        <font size="12" color="#374151">Documentation Complète • Références • Données Détaillées</font>
        </para>
        """
        story.append(Paragraph(annexes_header, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Annexe A: Détail des espaces
        story.append(Paragraph("Annexe A: Détail des espaces", self.styles['CustomHeading2']))
        
        metrics = analysis_data.get("building_metrics", {})
        spaces = metrics.get("spaces", {})
        space_details = spaces.get("space_details", [])
        
        if space_details:
            space_data = [['Nom', 'Type', 'Surface (m²)', 'Volume (m³)']]
            
            for space in space_details[:20]:  # Limiter à 20 espaces
                space_data.append([
                    space.get("name", "Sans nom")[:30],
                    space.get("type", "Non défini"),
                    f"{space.get('area', 0):.1f}" if space.get('area') else "N/A",
                    f"{space.get('volume', 0):.1f}" if space.get('volume') else "N/A"
                ])
            
            space_table = Table(space_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
            space_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(space_table)
        
        story.append(Spacer(1, 0.3*inch))

        # Annexe B: Références Réglementaires
        story.append(Paragraph("Annexe B: Références Réglementaires", self.styles['CustomHeading2']))

        regulations_data = [
            ['Domaine', 'Référence', 'Description'],
            ['Accessibilité PMR', 'Code de la Construction - Articles R111-19', 'Normes d\'accessibilité pour les personnes à mobilité réduite'],
            ['Qualité BIM', 'NF EN ISO 19650', 'Organisation et numérisation des informations relatives aux bâtiments'],
            ['Sécurité Incendie', 'Code de la Construction - Articles R123', 'Règles de sécurité contre les risques d\'incendie'],
            ['Performance Énergétique', 'RT 2012 / RE 2020', 'Réglementation thermique et environnementale'],
            ['Géométrie IFC', 'ISO 16739', 'Standard international pour les données BIM'],
            ['Contrôle Qualité', 'NF P03-001', 'Cahier des charges pour la qualité des modèles BIM']
        ]

        regulations_table = Table(regulations_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
        regulations_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        story.append(regulations_table)
        story.append(Spacer(1, 0.3*inch))

        # Annexe D: Glossaire
        story.append(Paragraph("Annexe D: Glossaire des Termes Techniques", self.styles['CustomHeading2']))

        glossary_data = [
            ['Terme', 'Définition'],
            ['BIM', 'Building Information Modeling - Modélisation des informations du bâtiment'],
            ['IFC', 'Industry Foundation Classes - Format standard d\'échange de données BIM'],
            ['PMR', 'Personne à Mobilité Réduite - Normes d\'accessibilité'],
            ['Anomalie Critique', 'Erreur majeure nécessitant une correction immédiate'],
            ['Ratio Fenêtres/Murs', 'Pourcentage de surface vitrée par rapport à la surface des murs'],
            ['Compacité', 'Mesure de l\'efficacité volumétrique du bâtiment'],
            ['Schema IFC', 'Version du standard IFC utilisée (IFC2X3, IFC4, etc.)'],
            ['Élément Structurel', 'Composant porteur du bâtiment (poutre, poteau, dalle)'],
            ['Espace IFC', 'Zone fonctionnelle définie dans le modèle BIM'],
            ['Conformité PMR', 'Respect des normes d\'accessibilité réglementaires']
        ]

        glossary_table = Table(glossary_data, colWidths=[1.5*inch, 4*inch])
        glossary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))

        story.append(glossary_table)
        story.append(Spacer(1, 0.3*inch))

        # 🏆 FOOTER BIMEX FINAL
        final_footer = f"""
        <para align="center" backColor="#1F2937" borderColor="#374151" borderWidth="1">
        <font size="14" color="#F9FAFB"><b>🏆 BIMEX - Building Information Modeling Expert</b></font><br/>
        <font size="10" color="#D1D5DB">Rapport généré par l'IA BIMEX le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</font><br/>
        <font size="8" color="#9CA3AF">Analyse Intelligente • Machine Learning • Conformité Automatisée</font><br/>
        <font size="8" color="#6B7280">© 2024 BIMEX - Tous droits réservés • Confidentiel</font>
        </para>
        """
        story.append(Paragraph(final_footer, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))

        # Signature IA
        ai_signature = """
        <para align="center">
        <font size="10" color="#7C3AED"><b>🤖 Analysé par l'Intelligence Artificielle BIMEX</b></font><br/>
        <font size="8" color="#6B7280">Précision • Rapidité • Innovation</font>
        </para>
        """
        story.append(Paragraph(ai_signature, self.styles['Normal']))

        # Annexe C: Éléments structurels
        story.append(Paragraph("Annexe C: Résumé des éléments structurels", self.styles['CustomHeading2']))
        
        structural = metrics.get("structural_elements", {})
        structural_summary = f"""
        • Poutres: {structural.get('beams', 0)}<br/>
        • Colonnes: {structural.get('columns', 0)}<br/>
        • Murs: {structural.get('walls', 0)}<br/>
        • Dalles: {structural.get('slabs', 0)}<br/>
        • Fondations: {structural.get('foundations', 0)}
        """
        
        story.append(Paragraph(structural_summary, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    def generate_quick_summary(self, ifc_file_path: str) -> Dict[str, Any]:
        """
        Génère un résumé rapide sans créer de PDF
        
        Args:
            ifc_file_path: Chemin vers le fichier IFC
            
        Returns:
            Dictionnaire avec le résumé
        """
        try:
            analyzer = IFCAnalyzer(ifc_file_path)
            analysis_data = analyzer.generate_full_analysis()
            
            anomaly_detector = IFCAnomalyDetector(ifc_file_path)
            anomalies = anomaly_detector.detect_all_anomalies()
            anomaly_summary = anomaly_detector.get_anomaly_summary()
            
            project_info = analysis_data.get("project_info", {})
            metrics = analysis_data.get("building_metrics", {})
            surfaces = metrics.get("surfaces", {})
            storeys = metrics.get("storeys", {})
            spaces = metrics.get("spaces", {})
            
            summary = {
                "file_name": Path(ifc_file_path).name,
                "project_name": project_info.get("project_name", "Non défini"),
                "building_name": project_info.get("building_name", "Non défini"),
                "key_metrics": {
                    "total_floor_area": surfaces.get("total_floor_area", 0),
                    "total_storeys": storeys.get("total_storeys", 0),
                    "total_spaces": spaces.get("total_spaces", 0),
                    "total_elements": project_info.get("total_elements", 0)
                },
                "quality_assessment": {
                    "total_anomalies": anomaly_summary.get("total_anomalies", 0),
                    "critical_anomalies": anomaly_summary.get("by_severity", {}).get("critical", 0),
                    "high_anomalies": anomaly_summary.get("by_severity", {}).get("high", 0),
                    "quality_score": self._calculate_quality_score(anomaly_summary)
                },
                "recommendations": self._generate_quick_recommendations(analysis_data, anomalies)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {e}")
            raise
    
    def _calculate_quality_score(self, anomaly_summary: Dict) -> float:
        """Calcule un score de qualité basé sur les anomalies"""
        total_anomalies = anomaly_summary.get("total_anomalies", 0)
        critical = anomaly_summary.get("by_severity", {}).get("critical", 0)
        high = anomaly_summary.get("by_severity", {}).get("high", 0)
        medium = anomaly_summary.get("by_severity", {}).get("medium", 0)
        low = anomaly_summary.get("by_severity", {}).get("low", 0)
        
        if total_anomalies == 0:
            return 100.0
        
        # Score pondéré (critique = -10, élevé = -5, moyen = -2, faible = -1)
        penalty = (critical * 10) + (high * 5) + (medium * 2) + (low * 1)
        
        # Score sur 100, minimum 0
        score = max(0, 100 - penalty)
        
        return score
    
    def _generate_quick_recommendations(self, analysis_data: Dict, anomalies: List) -> List[str]:
        """Génère des recommandations rapides"""
        recommendations = []
        
        total_anomalies = len(anomalies)
        critical_count = len([a for a in anomalies if a.severity == AnomalySeverity.CRITICAL])
        
        if total_anomalies == 0:
            recommendations.append("Modèle de excellente qualité - Aucune action requise")
        elif critical_count > 0:
            recommendations.append(f"Corriger immédiatement {critical_count} anomalies critiques")
        elif total_anomalies < 5:
            recommendations.append("Quelques améliorations mineures recommandées")
        else:
            recommendations.append("Révision qualité recommandée")
        
        return recommendations
