@echo off
echo ========================================
echo    BIMEX 2.0 Backend Startup Script
echo ========================================
echo.

echo [1/3] Verification de Python...
python --version
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo [2/3] Installation des dependances...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERREUR: Impossible d'installer les dependances
    pause
    exit /b 1
)

echo.
echo [3/3] Demarrage du serveur backend...
echo Backend sera accessible sur: http://localhost:8000
echo Frontend sera accessible sur: http://localhost:8000/frontend/bim_analysis.html
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.

python main.py

pause
