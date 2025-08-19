"""
Convertisseur RVT de secours
Utilise des méthodes alternatives quand Autodesk APS n'est pas disponible
"""

import os
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RVTConverterFallback:
    """Convertisseur de secours pour les fichiers RVT"""
    
    def __init__(self):
        """Initialise le convertisseur de secours"""
        self.available_methods = []
        self._check_available_methods()
    
    def _check_available_methods(self):
        """Vérifie les méthodes de conversion disponibles"""
        
        # Vérifier FreeCAD
        try:
            result = subprocess.run(['freecad', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.available_methods.append('freecad')
                logger.info("✅ FreeCAD détecté pour conversion RVT")
        except:
            pass
        
        # Vérifier Blender avec addon IFC
        try:
            result = subprocess.run(['blender', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.available_methods.append('blender')
                logger.info("✅ Blender détecté pour conversion RVT")
        except:
            pass
        
        if not self.available_methods:
            logger.warning("⚠️ Aucune méthode de conversion RVT alternative trouvée")
    
    def is_available(self) -> bool:
        """Vérifie si au moins une méthode est disponible"""
        return len(self.available_methods) > 0
    
    def get_available_methods(self) -> list:
        """Retourne la liste des méthodes disponibles"""
        return self.available_methods.copy()
    
    def convert_rvt_to_ifc_freecad(self, rvt_path: str, ifc_path: str, 
                                  progress_callback=None) -> Dict[str, Any]:
        """Conversion RVT vers IFC avec FreeCAD"""
        try:
            if progress_callback:
                progress_callback(10, "Préparation FreeCAD...")
            
            # Script Python pour FreeCAD
            freecad_script = f"""
import FreeCAD
import Import
import Arch

# Ouvrir le document
doc = FreeCAD.newDocument()

try:
    # Importer le fichier RVT (si supporté)
    Import.insert("{rvt_path}", doc.Name)
    
    # Exporter en IFC
    objects = doc.Objects
    if objects:
        Arch.export(objects, "{ifc_path}")
        print("CONVERSION_SUCCESS")
    else:
        print("CONVERSION_ERROR: Aucun objet trouvé")
        
except Exception as e:
    print(f"CONVERSION_ERROR: {{e}}")

FreeCAD.closeDocument(doc.Name)
"""
            
            # Sauvegarder le script temporairement
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(freecad_script)
                script_path = f.name
            
            if progress_callback:
                progress_callback(30, "Exécution FreeCAD...")
            
            # Exécuter FreeCAD en mode console
            cmd = ['freecad', '-c', script_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Nettoyer le script temporaire
            os.unlink(script_path)
            
            if progress_callback:
                progress_callback(90, "Vérification du résultat...")
            
            # Vérifier le résultat
            if "CONVERSION_SUCCESS" in result.stdout and os.path.exists(ifc_path):
                if progress_callback:
                    progress_callback(100, "Conversion FreeCAD terminée!")
                
                return {
                    'success': True,
                    'method': 'freecad',
                    'message': 'Conversion réussie avec FreeCAD'
                }
            else:
                error_msg = result.stderr or "Erreur inconnue"
                return {
                    'success': False,
                    'method': 'freecad',
                    'error': f'Erreur FreeCAD: {error_msg}'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'method': 'freecad',
                'error': 'Timeout: FreeCAD a pris trop de temps'
            }
        except Exception as e:
            return {
                'success': False,
                'method': 'freecad',
                'error': f'Erreur FreeCAD: {str(e)}'
            }
    
    def convert_rvt_to_ifc_blender(self, rvt_path: str, ifc_path: str, 
                                  progress_callback=None) -> Dict[str, Any]:
        """Conversion RVT vers IFC avec Blender + BlenderBIM"""
        try:
            if progress_callback:
                progress_callback(10, "Préparation Blender...")
            
            # Script Python pour Blender
            blender_script = f"""
import bpy
import bmesh

# Nettoyer la scène
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

try:
    # Importer le fichier (Blender ne supporte pas RVT nativement)
    # Cette méthode est limitée et expérimentale
    print("CONVERSION_ERROR: Blender ne supporte pas nativement les fichiers RVT")
    
except Exception as e:
    print(f"CONVERSION_ERROR: {{e}}")
"""
            
            # Note: Blender ne supporte pas nativement RVT
            # Cette méthode est incluse pour la complétude mais n'est pas fonctionnelle
            return {
                'success': False,
                'method': 'blender',
                'error': 'Blender ne supporte pas nativement les fichiers RVT'
            }
            
        except Exception as e:
            return {
                'success': False,
                'method': 'blender',
                'error': f'Erreur Blender: {str(e)}'
            }
    
    def convert_rvt_to_ifc(self, rvt_path: str, ifc_path: str, 
                          progress_callback=None) -> Dict[str, Any]:
        """
        Convertit un fichier RVT en IFC avec les méthodes disponibles
        
        Args:
            rvt_path: Chemin vers le fichier RVT
            ifc_path: Chemin de sortie pour le fichier IFC
            progress_callback: Fonction de callback pour le progrès
            
        Returns:
            Dictionnaire avec le résultat de la conversion
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Aucune méthode de conversion disponible',
                'message': 'Installez FreeCAD ou configurez Autodesk APS'
            }
        
        logger.info(f"🔄 Tentative conversion RVT avec méthodes alternatives: {rvt_path}")
        
        # Essayer les méthodes disponibles dans l'ordre de préférence
        for method in self.available_methods:
            try:
                if method == 'freecad':
                    result = self.convert_rvt_to_ifc_freecad(rvt_path, ifc_path, progress_callback)
                elif method == 'blender':
                    result = self.convert_rvt_to_ifc_blender(rvt_path, ifc_path, progress_callback)
                else:
                    continue
                
                if result['success']:
                    logger.info(f"✅ Conversion réussie avec {method}")
                    return result
                else:
                    logger.warning(f"⚠️ Échec conversion avec {method}: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"❌ Erreur avec {method}: {e}")
                continue
        
        # Aucune méthode n'a fonctionné
        return {
            'success': False,
            'error': 'Toutes les méthodes de conversion ont échoué',
            'message': 'Essayez de configurer Autodesk APS pour une meilleure compatibilité',
            'tried_methods': self.available_methods
        }

def get_installation_instructions() -> str:
    """Retourne les instructions d'installation pour les outils de conversion"""
    return """
🛠️ INSTALLATION DES OUTILS DE CONVERSION RVT

Option 1: FreeCAD (Recommandé)
- Windows: Téléchargez depuis https://www.freecad.org/downloads.php
- Ubuntu: sudo apt install freecad
- macOS: brew install freecad

Option 2: Autodesk APS (Meilleure qualité)
- Créez un compte sur https://aps.autodesk.com/
- Configurez AUTODESK_CLIENT_ID et AUTODESK_CLIENT_SECRET

Note: La conversion RVT est complexe. Autodesk APS offre la meilleure qualité.
"""
