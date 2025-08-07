#!/bin/bash

echo "========================================"
echo "   BIMEX 2.0 Backend Startup Script"
echo "========================================"
echo

echo "[1/3] Verification de Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERREUR: Python3 n'est pas installe ou pas dans le PATH"
    exit 1
fi

echo
echo "[2/3] Installation des dependances..."
cd backend
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERREUR: Impossible d'installer les dependances"
    exit 1
fi

echo
echo "[3/3] Demarrage du serveur backend..."
echo "Backend sera accessible sur: http://localhost:8000"
echo "Frontend sera accessible sur: http://localhost:8000/frontend/bim_analysis.html"
echo
echo "Appuyez sur Ctrl+C pour arreter le serveur"
echo

python3 main.py
