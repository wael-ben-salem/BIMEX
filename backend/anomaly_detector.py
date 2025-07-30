"""
Module de détection d'anomalies dans les modèles IFC
Identifie automatiquement les erreurs et incohérences dans les modèles BIM
"""

import ifcopenshell
import ifcopenshell.util.element
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AnomalySeverity(Enum):
    """Niveaux de sévérité des anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Anomaly:
    """Classe pour représenter une anomalie détectée"""
    id: str
    element_id: str
    element_type: str
    element_name: str
    anomaly_type: str
    description: str
    severity: AnomalySeverity
    suggested_fix: str
    location: Optional[Dict[str, float]] = None
    additional_data: Optional[Dict[str, Any]] = None

class IFCAnomalyDetector:
    """Détecteur d'anomalies pour les fichiers IFC"""

    def __init__(self, ifc_file_path: str):
        """
        Initialise le détecteur d'anomalies

        Args:
            ifc_file_path: Chemin vers le fichier IFC
        """
        self.ifc_file_path = ifc_file_path
        self.ifc_file = ifcopenshell.open(ifc_file_path)
        self.anomalies = []

    def _get_element_name(self, element) -> str:
        """Récupère le nom d'un élément de manière sécurisée"""
        try:
            return getattr(element, 'Name', None) or "Sans nom"
        except:
            return "Sans nom"
        
    def detect_all_anomalies(self) -> List[Anomaly]:
        """Détecte toutes les anomalies dans le modèle IFC"""
        logger.info("Début de la détection d'anomalies")
        
        self.anomalies = []
        
        # Différents types de détection
        self._detect_missing_properties()
        self._detect_geometric_inconsistencies()
        self._detect_material_issues()
        self._detect_connectivity_issues()
        self._detect_naming_issues()
        self._detect_classification_issues()
        self._detect_structural_issues()
        self._detect_space_issues()
        
        logger.info(f"Détection terminée. {len(self.anomalies)} anomalies trouvées")
        return self.anomalies
    
    def _detect_missing_properties(self):
        """Détecte les propriétés manquantes essentielles"""
        logger.info("Détection des propriétés manquantes")
        
        # Éléments qui doivent avoir des matériaux
        elements_needing_materials = (
            self.ifc_file.by_type("IfcWall") +
            self.ifc_file.by_type("IfcSlab") +
            self.ifc_file.by_type("IfcBeam") +
            self.ifc_file.by_type("IfcColumn")
        )
        
        for element in elements_needing_materials:
            materials = ifcopenshell.util.element.get_materials(element)
            if not materials:
                self.anomalies.append(Anomaly(
                    id=f"missing_material_{element.GlobalId}",
                    element_id=element.GlobalId,
                    element_type=element.is_a(),
                    element_name=element.Name or "Sans nom",
                    anomaly_type="missing_material",
                    description=f"L'élément {element.is_a()} n'a pas de matériau défini",
                    severity=AnomalySeverity.MEDIUM,
                    suggested_fix="Assigner un matériau approprié à cet élément"
                ))
        
        # Éléments sans nom
        all_elements = self.ifc_file.by_type("IfcElement")
        for element in all_elements:
            element_name = getattr(element, 'Name', None)
            if not element_name or element_name.strip() == "":
                self.anomalies.append(Anomaly(
                    id=f"missing_name_{element.GlobalId}",
                    element_id=element.GlobalId,
                    element_type=element.is_a(),
                    element_name="Sans nom",
                    anomaly_type="missing_name",
                    description=f"L'élément {element.is_a()} n'a pas de nom défini",
                    severity=AnomalySeverity.LOW,
                    suggested_fix="Donner un nom descriptif à cet élément"
                ))
        
        # Espaces sans surface ou volume
        spaces = self.ifc_file.by_type("IfcSpace")
        for space in spaces:
            psets = ifcopenshell.util.element.get_psets(space)
            has_area = any('Area' in pset or 'NetArea' in pset or 'GrossArea' in pset 
                          for pset in psets.values())
            has_volume = any('Volume' in pset or 'NetVolume' in pset or 'GrossVolume' in pset 
                            for pset in psets.values())
            
            if not has_area:
                self.anomalies.append(Anomaly(
                    id=f"missing_area_{space.GlobalId}",
                    element_id=space.GlobalId,
                    element_type=space.is_a(),
                    element_name=space.Name or "Sans nom",
                    anomaly_type="missing_area",
                    description="L'espace n'a pas de surface définie",
                    severity=AnomalySeverity.MEDIUM,
                    suggested_fix="Calculer et assigner la surface de l'espace"
                ))
            
            if not has_volume:
                self.anomalies.append(Anomaly(
                    id=f"missing_volume_{space.GlobalId}",
                    element_id=space.GlobalId,
                    element_type=space.is_a(),
                    element_name=space.Name or "Sans nom",
                    anomaly_type="missing_volume",
                    description="L'espace n'a pas de volume défini",
                    severity=AnomalySeverity.MEDIUM,
                    suggested_fix="Calculer et assigner le volume de l'espace"
                ))
    
    def _detect_geometric_inconsistencies(self):
        """Détecte les incohérences géométriques"""
        logger.info("Détection des incohérences géométriques")
        
        # Éléments avec des dimensions nulles ou négatives
        elements_with_geometry = (
            self.ifc_file.by_type("IfcWall") +
            self.ifc_file.by_type("IfcSlab") +
            self.ifc_file.by_type("IfcBeam") +
            self.ifc_file.by_type("IfcColumn")
        )
        
        for element in elements_with_geometry:
            psets = ifcopenshell.util.element.get_psets(element)
            
            # Vérifier les dimensions
            for pset_name, pset in psets.items():
                for prop_name, prop_value in pset.items():
                    if any(dim in prop_name.lower() for dim in ['length', 'width', 'height', 'thickness']):
                        try:
                            value = float(prop_value)
                            if value <= 0:
                                self.anomalies.append(Anomaly(
                                    id=f"invalid_dimension_{element.GlobalId}_{prop_name}",
                                    element_id=element.GlobalId,
                                    element_type=element.is_a(),
                                    element_name=element.Name or "Sans nom",
                                    anomaly_type="invalid_dimension",
                                    description=f"Dimension invalide: {prop_name} = {value}",
                                    severity=AnomalySeverity.HIGH,
                                    suggested_fix="Corriger la dimension avec une valeur positive",
                                    additional_data={"property": prop_name, "value": value}
                                ))
                        except (ValueError, TypeError):
                            continue
        
        # Vérifier les hauteurs d'étages incohérentes
        storeys = self.ifc_file.by_type("IfcBuildingStorey")
        if len(storeys) > 1:
            elevations = []
            for storey in storeys:
                if hasattr(storey, 'Elevation') and storey.Elevation is not None:
                    elevations.append((storey, storey.Elevation))
            
            elevations.sort(key=lambda x: x[1])
            
            for i in range(len(elevations) - 1):
                current_storey, current_elev = elevations[i]
                next_storey, next_elev = elevations[i + 1]
                height_diff = next_elev - current_elev
                
                # Hauteur d'étage anormale (< 2m ou > 6m)
                if height_diff < 2.0 or height_diff > 6.0:
                    self.anomalies.append(Anomaly(
                        id=f"unusual_storey_height_{current_storey.GlobalId}",
                        element_id=current_storey.GlobalId,
                        element_type=current_storey.is_a(),
                        element_name=current_storey.Name or "Sans nom",
                        anomaly_type="unusual_storey_height",
                        description=f"Hauteur d'étage inhabituelle: {height_diff:.2f}m",
                        severity=AnomalySeverity.MEDIUM,
                        suggested_fix="Vérifier l'élévation des étages",
                        additional_data={"height": height_diff}
                    ))
    
    def _detect_material_issues(self):
        """Détecte les problèmes liés aux matériaux"""
        logger.info("Détection des problèmes de matériaux")
        
        # Matériaux avec des noms génériques ou vides
        materials = self.ifc_file.by_type("IfcMaterial")
        generic_names = ['material', 'mat', 'default', 'unnamed', 'sans nom', '']

        for material in materials:
            material_name = getattr(material, 'Name', None)
            if not material_name or material_name.lower().strip() in generic_names:
                self.anomalies.append(Anomaly(
                    id=f"generic_material_{material.id()}",
                    element_id=str(material.id()),
                    element_type=material.is_a(),
                    element_name=material_name or "Sans nom",
                    anomaly_type="generic_material_name",
                    description="Matériau avec un nom générique ou vide",
                    severity=AnomalySeverity.LOW,
                    suggested_fix="Donner un nom descriptif au matériau"
                ))
        
        # Éléments structurels sans matériau approprié
        structural_elements = (
            self.ifc_file.by_type("IfcWall") +
            self.ifc_file.by_type("IfcSlab") +
            self.ifc_file.by_type("IfcBeam") +
            self.ifc_file.by_type("IfcColumn")
        )
        
        for element in structural_elements:
            materials = ifcopenshell.util.element.get_materials(element)
            if materials:
                material_names = [getattr(mat, 'Name', '').lower() if getattr(mat, 'Name', None) else '' for mat in materials]
                # Vérifier si le matériau semble approprié pour l'élément
                element_type = element.is_a().lower()
                
                inappropriate = True
                if 'wall' in element_type:
                    inappropriate = not any(mat in material_names[0] for mat in ['concrete', 'brick', 'block', 'béton', 'brique'])
                elif 'slab' in element_type:
                    inappropriate = not any(mat in material_names[0] for mat in ['concrete', 'steel', 'béton', 'acier'])
                elif any(struct in element_type for struct in ['beam', 'column']):
                    inappropriate = not any(mat in material_names[0] for mat in ['concrete', 'steel', 'wood', 'béton', 'acier', 'bois'])
                
                if inappropriate and material_names[0]:
                    self.anomalies.append(Anomaly(
                        id=f"inappropriate_material_{element.GlobalId}",
                        element_id=element.GlobalId,
                        element_type=element.is_a(),
                        element_name=element.Name or "Sans nom",
                        anomaly_type="inappropriate_material",
                        description=f"Matériau possiblement inapproprié pour {element.is_a()}: {material_names[0]}",
                        severity=AnomalySeverity.LOW,
                        suggested_fix="Vérifier que le matériau est approprié pour cet élément"
                    ))
    
    def _detect_connectivity_issues(self):
        """Détecte les problèmes de connectivité entre éléments"""
        logger.info("Détection des problèmes de connectivité")
        
        # Portes et fenêtres non connectées à des murs
        openings = self.ifc_file.by_type("IfcDoor") + self.ifc_file.by_type("IfcWindow")
        
        for opening in openings:
            # Chercher les relations de remplissage
            filling_rels = [rel for rel in self.ifc_file.by_type("IfcRelFillsElement") 
                           if rel.RelatedBuildingElement == opening]
            
            if not filling_rels:
                self.anomalies.append(Anomaly(
                    id=f"unconnected_opening_{opening.GlobalId}",
                    element_id=opening.GlobalId,
                    element_type=opening.is_a(),
                    element_name=opening.Name or "Sans nom",
                    anomaly_type="unconnected_opening",
                    description=f"{opening.is_a()} non connecté(e) à un mur",
                    severity=AnomalySeverity.HIGH,
                    suggested_fix="Connecter l'ouverture à un mur approprié"
                ))
        
        # Espaces sans éléments de délimitation
        spaces = self.ifc_file.by_type("IfcSpace")
        for space in spaces:
            boundary_rels = [rel for rel in self.ifc_file.by_type("IfcRelSpaceBoundary") 
                            if rel.RelatingSpace == space]
            
            if not boundary_rels:
                self.anomalies.append(Anomaly(
                    id=f"unbounded_space_{space.GlobalId}",
                    element_id=space.GlobalId,
                    element_type=space.is_a(),
                    element_name=space.Name or "Sans nom",
                    anomaly_type="unbounded_space",
                    description="Espace sans éléments de délimitation définis",
                    severity=AnomalySeverity.MEDIUM,
                    suggested_fix="Définir les éléments qui délimitent cet espace"
                ))
    
    def _detect_naming_issues(self):
        """Détecte les problèmes de nommage"""
        logger.info("Détection des problèmes de nommage")
        
        # Noms dupliqués pour des éléments du même type
        element_types = ["IfcWall", "IfcSlab", "IfcBeam", "IfcColumn", "IfcSpace", "IfcDoor", "IfcWindow"]
        
        for element_type in element_types:
            elements = self.ifc_file.by_type(element_type)
            names = {}
            
            for element in elements:
                if element.Name:
                    name = element.Name.strip()
                    if name in names:
                        names[name].append(element)
                    else:
                        names[name] = [element]
            
            # Signaler les doublons
            for name, element_list in names.items():
                if len(element_list) > 1:
                    for element in element_list:
                        self.anomalies.append(Anomaly(
                            id=f"duplicate_name_{element.GlobalId}",
                            element_id=element.GlobalId,
                            element_type=element.is_a(),
                            element_name=element.Name or "Sans nom",
                            anomaly_type="duplicate_name",
                            description=f"Nom dupliqué '{name}' pour {element.is_a()}",
                            severity=AnomalySeverity.LOW,
                            suggested_fix="Utiliser des noms uniques pour chaque élément",
                            additional_data={"duplicate_count": len(element_list)}
                        ))
    
    def _detect_classification_issues(self):
        """Détecte les problèmes de classification"""
        logger.info("Détection des problèmes de classification")
        
        # Éléments sans classification
        elements = self.ifc_file.by_type("IfcElement")
        for element in elements:
            # Chercher les références de classification
            class_refs = [rel for rel in self.ifc_file.by_type("IfcRelAssociatesClassification") 
                         if element in rel.RelatedObjects]
            
            if not class_refs and not hasattr(element, 'ObjectType'):
                self.anomalies.append(Anomaly(
                    id=f"unclassified_element_{element.GlobalId}",
                    element_id=element.GlobalId,
                    element_type=element.is_a(),
                    element_name=element.Name or "Sans nom",
                    anomaly_type="unclassified_element",
                    description="Élément sans classification ou type d'objet défini",
                    severity=AnomalySeverity.LOW,
                    suggested_fix="Assigner une classification ou un type d'objet approprié"
                ))
    
    def _detect_structural_issues(self):
        """Détecte les problèmes structurels"""
        logger.info("Détection des problèmes structurels")
        
        # Poutres sans support
        beams = self.ifc_file.by_type("IfcBeam")
        columns = self.ifc_file.by_type("IfcColumn")
        walls = self.ifc_file.by_type("IfcWall")
        
        for beam in beams:
            # Vérifier si la poutre a des supports (connexions avec colonnes ou murs)
            connections = [rel for rel in self.ifc_file.by_type("IfcRelConnectsElements") 
                          if beam in [rel.RelatingElement, rel.RelatedElement]]
            
            has_support = False
            for conn in connections:
                other_element = conn.RelatedElement if conn.RelatingElement == beam else conn.RelatingElement
                if other_element.is_a() in ["IfcColumn", "IfcWall"]:
                    has_support = True
                    break
            
            if not has_support:
                # Créer un nom unique pour chaque poutre
                beam_name = getattr(beam, 'Name', None) or f"Poutre-{beam.GlobalId[:8]}"
                self.anomalies.append(Anomaly(
                    id=f"unsupported_beam_{beam.GlobalId}",
                    element_id=beam.GlobalId,
                    element_type=beam.is_a(),
                    element_name=beam_name,
                    anomaly_type="unsupported_beam",
                    description=f"Poutre '{beam_name}' sans support apparent (colonne ou mur)",
                    severity=AnomalySeverity.CRITICAL,
                    suggested_fix=f"Vérifier les connexions structurelles de la poutre '{beam_name}'"
                ))
    
    def _detect_space_issues(self):
        """Détecte les problèmes liés aux espaces"""
        logger.info("Détection des problèmes d'espaces")
        
        spaces = self.ifc_file.by_type("IfcSpace")
        
        for space in spaces:
            # Espaces avec des surfaces anormalement petites ou grandes
            psets = ifcopenshell.util.element.get_psets(space)
            area = None
            
            for pset_name, pset in psets.items():
                if 'Area' in pset:
                    try:
                        area = float(pset['Area'])
                        break
                    except (ValueError, TypeError):
                        continue
            
            if area is not None:
                if area < 1.0:  # Moins de 1 m²
                    self.anomalies.append(Anomaly(
                        id=f"tiny_space_{space.GlobalId}",
                        element_id=space.GlobalId,
                        element_type=space.is_a(),
                        element_name=space.Name or "Sans nom",
                        anomaly_type="tiny_space",
                        description=f"Espace très petit: {area:.2f} m²",
                        severity=AnomalySeverity.MEDIUM,
                        suggested_fix="Vérifier si cette surface est correcte",
                        additional_data={"area": area}
                    ))
                elif area > 1000.0:  # Plus de 1000 m²
                    self.anomalies.append(Anomaly(
                        id=f"huge_space_{space.GlobalId}",
                        element_id=space.GlobalId,
                        element_type=space.is_a(),
                        element_name=space.Name or "Sans nom",
                        anomaly_type="huge_space",
                        description=f"Espace très grand: {area:.2f} m²",
                        severity=AnomalySeverity.LOW,
                        suggested_fix="Vérifier si cette surface est correcte ou si l'espace doit être subdivisé",
                        additional_data={"area": area}
                    ))
    
    def get_anomalies_by_severity(self, severity: AnomalySeverity) -> List[Anomaly]:
        """Retourne les anomalies d'un niveau de sévérité donné"""
        return [anomaly for anomaly in self.anomalies if anomaly.severity == severity]
    
    def get_anomalies_by_type(self, anomaly_type: str) -> List[Anomaly]:
        """Retourne les anomalies d'un type donné"""
        return [anomaly for anomaly in self.anomalies if anomaly.anomaly_type == anomaly_type]
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """Génère un résumé des anomalies détectées"""
        summary = {
            "total_anomalies": len(self.anomalies),
            "by_severity": {
                "critical": len(self.get_anomalies_by_severity(AnomalySeverity.CRITICAL)),
                "high": len(self.get_anomalies_by_severity(AnomalySeverity.HIGH)),
                "medium": len(self.get_anomalies_by_severity(AnomalySeverity.MEDIUM)),
                "low": len(self.get_anomalies_by_severity(AnomalySeverity.LOW))
            },
            "by_type": {},
            "most_common_issues": []
        }
        
        # Compter par type
        type_counts = {}
        for anomaly in self.anomalies:
            if anomaly.anomaly_type in type_counts:
                type_counts[anomaly.anomaly_type] += 1
            else:
                type_counts[anomaly.anomaly_type] = 1
        
        summary["by_type"] = type_counts
        
        # Les problèmes les plus fréquents
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        summary["most_common_issues"] = sorted_types[:5]
        
        return summary
    
    def export_anomalies_to_dict(self) -> List[Dict[str, Any]]:
        """Exporte les anomalies vers une liste de dictionnaires"""
        return [
            {
                "id": anomaly.id,
                "element_id": anomaly.element_id,
                "element_type": anomaly.element_type,
                "element_name": anomaly.element_name,
                "anomaly_type": anomaly.anomaly_type,
                "description": anomaly.description,
                "severity": anomaly.severity.value,
                "suggested_fix": anomaly.suggested_fix,
                "location": anomaly.location,
                "additional_data": anomaly.additional_data
            }
            for anomaly in self.anomalies
        ]

    def get_grouped_anomalies(self) -> Dict[str, Dict]:
        """Retourne les anomalies groupées par type pour éviter les répétitions"""
        grouped = {}

        for anomaly in self.anomalies:
            anomaly_type = anomaly.anomaly_type

            if anomaly_type not in grouped:
                # Extraire la description générique (sans nom spécifique)
                base_description = anomaly.description
                if "'" in base_description:
                    base_description = base_description.split("'")[0].strip() + " (éléments multiples)"

                base_fix = anomaly.suggested_fix
                if "'" in base_fix:
                    base_fix = base_fix.split("'")[0].strip() + " pour chaque élément concerné"

                grouped[anomaly_type] = {
                    "type": anomaly_type,
                    "severity": anomaly.severity,
                    "count": 0,
                    "elements": [],
                    "description": base_description,
                    "suggested_fix": base_fix
                }

            grouped[anomaly_type]["count"] += 1
            grouped[anomaly_type]["elements"].append({
                "name": anomaly.element_name,
                "id": anomaly.element_id,
                "type": anomaly.element_type
            })

        return grouped
