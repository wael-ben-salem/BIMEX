BIMEX / xeokit-convert2 — Documentation complète du projet

## Vue d’ensemble

Plateforme complète d’analyse et de visualisation BIM combinant :
- Backend FastAPI pour l’ingestion IFC/RVT, l’analyse (ifcopenshell), la détection d’anomalies, la classification, l’analyse PMR, les coûts/environnement/analytics avancés, et la génération de rapports (HTML/PDF).
- Frontend Mission Control (`frontend/bim_analysis.html`) pour piloter les analyses, afficher les résultats, ouvrir le rapport, etc.
- Viewer xeokit (`xeokit-bim-viewer/app/home.html`) pour parcourir les projets et afficher les modèles (`geometry.ifc`, `geometry.xkt`).

## Périmètre et architecture

- `backend/` (API, analyses, génération rapports)
- `frontend/` (interface Mission Control)
- `xeokit-bim-viewer/app/` (explorateur de projets et viewer 3D)
- Orchestration optionnelle via Airflow (`airflow/dags/bim_analysis_pipeline.py`)
- Conversion et utilitaires xeokit (`convert2xkt.js`, `src/`, `package.json`)

## Outils et stack utilisés

### Backend (Python)
- FastAPI, Uvicorn: API HTTP et serveur ASGI
- ifcopenshell: parsing IFC, extraction surfaces/volumes/étages/espaces, matériaux, propriétés
- numpy, pandas, scipy: calculs numériques, transformations et statistiques
- scikit-learn: RandomForestClassifier/Regressor, KMeans, PCA, IsolationForest, DBSCAN (via modules)
- matplotlib, seaborn, plotly: graphiques (PDF/images et usages éventuels)
- reportlab, fpdf2, python-docx: génération PDF/Docs (rapports)
- jinja2: templates HTML (ex: `backend/templates/report_template.html`)
- weasyprint, playwright (+ nest-asyncio): génération PDF depuis HTML (fallback/alternative)
- python-multipart, aiofiles: uploads et fichiers
- requests, python-dotenv: HTTP et configuration
- python-jose[cryptography], passlib[bcrypt]: JWT/Auth si nécessaire
- langchain, openai, langchain-openai: assistants/IA éventuels (modules `bim_assistant*`)

Note compatibilité: `ifcopenshell` peut être incompatible avec Python 3.13 (voir commentaire dans `backend/requirements.txt`). Des fallbacks existent (ex: `IFCAnalyzerFallback`).

### Frontend (HTML/CSS/JS)
- Pages statiques avec styles personnalisés (Google Fonts, Font Awesome)
- Intégrations UI: widgets, grilles, cartes, tableaux, indicateurs
- Chart.js (via `report_template.html`), fallbacks texte pour l’export impression/PDF

### Viewer / Conversion (Node.js)
- xeokit et loaders.gl (GLTF/OBJ/PLY/LAZ, textures, images, JSON)
- `web-ifc` côté JS
- CLI `convert2xkt.js` et configuration `convert2xkt.conf.{js,json}`

### Orchestration & BI (optionnel)
- Airflow: pipeline d’analyse/exports
- Connecteurs BI (dans `backend/bi_integration.py`): Superset, IFC.js, n8n, ERPNext

## Pages et composants

### `frontend/bim_analysis.html` (Mission Control)
- En-tête futuriste et branding BIMEX
- Zone d’upload (RVT/IFC), drag&drop, boutons d’action:
  - Analyze file / Détecter anomalies / Classifier / Analyse PMR
  - Générer Rapport (ouvre `/report-view/{id}`) / Télécharger PDF
- Indicateurs et métriques:
  - Cartes métriques (surfaces, volumes, ratios), barres de progression
  - Résultats anomalies par sévérité (critique/élevée/moyenne/faible)
  - Zone de chat/assistant (intégration IA)
- Mission Control Dashboard et Workflow Panel:
  - Boutons d’exécution, pause, stop, progression, statut
  - Grille de contrôles (coûts, environnement, optimisation, anomalies…)
- Effets UI: animations, overlays, loaders

