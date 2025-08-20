"""
Module API OCR
Ce fichier expose les routes API pour l'intégration
"""

# Import des modules API
try:
    from . import files, processing, results
    __all__ = ['files', 'processing', 'results']
except ImportError as e:
    print(f"⚠️ Erreur lors de l'import des modules API: {e}")
    __all__ = []
