#!/usr/bin/env python3
"""
🚀 CONFIGURATION AUTOMATIQUE POUR SOLUTIONS OPEN-SOURCE
Apache Superset + IFC.js + n8n + ERPNext
"""

import os
import json
import subprocess
import sys
import time
import requests
from pathlib import Path

def print_step(step, message):
    """Affiche une étape avec style"""
    print(f"\n🔧 ÉTAPE {step}: {message}")
    print("=" * 60)

def check_docker():
    """Vérifie que Docker est installé"""
    try:
        subprocess.check_output(["docker", "--version"])
        print("✅ Docker détecté")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Docker non détecté - installation manuelle requise")
        return False

def create_docker_compose():
    """Crée un docker-compose.yml pour les services open-source"""
    print_step(1, "CRÉATION DU DOCKER-COMPOSE")
    
    docker_compose = """version: '3.8'

services:
  # Apache Superset
  superset:
    image: apache/superset:latest
    container_name: bimex_superset
    ports:
      - "8088:8088"
    environment:
      - SUPERSET_SECRET_KEY=your_secret_key_here
    volumes:
      - superset_data:/app/superset_home
    command: >
      bash -c "
        superset fab create-admin --username admin --firstname Admin --lastname User --email admin@bimex.com --password admin &&
        superset db upgrade &&
        superset init &&
        superset run -h 0.0.0.0 -p 8088
      "
    restart: unless-stopped

  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: bimex_n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

  # ERPNext (Frappe)
  erpnext:
    image: frappe/erpnext:latest
    container_name: bimex_erpnext
    ports:
      - "8000:8000"
    environment:
      - SITE_NAME=bimex.localhost
      - ADMIN_PASSWORD=admin
    volumes:
      - erpnext_data:/home/frappe/frappe-bench
    restart: unless-stopped

  # IFC.js Viewer (Node.js app)
  ifc-viewer:
    image: node:16-alpine
    container_name: bimex_ifc_viewer
    ports:
      - "3000:3000"
    working_dir: /app
    volumes:
      - ./ifc-viewer:/app
    command: >
      sh -c "
        if [ ! -f package.json ]; then
          npm init -y &&
          npm install express multer three ifc.js &&
          echo 'const express = require(\"express\"); const app = express(); app.use(express.static(\"public\")); app.listen(3000, () => console.log(\"IFC Viewer on port 3000\"));' > server.js
        fi &&
        npm start
      "
    restart: unless-stopped

volumes:
  superset_data:
  n8n_data:
  erpnext_data:
"""
    
    compose_path = Path("docker-compose-bi.yml")
    with open(compose_path, 'w') as f:
        f.write(docker_compose)
    
    print(f"✅ Docker Compose créé : {compose_path}")
    return compose_path

