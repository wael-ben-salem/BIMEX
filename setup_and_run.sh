#!/bin/bash

echo "🚀 CONFIGURATION ET DÉMARRAGE AUTOMATIQUE BIMEX BI"
echo "====================================================="

echo ""
echo "📦 Étape 1: Configuration du système..."
python3 setup_bi_system.py

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la configuration"
    exit 1
fi

echo ""
echo "🚀 Étape 2: Démarrage du serveur..."
echo "Ouverture automatique du navigateur dans 3 secondes..."
sleep 3

# Ouvrir le navigateur selon l'OS
if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:8000/app/home.html" &
elif command -v open > /dev/null; then
    open "http://localhost:8000/app/home.html" &
fi

python3 start_bimex_bi.py
