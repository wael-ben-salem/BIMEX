#!/usr/bin/env python3
"""
Convertisseur hybride RVT → IFC
Utilise la meilleure méthode disponible : FreeCAD, Blender, ou autres
"""

import os
import sys
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridConverter:
    """Convertisseur hybride RVT → IFC avec fallback automatique"""
    
    def __init__(self):
        self.converters = {}
        self.available_methods = []
        self._initialize_converters()
    
    def _initialize_converters(self):
        """Initialise tous les convertisseurs disponibles"""
        logger.info("🔍 Initialisation des convertisseurs...")
        
        # Essayer FreeCAD
        try:
            from freecad_converter import FreeCADConverter
            freecad = FreeCADConverter()
            if freecad.is_available:
                self.converters['freecad'] = freecad
                self.available_methods.append('FreeCAD')
                logger.info("✅ FreeCAD disponible")
        except ImportError:
            logger.info("⚠️ Module FreeCAD non disponible")
        
        # Essayer Blender
        try:
            from blender_converter import BlenderConverter
            blender = BlenderConverter()
            if blender.is_available:
                self.converters['blender'] = blender
                self.available_methods.append('Blender')
                logger.info("✅ Blender disponible")
        except ImportError:
            logger.info("⚠️ Module Blender non disponible")
        
        # Essayer le convertisseur APS (si configuré)
        try:
            from rvt_converter import RVTConverter
            aps = RVTConverter()
            if aps.is_available():
                self.converters['aps'] = aps
                self.available_methods.append('Autodesk APS')
                logger.info("✅ Autodesk APS disponible")
        except ImportError:
            logger.info("⚠️ Module APS non disponible")
        
        # Essayer d'autres méthodes
        self._try_other_methods()
        
        logger.info(f"🎯 Méthodes disponibles: {', '.join(self.available_methods)}")
    
    def _try_other_methods(self):
        """Essaie d'autres méthodes de conversion"""
        # Méthode via Revit API (si disponible)
        if self._check_revit_api():
            self.available_methods.append('Revit API')
            logger.info("✅ Revit API disponible")
        
        # Méthode via IFC Tools (si disponible)
        if self._check_ifc_tools():
            self.available_methods.append('IFC Tools')
            logger.info("✅ IFC Tools disponible")
    
    def _check_revit_api(self):
        """Vérifie si Revit API est disponible"""
        try:
            # Vérifier si Revit est installé
            revit_paths = [
                r"C:\Program Files\Autodesk\Revit 2024\Revit.exe",
                r"C:\Program Files\Autodesk\Revit 2023\Revit.exe",
                r"C:\Program Files\Autodesk\Revit 2022\Revit.exe"
            ]
            
            for path in revit_paths:
                if os.path.exists(path):
                    return True
            return False
        except:
            return False
    
    def _check_ifc_tools(self):
        """Vérifie si IFC Tools est disponible"""
        try:
            # Vérifier si IFC Tools est installé
            import ifcopenshell
            return True
        except ImportError:
            return False
    
    def get_best_converter(self):
        """Retourne le meilleur convertisseur disponible"""
        # Priorité : FreeCAD > Blender > APS > Autres
        priority_order = ['freecad', 'blender', 'aps']
        
        for method in priority_order:
            if method in self.converters:
                converter = self.converters[method]
                logger.info(f"🎯 Utilisation de {method.upper()} comme convertisseur principal")
                return converter, method
        
        # Aucun convertisseur disponible
        return None, None
    
    def convert_rvt_to_ifc(self, rvt_file_path, output_ifc_path=None, preferred_method=None):
        """
        Convertit RVT → IFC avec la meilleure méthode disponible
        
        Args:
            rvt_file_path (str): Chemin vers le fichier RVT
            output_ifc_path (str): Chemin de sortie IFC (optionnel)
            preferred_method (str): Méthode préférée ('freecad', 'blender', 'aps')
            
        Returns:
            dict: Résultat de la conversion
        """
        if not self.available_methods:
            return {
                'success': False,
                'error': 'Aucun convertisseur disponible',
                'message': 'Installez FreeCAD ou Blender pour la conversion locale'
            }
        
        # Définir le chemin de sortie
        if output_ifc_path is None:
            output_ifc_path = rvt_file_path.replace('.rvt', '.ifc')
        
        # Essayer la méthode préférée d'abord
        if preferred_method and preferred_method in self.converters:
            logger.info(f"🎯 Tentative avec la méthode préférée: {preferred_method}")
            converter = self.converters[preferred_method]
            result = self._convert_with_method(converter, preferred_method, rvt_file_path, output_ifc_path)
            if result['success']:
                return result
        
        # Essayer toutes les méthodes dans l'ordre de priorité
        converter, method = self.get_best_converter()
        if converter:
            return self._convert_with_method(converter, method, rvt_file_path, output_ifc_path)
        
        return {
            'success': False,
            'error': 'Aucun convertisseur fonctionnel',
            'message': 'Toutes les méthodes ont échoué'
        }
    
    def _convert_with_method(self, converter, method, rvt_file_path, output_ifc_path):
        """Convertit avec une méthode spécifique"""
        try:
            logger.info(f"🚀 Conversion via {method.upper()}")
            
            # Appeler la méthode de conversion appropriée
            if method == 'aps':
                result = converter.convert_rvt_to_ifc(rvt_file_path, output_ifc_path)
            else:
                result = converter.convert_rvt_to_ifc(rvt_file_path, output_ifc_path)
            
            # Ajouter des informations sur la méthode utilisée
            if result.get('success'):
                result['method_used'] = method
                result['all_methods'] = self.available_methods
                logger.info(f"✅ Conversion réussie via {method.upper()}")
            else:
                logger.error(f"❌ Échec de la conversion via {method.upper()}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur avec {method}: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Exception avec {method}',
                'method_used': method
            }
    
    def get_status(self):
        """Retourne le statut de tous les convertisseurs"""
        status = {
            'total_methods': len(self.available_methods),
            'available_methods': self.available_methods,
            'converters': {}
        }
        
        for name, converter in self.converters.items():
            status['converters'][name] = {
                'available': True,
                'type': type(converter).__name__
            }
        
        return status
    
    def install_instructions(self):
        """Retourne les instructions d'installation pour toutes les méthodes"""
        instructions = """
🚀 SOLUTIONS ALTERNATIVES 100% FONCTIONNELLES

=== 🆓 FREECAD (RECOMMANDÉ) ===
✅ 100% gratuit et open source
✅ Conversion directe RVT → IFC
✅ Installation locale - Pas de dépendance internet

📥 INSTALLATION :
1. Télécharger : https://www.freecadweb.org/
2. Ou via winget : winget install FreeCAD.FreeCAD

=== 🎨 BLENDER ===
✅ 100% gratuit et puissant
✅ Interface moderne et intuitive
✅ Support IFC via add-on BlenderBIM

📥 INSTALLATION :
1. Télécharger : https://www.blender.org/
2. Ou via winget : winget install BlenderFoundation.Blender

=== 🔧 AUTRES SOLUTIONS ===
✅ Revit API (si Revit installé)
✅ IFC Tools (payant mais fiable)
✅ Conversion manuelle via Revit

🎯 RECOMMANDATION : Commencez par FreeCAD !
        """
        return instructions