Fonctionnement côté page:
- Appels aux endpoints du backend pour lancer chaque analyse et afficher les retours JSON (métriques, anomalies, recommandations, scores, etc.).

### `xeokit-bim-viewer/app/home.html` (Viewer & Projets)
- En-tête et arrière-plan animé, thème sombre BIMEX 2.0
- Sections:
  - Barre de recherche, “Add model” (CTA), statut système
  - Grille de projets (cards): titre, id, actions principales
  - Action menu contextuel (ouvrir, analyser, exporter, etc.)
  - Actions modal (dialog centralisé)
  - BI Dashboard (panneau plein écran), widgets BI (cartes, statistiques, effets)
- Objectif: Naviguer dans `data/projects/<Project>/models/model/geometry.(ifc|xkt)`, ouvrir le viewer, déclencher actions (analyse/rapport via API)

### `backend/templates/report_template.html` (Rapport HTML)
- Header rapport (titre, sous-titre, date, modèle), boutons “Télécharger PDF” et “Imprimer”
- Scores BIMEX (qualité, complexité, efficacité) avec barres
- Analyse IA BIMEX (emoji/note/score, recommandations, indicateurs primaires, facteurs de confiance, patterns neuronaux)
- Conformité PMR (score, statut, barre, nb de contrôles)
- Résumé exécutif (surfaces totales, étages, espaces, anomalies, PMR)
- Informations projet (table: noms, schéma IFC, type, confiance IA, éléments, taille)
- Classification Intelligente (type/fr, confiance, indicateurs)
- Métriques Bâtiment (surfaces/volumes/organisation spatiale/ratios avancés)
- Analyse des Anomalies (tableau par sévérité + petit graphe Chart.js avec fallback print)
- Statistiques avancées BIMEX (anomalies prioritaires, criticité, urgences, visualisation)
- Listes: problèmes fréquents, anomalies prioritaires à corriger (avec détails)
- Technique: Jinja2 pour les variables du backend (exemples récurrents vues dans le template)

Variables Jinja principales utilisées (exemples): `filename`, `date`, `quality_score`, `complexity_score`, `efficiency_score`, `ai_emoji`, `ai_color`, `ai_grade`, `ai_score`, `ai_recommendations`, `pmr_score`, `pmr_color`, `pmr_status`, `pmr_total_checks`, `project_name`, `building_name`, `schema_ifc`, `building_type`, `building_confidence`, `classification_method`, `total_elements`, `file_size`, `ai_primary_indicators`, `ai_confidence_factors`, `ai_neural_patterns`, `floor_surfaces`, `wall_surfaces`, `window_surfaces`, `door_surfaces`, `roof_surfaces`, `structural_surfaces`, `total_floor_area`, `space_volumes`, `structural_volumes`, `total_volumes`, `total_storeys`, `total_spaces`, `space_types`, `window_wall_ratio`, `spatial_efficiency`, `building_compactness`, `space_density`, `critical_anomalies`, `high_anomalies`, `medium_anomalies`, `low_anomalies`, `critical_percentage`, `high_percentage`, `medium_percentage`, `low_percentage`, `priority_anomalies`, etc.

## Backend API — endpoints clés

- POST `/upload`: upload IFC et enregistrement projet
- POST `/upload-rvt`: upload d’un RVT, délégation conversion pyRevit (RVT→IFC), puis IFC→XKT et indexation
- GET `/generate-html-report?auto=true&project=<id>&file_detected=true`: génère un rapport depuis le projet et redirige vers `/report-view/{id}`
- GET `/report-view/{report_id}`: rend le template `report_template.html`
- GET `/api/download-pdf/{report_id}`: PDF via WeasyPrint/Playwright
- POST `/api/export/{project_id}/{kind}`: `csv`, `parquet`, `features`, `dataset-ml`, `neo4j`, `geojson` (avec `persist=true` pour écrire dans le projet)
- Analyses: `POST /analyze-ifc` et/ou `GET /analyze-comprehensive-project/{project}` selon vos flux

Notes de flux RVT → IFC → XKT:
- `process_rvt_with_pyrevit(...)` dépose le RVT dans `C:\RVT_WATCH_FOLDER`, attend l’IFC, copie dans le projet, lance la conversion IFC→XKT, puis met à jour l’index des projets.
- CORS activé pour accès frontend.