def create_ifc_viewer_app():
    """Crée une application IFC.js Viewer simple"""
    print_step(2, "CRÉATION DE L'APPLICATION IFC VIEWER")
    
    viewer_dir = Path("ifc-viewer")
    viewer_dir.mkdir(exist_ok=True)
    
    # Package.json
    package_json = {
        "name": "bimex-ifc-viewer",
        "version": "1.0.0",
        "description": "IFC.js Viewer pour BIMEX BI",
        "main": "server.js",
        "scripts": {
            "start": "node server.js"
        },
        "dependencies": {
            "express": "^4.18.0",
            "multer": "^1.4.0",
            "cors": "^2.8.5"
        }
    }
    
    with open(viewer_dir / "package.json", 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Server.js
    server_js = '''const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Configuration multer pour upload IFC
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

// API Routes
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'IFC.js Viewer', timestamp: new Date().toISOString() });
});

app.post('/viewer/upload', upload.single('ifc'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Aucun fichier IFC fourni' });
  }
  
  res.json({
    success: true,
    message: 'Fichier IFC uploadé avec succès',
    file: {
      filename: req.file.filename,
      originalname: req.file.originalname,
      size: req.file.size,
      path: req.file.path
    }
  });
});

app.get('/viewer/models', (req, res) => {
  const uploadsDir = 'uploads';
  if (!fs.existsSync(uploadsDir)) {
    return res.json({ models: [] });
  }
  
  const files = fs.readdirSync(uploadsDir)
    .filter(file => file.endsWith('.ifc'))
    .map(file => ({
      name: file,
      path: `/uploads/${file}`,
      size: fs.statSync(path.join(uploadsDir, file)).size,
      modified: fs.statSync(path.join(uploadsDir, file)).mtime
    }));
  
  res.json({ models: files });
});

app.listen(port, () => {
  console.log(`🏗️ IFC.js Viewer démarré sur http://localhost:${port}`);
});
'''
    
    with open(viewer_dir / "server.js", 'w') as f:
        f.write(server_js)
    
    # Créer le dossier public
    public_dir = viewer_dir / "public"
    public_dir.mkdir(exist_ok=True)
    
    # Index.html simple
    index_html = '''<!DOCTYPE html>
<html>
<head>
    <title>BIMEX IFC.js Viewer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .upload-area { border: 2px dashed #ccc; padding: 20px; text-align: center; margin: 20px 0; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ BIMEX IFC.js Viewer</h1>
        <div class="upload-area">
            <input type="file" id="ifcFile" accept=".ifc" />
            <button onclick="uploadIFC()">Upload IFC</button>
        </div>
        <div id="status"></div>
        <div id="models"></div>
    </div>
    
    <script>
        function uploadIFC() {
            const fileInput = document.getElementById('ifcFile');
            const file = fileInput.files[0];
            
            if (!file) {
                showStatus('Veuillez sélectionner un fichier IFC', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('ifc', file);
            
            fetch('/viewer/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showStatus('Fichier IFC uploadé avec succès!', 'success');
                    loadModels();
                } else {
                    showStatus('Erreur: ' + data.error, 'error');
                }
            })
            .catch(error => {
                showStatus('Erreur: ' + error.message, 'error');
            });
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
        }
        
        function loadModels() {
            fetch('/viewer/models')
            .then(response => response.json())
            .then(data => {
                const modelsDiv = document.getElementById('models');
                if (data.models.length > 0) {
                    modelsDiv.innerHTML = '<h3>Modèles IFC disponibles:</h3>' + 
                        data.models.map(model => `<p>📄 ${model.name} (${Math.round(model.size/1024)}KB)</p>`).join('');
                }
            });
        }
        
        // Charger les modèles au démarrage
        loadModels();
    </script>
</body>
</html>'''
    
    with open(public_dir / "index.html", 'w') as f:
        f.write(index_html)
    
    print(f"✅ Application IFC Viewer créée : {viewer_dir}")

def create_startup_scripts():
    """Crée les scripts de démarrage pour les services"""
    print_step(3, "CRÉATION DES SCRIPTS DE DÉMARRAGE")
    
    # Script de démarrage des services
    start_services = '''#!/bin/bash
echo "🚀 DÉMARRAGE DES SERVICES OPEN-SOURCE BIMEX BI"
echo "================================================"

echo "📦 Démarrage des conteneurs Docker..."
docker-compose -f docker-compose-bi.yml up -d

echo "⏳ Attente du démarrage des services..."
sleep 10

echo "🌐 Services disponibles:"
echo "  📊 Superset:    http://localhost:8088 (admin/admin)"
echo "  ⚙️ n8n:         http://localhost:5678 (admin/admin)"
echo "  🏢 ERPNext:     http://localhost:8000"
echo "  🏗️ IFC Viewer:  http://localhost:3000"
echo "  🚀 BIMEX BI:    http://localhost:8000/app/home.html"

echo "✅ Tous les services sont démarrés!"
'''
    
    with open("start_services.sh", 'w') as f:
        f.write(start_services)
    
    os.chmod("start_services.sh", 0o755)
    
    # Script Windows
    start_services_bat = '''@echo off
echo 🚀 DÉMARRAGE DES SERVICES OPEN-SOURCE BIMEX BI
echo ================================================

echo 📦 Démarrage des conteneurs Docker...
docker-compose -f docker-compose-bi.yml up -d

echo ⏳ Attente du démarrage des services...
timeout /t 10 /nobreak > nul

echo 🌐 Services disponibles:
echo   📊 Superset:    http://localhost:8088 (admin/admin)
echo   ⚙️ n8n:         http://localhost:5678 (admin/admin)
echo   🏢 ERPNext:     http://localhost:8000
echo   🏗️ IFC Viewer:  http://localhost:3000
echo   🚀 BIMEX BI:    http://localhost:8000/app/home.html

echo ✅ Tous les services sont démarrés!
pause
'''
    
    with open("start_services.bat", 'w') as f:
        f.write(start_services_bat)
    
    print("✅ Scripts de démarrage créés")

def main():
    """Fonction principale"""
    print("🚀 CONFIGURATION AUTOMATIQUE - SOLUTIONS OPEN-SOURCE")
    print("=" * 60)
    print("Apache Superset + IFC.js + n8n + ERPNext")
    
    try:
        has_docker = check_docker()
        create_docker_compose()
        create_ifc_viewer_app()
        create_startup_scripts()
        
        print("\n" + "=" * 60)
        print("🎉 CONFIGURATION TERMINÉE !")
        print("=" * 60)
        
        if has_docker:
            print("\n📋 PROCHAINES ÉTAPES:")
            print("1. Démarrez les services: ./start_services.sh (Linux/Mac) ou start_services.bat (Windows)")
            print("2. Attendez 2-3 minutes que tous les services démarrent")
            print("3. Lancez BIMEX BI: python start_bimex_bi.py")
            print("4. Testez: python test_opensource_bi.py")
        else:
            print("\n📋 INSTALLATION MANUELLE REQUISE:")
            print("1. Installez Docker et Docker Compose")
            print("2. Ou installez manuellement:")
            print("   - Apache Superset: pip install apache-superset")
            print("   - n8n: npm install -g n8n")
            print("   - ERPNext: https://github.com/frappe/bench")
            print("   - IFC.js: npm install ifc.js")
        
        print("\n🌐 URLS DES SERVICES:")
        print("📊 Superset:    http://localhost:8088")
        print("⚙️ n8n:         http://localhost:5678")
        print("🏢 ERPNext:     http://localhost:8000")
        print("🏗️ IFC Viewer:  http://localhost:3000")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
