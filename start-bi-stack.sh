#!/bin/bash

# Script de démarrage pour la stack BI BIMEX
# Ce script lance tous les services nécessaires pour le dashboard enrichi

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé. Veuillez installer Docker avant de continuer."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé. Veuillez installer Docker Compose avant de continuer."
        exit 1
    fi
    
    log_success "Docker et Docker Compose sont installés"
}

# Créer les dossiers nécessaires
create_directories() {
    log_info "Création des dossiers nécessaires..."
    
    mkdir -p config/grafana/dashboards
    mkdir -p config/grafana/datasources
    mkdir -p airflow/dags
    mkdir -p airflow/logs
    mkdir -p airflow/plugins
    mkdir -p n8n/workflows
    mkdir -p notebooks/samples
    mkdir -p notebooks/templates
    
    log_success "Dossiers créés avec succès"
}

# Créer les fichiers de configuration manquants
create_config_files() {
    log_info "Création des fichiers de configuration..."
    
    # Configuration Grafana datasource
    cat > config/grafana/datasources/datasource.yml << EOF
apiVersion: 1

datasources:
  - name: PostgreSQL-BIM
    type: postgres
    url: postgres:5432
    database: bim_data
    user: bim_user
    secureJsonData:
      password: bim_password
    jsonData:
      sslmode: disable
      postgresVersion: 1300
    isDefault: true
    
  - name: BIMEX-API
    type: prometheus
    url: http://host.docker.internal:8000/metrics
    access: proxy
    isDefault: false
EOF

    # Dashboard Grafana pour BIM
    cat > config/grafana/dashboards/bim-overview.json << EOF
{
  "dashboard": {
    "id": null,
    "title": "BIM Overview Dashboard",
    "tags": ["bim", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Total Projects",
        "type": "stat",
        "targets": [
          {
            "expr": "count(bim_projects)",
            "refId": "A"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      }
    ],
    "time": {"from": "now-24h", "to": "now"},
    "refresh": "5s"
  }
}
EOF

    log_success "Fichiers de configuration créés"
}

# Initialiser Airflow
init_airflow() {
    log_info "Initialisation d'Airflow..."
    
    # Créer le DAG d'exemple pour BIM
    cat > airflow/dags/bim_analysis_dag.py << EOF
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'bimex',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bim_analysis_pipeline',
    default_args=default_args,
    description='Pipeline d\'analyse BIM automatisé',
    schedule_interval=timedelta(hours=1),
    catchup=False,
)

def analyze_bim_files():
    print("Analyse des fichiers BIM en cours...")
    # Logique d'analyse ici
    return "Analyse terminée avec succès"

analyze_task = PythonOperator(
    task_id='analyze_bim_files',
    python_callable=analyze_bim_files,
    dag=dag,
)

export_task = BashOperator(
    task_id='export_to_bi',
    bash_command='echo "Export vers les plateformes BI terminé"',
    dag=dag,
)

analyze_task >> export_task
EOF

    log_success "Airflow initialisé"
}

# Créer des notebooks Jupyter d'exemple
create_jupyter_notebooks() {
    log_info "Création des notebooks Jupyter d'exemple..."
    
    cat > notebooks/templates/bim_analysis_starter.ipynb << EOF
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# BIM Analysis Starter\n",
    "\n",
    "Ce notebook vous aide à démarrer l'analyse de vos fichiers BIM."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import requests\n",
    "\n",
    "# Configuration BIMEX\n",
    "BIMEX_API_URL = 'http://host.docker.internal:8000'\n",
    "\n",
    "print('Notebook BIM Analysis prêt!')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF

    log_success "Notebooks Jupyter créés"
}

# Démarrer les services
start_services() {
    log_info "Démarrage des services BI..."
    
    # Arrêter les services existants
    docker-compose -f docker-compose-bi.yml down
    
    # Démarrer les services
    docker-compose -f docker-compose-bi.yml up -d
    
    log_success "Services BI démarrés"
}

# Attendre que les services soient prêts
wait_for_services() {
    log_info "Attente du démarrage des services..."
    
    services=(
        "http://localhost:5678:N8N"
        "http://localhost:8088:Superset"
        "http://localhost:8080:Airflow"
        "http://localhost:3000:Grafana"
        "http://localhost:3001:Metabase"
        "http://localhost:8888:JupyterHub"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        log_info "Vérification de $name..."
        
        max_attempts=30
        attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302\|401"; then
                log_success "$name est prêt"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_warning "$name n'est pas encore prêt après $max_attempts tentatives"
            else
                sleep 10
                ((attempt++))
            fi
        done
    done
}

# Afficher les informations de connexion
show_connection_info() {
    log_info "Informations de connexion:"
    echo ""
    echo "🔗 Services disponibles:"
    echo "  • N8N Workflows:      http://localhost:5678 (admin/bimex2024)"
    echo "  • Apache Superset:    http://localhost:8088 (admin/bimex2024)"
    echo "  • Apache Airflow:     http://localhost:8080 (admin/admin)"
    echo "  • Grafana:            http://localhost:3000 (admin/bimex2024)"
    echo "  • Metabase:           http://localhost:3001 (Configuration initiale requise)"
    echo "  • JupyterHub:         http://localhost:8888 (admin/bimex2024)"
    echo ""
    echo "📊 Dashboard principal: http://localhost:8000"
    echo ""
    echo "🐳 Pour voir les logs: docker-compose -f docker-compose-bi.yml logs -f [service]"
    echo "🛑 Pour arrêter:       docker-compose -f docker-compose-bi.yml down"
}

# Fonction principale
main() {
    echo "🚀 Démarrage de la stack BI BIMEX"
    echo "=================================="
    
    check_docker
    create_directories
    create_config_files
    init_airflow
    create_jupyter_notebooks
    start_services
    wait_for_services
    show_connection_info
    
    log_success "Stack BI BIMEX démarrée avec succès!"
}

# Gestion des arguments
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        log_info "Arrêt des services BI..."
        docker-compose -f docker-compose-bi.yml down
        log_success "Services arrêtés"
        ;;
    restart)
        log_info "Redémarrage des services BI..."
        docker-compose -f docker-compose-bi.yml down
        sleep 5
        docker-compose -f docker-compose-bi.yml up -d
        log_success "Services redémarrés"
        ;;
    logs)
        docker-compose -f docker-compose-bi.yml logs -f
        ;;
    status)
        docker-compose -f docker-compose-bi.yml ps
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status}"
        echo ""
        echo "  start   - Démarrer tous les services BI"
        echo "  stop    - Arrêter tous les services BI"
        echo "  restart - Redémarrer tous les services BI"
        echo "  logs    - Afficher les logs en temps réel"
        echo "  status  - Afficher le statut des services"
        exit 1
        ;;
esac