## Modules Python et techniques de data science

- `backend/ifc_analyzer.py` — IFCAnalyzer
  - Chargement IFC sécurisé, extraction: infos projet, surfaces (planchers/murs/toitures/ouvrants), volumes (espaces/structure), étages (tri par élévation), espaces (types/aire/volume), éléments structurels (poutres, poteaux, murs, dalles, fondations) et matériaux.
  - Utilise `ifcopenshell.util.*`, numpy/pandas, garde-fous d’erreurs et diagnostics.

- `backend/anomaly_detector.py` — IFCAnomalyDetector
  - Règles et heuristiques: propriétés manquantes (matériaux, nom), incohérences géométriques (dimensions ≤ 0), hauteurs d’étage atypiques, matériaux génériques/inappropriés, connectivité (portes/fenêtres non rattachées, espaces non bornés), nommage dupliqué, classification manquante, structure (poutres sans support).
  - Enum `AnomalySeverity`, dataclass `Anomaly`.

- `backend/building_classifier.py` — BuildingClassifier + BIMEXIntelligentClassifier
  - ML: RandomForestClassifier, KMeans, PCA, StandardScaler, LabelEncoder
  - Système IA basé sur base de connaissances + patterns neuronaux (indicateurs primaires, facteurs de confiance, patterns géométriques/spatiaux)
  - Sorties: type de bâtiment (fr), confiance, indicateurs IA, résumé d’entraînement

- `backend/environmental_analyzer.py` — EnvironmentalAnalyzer
  - ML/Stats: RandomForestRegressor, IsolationForest, KMeans, DBSCAN, MinMax/Standard Scalers, optimisation (scipy.optimize), analyses de sensibilité/Monte Carlo, comparaisons standards
  - Calculs: empreinte carbone par matériaux, performance énergétique (fenêtres/murs, enveloppe), eau, recyclabilité, confort thermique, potentiel renouvelable, scoring de durabilité, recommandations IA

- `backend/advanced_cost_analyzer.py` — AdvancedCostAnalyzer
  - Base coûts matériaux/éléments (ajustée tendance marché), estimation quantités, regroupements ML, coût total et par m², sensibilité, recommandations d’optimisation

- `backend/advanced_analytics.py` — AdvancedAnalytics
  - Maintenance prédictive (durées de vie, priorités), benchmarks par type, performance globale (structure/énergie/espace/accessibilité), IsolationForest pour anomalies avancées, tendances et projections, score de qualité global

- `backend/report_generator.py` — BIMReportGenerator
  - Génère des PDF enrichis via ReportLab (styles sur-mesure, en-têtes/pieds, sections analytiques, annexes). Intègre données d’IFCAnalyzer, AnomalyDetector, PMRAnalyzer (si dispo), BuildingClassifier.

### Autres modules notables
- `backend/pmr_analyzer.py` — Vérifications PMR selon normes FR (largeurs portes/couloirs/escaliers, pentes rampes, ascenseurs, WC…), niveaux de conformité et recommandations. Sorties sérialisables et résumé global.
- `backend/ai_optimizer.py` — Optimiseur IA multi-objectifs (énergie, coût, structure, environnement, confort), recommandations priorisées, Pareto, Monte Carlo, graphes de connectivité, algorithmes (RandomForest, GBoosting, MLP, KMeans, optimisation différentielle, CFD/heuristiques).
- `backend/comprehensive_ifc_analyzer.py` — Orchestrateur combinant métriques, anomalies, classification, PMR, avec résumé consolidé et scores.
- `backend/bi_integration.py` — Gestionnaire BI (connecteurs PowerBI/Tableau/n8n/ERP, extraction métriques prêtes BI, scores de complétude/qualité, persistance config `bi_config.json`).
- `backend/cost_predictor.py` — Prédicteur de coûts avec base matériaux/éléments, agrégations, ML (RandomForest), sensibilité, recommandations d’optimisation, coûts par m².

## Conversion & Viewer (Node.js)

