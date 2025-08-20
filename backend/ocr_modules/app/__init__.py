"""
Module d'application OCR principal
Ce fichier expose les modules API pour l'intégration
"""

# Import des modules API
try:
    from .api import files, processing, results
    __all__ = ['files', 'processing', 'results']
except ImportError as e:
    print(f"⚠️ Erreur lors de l'import des modules API: {e}")
    __all__ = []
