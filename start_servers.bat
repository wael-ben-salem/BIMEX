@echo off
echo 🚀 Démarrage des serveurs XeoKit BIM Viewer
echo.

echo 📋 Configuration:
echo   - Backend (Python FastAPI): Port 8000
echo   - Frontend (HTTP Server): Port 8081
echo.

echo 🔧 Vérification de l'environnement...
if not exist "backend\main.py" (
    echo ❌ Erreur: Fichier backend\main.py non trouvé
    echo    Assurez-vous d'être dans le répertoire racine du projet
    pause
    exit /b 1
)

if not exist "xeokit-bim-viewer\app\index.html" (
    echo ❌ Erreur: Fichier xeokit-bim-viewer\app\index.html non trouvé
    echo    Assurez-vous que le dossier xeokit-bim-viewer existe
    pause
    exit /b 1
)

echo ✅ Fichiers trouvés
echo.

echo 🚀 Démarrage du serveur frontend (port 8081)...
echo    URL: http://localhost:8081/xeokit-bim-viewer/app/home.html
start "Frontend XeoKit" cmd /k "npx http-server . -p 8081"

echo.
echo ⏳ Attente de 3 secondes pour le démarrage du frontend...
timeout /t 3 /nobreak >nul

echo.
echo 🚀 Démarrage du serveur backend (port 8000)...
echo    URL: http://localhost:8000
echo    API: http://localhost:8000/docs
start "Backend Python" cmd /k "cd backend && python main.py"

echo.
echo ✅ Serveurs démarrés !
echo.
echo 📋 URLs importantes:
echo   🏠 Page d'accueil: http://localhost:8081/xeokit-bim-viewer/app/home.html
echo   👁️  Viewer direct:  http://localhost:8081/xeokit-bim-viewer/app/index.html?projectId=basic2
echo   🔧 API Backend:    http://localhost:8000/docs
echo   📊 Analyse BIM:    http://localhost:8000/analysis?project=basic2^&auto=true^&file_detected=true
echo.
echo 💡 Conseils:
echo   - Utilisez la page d'accueil pour naviguer entre les projets
echo   - Cliquez sur "Voir le modèle" pour ouvrir le viewer 3D
echo   - Cliquez sur "Analyser" pour l'analyse BIM automatique
echo.
echo ⚠️  Pour arrêter les serveurs, fermez les fenêtres de commande ouvertes
echo.
pause