- `package.json` (racine): dépendances principales pour conversion/affichages (loaders.gl, web-ifc, pako, Font Awesome). Scripts: `docs`, `types`.
- CLI `convert2xkt.js`: conversion IFC → XKT (config via `convert2xkt.conf.js|json`).
- `src/` contient les utilitaires JS utilisés par la conversion et le viewer.

## Installation & démarrage

### Backend (Python 3.10–3.12 recommandé)
```
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
- Ouvrir `frontend/bim_analysis.html` dans un navigateur (ou servir statiquement)
- Ouvrir `xeokit-bim-viewer/app/home.html` pour le viewer/projets
- Assurez-vous que l’UI cible `http://localhost:8001` pour l’API

### Airflow (optionnel)
- `airflow/dags/bim_analysis_pipeline.py`: scan des uploads, déclenchement analyses backend, persistance GeoJSON par projet

## Exports & Données

- Exports par `/api/export/{project_id}/{kind}`: CSV, Parquet, Features, Dataset ML, Neo4j (CSV), GeoJSON
- GeoJSON: peut être retourné ou persisté dans le projet en `geometry.geojson` (pour usages carto/BI)

## Sécurité & Auth

- JWT via `python-jose`, mots de passe via `passlib[bcrypt]` (si activé)
- Variables d’environnement gérées par `.env` (voir `backend/env_example.txt`)

## Compatibilité & limitations

- ifcopenshell: versions à aligner avec votre Python (éviter 3.13 selon note). En absence, fallback prévu et/ou analyses simulées.
- Conversion RVT → IFC nécessite un environnement Revit/pyRevit local et un dossier surveillé `C:\RVT_WATCH_FOLDER`.

## Flux d’utilisation type

- Mode Projet: ouvrir Mission Control, cliquer “Générer Rapport Complet” ou “Rapport PDF”
  - `/generate-html-report?auto=true&project=<Project>&file_detected=true` → redirection `/report-view/{id}`
- Mode Upload: charger un IFC (ou RVT via `/upload-rvt`), exécuter analyses, ouvrir le rapport
- PDF: depuis la page rapport “Télécharger PDF” (WeasyPrint/Playwright)

## Dépannage rapide

- Rapport non généré: vérifier que l’IFC existe pour le projet et que l’analyse renvoie des données. Utiliser l’analyse dynamique de secours si nécessaire.
- PDF: installer WeasyPrint/Playwright selon votre OS. En mode print, les fallbacks texte Chart.js s’affichent.
- Conversion RVT→IFC: vérifier pyRevit, droits d’accès et `C:\RVT_WATCH_FOLDER`.

## Licence

Voir `LICENSE`.

BIMEX Platform – Architecture, Setup, and Usage

Overview

BIMEX is a full-stack BIM analysis and visualization platform:
- Backend (`backend/`): FastAPI service for IFC ingestion, analysis (ifcopenshell), anomaly detection, PMR checks, reporting (HTML + WeasyPrint PDF), analytics and exports (CSV, Parquet, Neo4j, GeoJSON).
- Viewer (`xeokit-bim-viewer/`): xeokit-based web viewer hosting projects and models (`geometry.ifc`, `geometry.xkt`).
- Frontend (`frontend/`): Mission Control dashboard (`bim_analysis.html`) with rich UX (analysis, anomalies, classification, PMR, PDF reports) and integrations.

Key Features

- Real IFC analysis via ifcopenshell: surfaces, volumes, storeys, spaces, elements, materials
- Anomaly detection and summary by severity/type
- PMR accessibility analysis (summary, compliance bars, recommendations)
- Dynamic building classification and training details
- HTML Report with `backend/templates/report_template.html` and PDF via WeasyPrint
- Exports: CSV/Parquet/Neo4j/GeoJSON (spatial points) per project
- Airflow pipeline step to generate and persist GeoJSON
- Mission Control UI: analysis, PMR, classification, cost/env/opt widgets; BIMEX loading overlays

Repository Structure

