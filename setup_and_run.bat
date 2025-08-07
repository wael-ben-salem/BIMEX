@echo off
echo 🚀 CONFIGURATION ET DÉMARRAGE AUTOMATIQUE BIMEX BI
echo =====================================================

echo.
echo 📦 Étape 1: Configuration du système...
python setup_bi_system.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de la configuration
    pause
    exit /b 1
)

echo.
echo 🚀 Étape 2: Démarrage du serveur...
echo Ouverture automatique du navigateur dans 3 secondes...
timeout /t 3 /nobreak > nul

start "" "http://localhost:8000/app/home.html"
python start_bimex_bi.py

pause