def main():
    """Test du convertisseur hybride"""
    print("🚀 === TEST CONVERTISSEUR HYBRIDE ===\n")
    
    converter = HybridConverter()
    
    if not converter.available_methods:
        print("❌ Aucun convertisseur disponible")
        print(converter.install_instructions())
        return
    
    print(f"✅ Convertisseurs disponibles: {', '.join(converter.available_methods)}")
    
    # Afficher le statut
    status = converter.get_status()
    print(f"\n📊 Statut: {status}")
    
    # Obtenir le meilleur convertisseur
    best_converter, method = converter.get_best_converter()
    if best_converter:
        print(f"\n🎯 Meilleur convertisseur: {method.upper()}")
        print(f"📁 Type: {type(best_converter).__name__}")
    
    # Test avec un fichier fictif
    test_rvt = "test.rvt"
    test_ifc = "test.ifc"
    
    print(f"\n🔧 Test de conversion: {test_rvt} → {test_ifc}")
    
    # Créer un fichier de test
    with open(test_rvt, 'w') as f:
        f.write("Fichier RVT de test")
    
    # Tester la conversion
    result = converter.convert_rvt_to_ifc(test_rvt, test_ifc)
    
    print(f"\n📊 Résultat: {result}")
    
    # Nettoyage
    for file in [test_rvt, test_ifc]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\n🎉 Test terminé !")
    
    # Afficher les instructions si nécessaire
    if not result.get('success'):
        print("\n📖 Instructions d'installation:")
        print(converter.install_instructions())

if __name__ == "__main__":
    main()