- `backend/`
  - `main.py`: FastAPI API; analysis endpoints; report generation (`/generate-html-report`, `/report-view/{id}`, `/api/download-pdf/{id}`); exports; GeoJSON generation; dynamic building analysis fallback.
  - `ifc_analyzer.py`, `anomaly_detector.py`, `pmr_analyzer.py`, `advanced_analytics.py`, `ai_optimizer.py`, `environmental_analyzer.py`: analysis modules using ifcopenshell.
  - `templates/report_template.html`: full HTML report template rendered by `/report-view/{id}`.
  - `generatedReports/`: output PDFs (if used by some flows).
- `frontend/`
  - `bim_analysis.html`: Mission Control UI (buttons for analysis, PMR, classification, report, PDF; BIMEX overlays; charts; widgets).
- `xeokit-bim-viewer/app/`
  - `home.html`: viewer UI entry
  - `data/projects/<Project>/models/model/geometry.ifc|geometry.xkt`: project data

Backend – Notable Endpoints

- `POST /upload`: upload IFC and register a project
- `POST /analyze-ifc` or `GET /analyze-comprehensive-project/{project}`: full analysis
- `GET /generate-html-report?auto=true&project=<id>&file_detected=true`: generate report from project IFC and redirect to `/report-view/{id}`
- `GET /report-view/{report_id}`: render `report_template.html`
- `GET /api/download-pdf/{report_id}`: generate PDF via WeasyPrint
- `POST /api/export/{project_id}/{kind}`: `csv`, `parquet`, `features`, `dataset-ml`, `neo4j`, `geojson`
  - GeoJSON: returns FeatureCollection of 3D points (IfcSpace, IfcWall, …); persisted as `geometry.geojson` when `persist=true`

Frontend – Mission Control (`frontend/bim_analysis.html`)

- Detects project (auto mode) or accepts upload
- Buttons:
  - Analyze file, Detect anomalies, Classify building, PMR analysis
  - Generate Report: shows BIMEX overlay, calls backend to open `/report-view/{id}`
  - Rapport PDF: opens report view; PDF button in the report triggers WeasyPrint download
- Widgets: BIM scores, charts, PMR summary, recommendations, costs, environment, optimization

Viewer – xeokit (`xeokit-bim-viewer/app/`)

- `home.html` and project structure under `data/projects/` (each with `index.json` and `models/model/geometry.*`)
- Compatible with the Mission Control flows for auto mode (project-based analysis/report)

Setup

1) Python backend
- Python 3.10–3.12 recommended
- Install dependencies:
```
pip install -r backend/requirements.txt
```
- Run backend:
```
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

2) Frontend
- Serve `frontend/` and `xeokit-bim-viewer/app/` statically (local file or simple HTTP server)
- Ensure the UI points to `http://localhost:8001` for API calls

Airflow (optional)

- Included DAG (`airflow/dags/bim_analysis_pipeline.py`) scans uploads, triggers backend analysis, and persists GeoJSON export for each project.

Data Science & Tech Stack

- ifcopenshell (IFC parsing/metrics), numpy/pandas (data shaping), matplotlib (chart images for PDFs)
- FastAPI (backend), WeasyPrint (PDF), Airflow (orchestration), xeokit (viewer)
- Exports: CSV, Parquet (pyarrow), Neo4j CSV, GeoJSON

Security & Cleanup Notes

- This cleaned distribution removes stray test scripts and artifacts (e.g., `tests/index.js`, `images/!DOCTYPE html.txt`).
- No test runners or dev-only secrets included in this trimmed version; ensure environment variables are managed securely if added.

Usage – Common Flows

- Auto project: open Mission Control and click “Générer Rapport Complet” or “Rapport PDF”
  - Navigates to: `http://localhost:8001/generate-html-report?auto=true&project=<Project>&file_detected=true`
  - Then: `/report-view/{report_id}` renders dynamic report from the actual `geometry.ifc`
- From file upload: use Mission Control upload, then Generate Report → opens `/report-view/{report_id}`
- PDF: from the report page, use “Télécharger PDF” (WeasyPrint)

Troubleshooting

- If `/generate-html-report` fails with a missing function, the fallback `analyze_building_dynamically` in `main.py` provides a robust dynamic analysis.
- If PDF errors occur, ensure WeasyPrint is installed and accessible; the template embeds chart images when needed.


