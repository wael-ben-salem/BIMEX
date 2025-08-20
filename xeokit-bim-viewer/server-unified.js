const express = require('express');
const path = require('path');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');

// Configuration des ports
const XEOKIT_PORT = 8081;
const OCR_PORT = 3000;
const UNIFIED_PORT = 8080;

// Application Express principale
const app = express();

// Middleware CORS
app.use(cors());

// Middleware pour servir les fichiers statiques
app.use(express.static(path.join(__dirname)));

// Proxy pour rediriger les requêtes API vers le backend
app.use('/api', createProxyMiddleware({
    target: 'http://localhost:8001',
    changeOrigin: true,
    pathRewrite: {
        '^/api': ''
    }
}));

// Routes principales
app.get('/', (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>XeoKit BIM + OCR - Interface Unifiée</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    text-align: center;
                }
                .header {
                    margin-bottom: 40px;
                }
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .header p {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                .options {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 30px;
                    margin-top: 40px;
                }
                .option-card {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 30px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .option-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }
                .option-card h2 {
                    margin-bottom: 15px;
                    font-size: 1.5em;
                }
                .option-card p {
                    margin-bottom: 20px;
                    opacity: 0.9;
                    line-height: 1.6;
                }
                .btn {
                    display: inline-block;
                    padding: 12px 30px;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    text-decoration: none;
                    border-radius: 25px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    transition: all 0.3s ease;
                    font-weight: bold;
                }
                .btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                    border-color: rgba(255, 255, 255, 0.5);
                    transform: scale(1.05);
                }
                .btn-primary {
                    background: #4CAF50;
                    border-color: #4CAF50;
                }
                .btn-primary:hover {
                    background: #45a049;
                    border-color: #45a049;
                }
                .status {
                    margin-top: 20px;
                    padding: 10px;
                    border-radius: 8px;
                    font-size: 0.9em;
                }
                .status.online {
                    background: rgba(76, 175, 80, 0.2);
                    border: 1px solid #4CAF50;
                }
                .status.offline {
                    background: rgba(244, 67, 54, 0.2);
                    border: 1px solid #f44336;
                }
                .features {
                    margin-top: 20px;
                    text-align: left;
                }
                .features ul {
                    list-style: none;
                    padding: 0;
                }
                .features li {
                    padding: 5px 0;
                    position: relative;
                    padding-left: 20px;
                }
                .features li:before {
                    content: "✓";
                    position: absolute;
                    left: 0;
                    color: #4CAF50;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 XeoKit BIM + OCR</h1>
                    <p>Interface unifiée pour l'analyse BIM et OCR</p>
                </div>
                
                <div class="options">
                                         <div class="option-card">
                         <h2>🎯 Interface Complète</h2>
                         <p>XeoKit BIM Viewer + OCR Analysis avec navigation complète</p>
                         <div class="features">
                             <ul>
                                 <li>Navigation par panneau latéral</li>
                                 <li>Vues multiples intégrées</li>
                                 <li>Interface moderne et responsive</li>
                                 <li>Thème clair/sombre</li>
                             </ul>
                         </div>
                         <a href="/app/index-complete.html" class="btn btn-primary">🚀 Lancer l'Interface Complète</a>
                         <div class="status online" id="complete-status">
                             ✅ Interface complète disponible
                         </div>
                     </div>
                     
                     <div class="option-card">
                         <h2>🔗 Interface Intégrée</h2>
                         <p>XeoKit BIM Viewer + OCR Analysis dans une seule interface</p>
                         <div class="features">
                             <ul>
                                 <li>Visualisation BIM complète</li>
                                 <li>Analyse OCR des plans</li>
                                 <li>Interface unifiée</li>
                                 <li>Bouton OCR flottant</li>
                             </ul>
                         </div>
                         <a href="/app/index-integrated.html" class="btn">🔗 Lancer l'Interface Intégrée</a>
                         <div class="status online" id="integrated-status">
                             ✅ Interface intégrée disponible
                         </div>
                     </div>
                    
                    <div class="option-card">
                        <h2>🏗️ XeoKit BIM Viewer</h2>
                        <p>Visualisation BIM traditionnelle</p>
                        <div class="features">
                            <ul>
                                <li>Visualisation 3D</li>
                                <li>Explorateur d'objets</li>
                                <li>Inspecteur de propriétés</li>
                                <li>Outils de navigation</li>
                            </ul>
                        </div>
                        <a href="/app/index.html" class="btn">👁️ Ouvrir XeoKit Viewer</a>
                        <div class="status online" id="xeokit-status">
                            ✅ XeoKit Viewer disponible
                        </div>
                    </div>
                    
                    <div class="option-card">
                        <h2>📷 OCR Frontend</h2>
                        <p>Interface dédiée à l'analyse OCR</p>
                        <div class="features">
                            <ul>
                                <li>Upload d'images</li>
                                <li>Analyse OCR avancée</li>
                                <li>Résultats détaillés</li>
                                <li>Interface React moderne</li>
                            </ul>
                        </div>
                        <a href="http://localhost:3000" class="btn" target="_blank">📷 Ouvrir OCR Frontend</a>
                        <div class="status offline" id="ocr-status">
                            ⚠️ OCR Frontend (port 3000)
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 40px; opacity: 0.8;">
                    <p><strong>Backend API:</strong> <a href="http://localhost:8001" target="_blank" style="color: #4CAF50;">http://localhost:8001</a></p>
                    <p><strong>Documentation:</strong> <a href="http://localhost:8001/docs" target="_blank" style="color: #4CAF50;">API Documentation</a></p>
                </div>
            </div>
            
            <script>
                // Vérifier le statut des services
                async function checkServiceStatus() {
                    try {
                        // Vérifier le backend
                        const backendResponse = await fetch('/api/');
                        if (backendResponse.ok) {
                            document.getElementById('integrated-status').className = 'status online';
                            document.getElementById('integrated-status').innerHTML = '✅ Backend connecté';
                        }
                    } catch (error) {
                        document.getElementById('integrated-status').className = 'status offline';
                        document.getElementById('integrated-status').innerHTML = '❌ Backend non connecté';
                    }
                }
                
                // Vérifier le statut au chargement
                checkServiceStatus();
                
                // Vérifier périodiquement
                setInterval(checkServiceStatus, 10000);
            </script>
        </body>
        </html>
    `);
});

// Route pour l'interface complète
app.get('/complete', (req, res) => {
    res.redirect('/app/index-complete.html');
});

// Route pour l'interface intégrée
app.get('/integrated', (req, res) => {
    res.redirect('/app/index-integrated.html');
});

// Route pour le XeoKit viewer
app.get('/xeokit', (req, res) => {
    res.redirect('/app/index.html');
});

// Route pour l'OCR frontend
app.get('/ocr', (req, res) => {
    res.redirect('http://localhost:3000');
});

// Démarrer le serveur
app.listen(UNIFIED_PORT, () => {
    console.log('🚀 Serveur Frontend Unifié démarré!');
    console.log(`📱 Interface principale: http://localhost:${UNIFIED_PORT}`);
    console.log(`🎯 Interface complète: http://localhost:${UNIFIED_PORT}/app/index-complete.html`);
    console.log(`🔗 Interface intégrée: http://localhost:${UNIFIED_PORT}/app/index-integrated.html`);
    console.log(`🏗️ XeoKit Viewer: http://localhost:${UNIFIED_PORT}/app/index.html`);
    console.log(`📷 OCR Frontend: http://localhost:3000`);
    console.log(`🔧 Backend API: http://localhost:8001`);
    console.log('');
    console.log('💡 Utilisez l\'interface principale pour naviguer entre les différentes vues!');
});
