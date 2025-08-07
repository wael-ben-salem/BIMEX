"""
DAG Airflow pour l'analyse automatisée des fichiers BIM
Ce pipeline orchestre l'analyse complète des modèles BIM et l'export vers les plateformes BI
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.http import SimpleHttpOperator
from airflow.sensors.filesystem import FileSensor
import requests
import json
import os

# Configuration par défaut
default_args = {
    'owner': 'bimex-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email': ['admin@bimex.com']
}

# Définition du DAG
dag = DAG(
    'bim_analysis_pipeline',
    default_args=default_args,
    description='Pipeline complet d\'analyse BIM avec export BI',
    schedule_interval=timedelta(hours=6),  # Toutes les 6 heures
    catchup=False,
    max_active_runs=1,
    tags=['bim', 'analysis', 'bi-export']
)

# Configuration
BIMEX_API_URL = os.getenv('BIMEX_API_URL', 'http://host.docker.internal:8001')
UPLOAD_PATH = '/opt/airflow/data/uploads'
PROCESSED_PATH = '/opt/airflow/data/processed'

def scan_for_new_files(**context):
    """Scanner les nouveaux fichiers BIM à traiter"""
    import glob
    
    # Chercher les fichiers IFC, RVT, DWG non traités
    patterns = ['*.ifc', '*.IFC', '*.rvt', '*.RVT', '*.dwg', '*.DWG']
    new_files = []
    
    for pattern in patterns:
        files = glob.glob(os.path.join(UPLOAD_PATH, pattern))
        for file_path in files:
            # Vérifier si le fichier n'a pas déjà été traité
            processed_marker = os.path.join(PROCESSED_PATH, os.path.basename(file_path) + '.processed')
            if not os.path.exists(processed_marker):
                new_files.append(file_path)
    
    print(f"Nouveaux fichiers trouvés: {new_files}")
    
    # Stocker la liste dans XCom pour les tâches suivantes
    context['task_instance'].xcom_push(key='new_files', value=new_files)
    
    return len(new_files)

def upload_file_to_bimex(file_path, **context):
    """Uploader un fichier vers l'API BIMEX"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f'{BIMEX_API_URL}/upload',
                files=files,
                timeout=300
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Fichier uploadé avec succès: {result}")
            return result.get('project_id')
        else:
            raise Exception(f"Erreur upload: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erreur lors de l'upload: {e}")
        raise

def analyze_bim_file(project_id, **context):
    """Lancer l'analyse BIM via l'API"""
    try:
        response = requests.post(
            f'{BIMEX_API_URL}/analyze',
            data={'project_id': project_id},
            timeout=600  # 10 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Analyse terminée: {result}")
            
            # Stocker les résultats dans XCom
            context['task_instance'].xcom_push(key='analysis_result', value=result)
            return result
        else:
            raise Exception(f"Erreur analyse: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")
        raise

def export_to_superset(**context):
    """Exporter les données vers Apache Superset"""
    try:
        analysis_result = context['task_instance'].xcom_pull(key='analysis_result')
        project_id = analysis_result.get('project_id')
        
        response = requests.post(
            f'{BIMEX_API_URL}/bi/export-superset',
            data={'project_id': project_id},
            timeout=120
        )
        
        if response.status_code == 200:
            print("Export vers Superset réussi")
            return True
        else:
            print(f"Erreur export Superset: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erreur export Superset: {e}")
        return False

def update_grafana_metrics(**context):
    """Mettre à jour les métriques Grafana"""
    try:
        analysis_result = context['task_instance'].xcom_pull(key='analysis_result')
        
        # Simuler l'envoi de métriques à Grafana/Prometheus
        metrics = {
            'bim_analysis_total': 1,
            'bim_elements_count': analysis_result.get('building_metrics', {}).get('total_elements', 0),
            'bim_anomalies_count': analysis_result.get('anomaly_summary', {}).get('total_anomalies', 0),
            'bim_processing_time': analysis_result.get('processing_time', 0)
        }
        
        print(f"Métriques mises à jour: {metrics}")
        return True
        
    except Exception as e:
        print(f"Erreur mise à jour métriques: {e}")
        return False

def create_metabase_dashboard(**context):
    """Créer/mettre à jour le dashboard Metabase"""
    try:
        analysis_result = context['task_instance'].xcom_pull(key='analysis_result')
        project_id = analysis_result.get('project_id')
        
        # Simuler la création d'un dashboard Metabase
        dashboard_config = {
            'name': f'BIM Analysis - {project_id}',
            'description': 'Dashboard automatiquement généré pour l\'analyse BIM',
            'cards': [
                {'type': 'metric', 'title': 'Total Elements'},
                {'type': 'chart', 'title': 'Anomalies by Severity'},
                {'type': 'table', 'title': 'Element Details'}
            ]
        }
        
        print(f"Dashboard Metabase créé: {dashboard_config}")
        return True
        
    except Exception as e:
        print(f"Erreur création dashboard Metabase: {e}")
        return False

def trigger_n8n_workflow(**context):
    """Déclencher un workflow N8N pour les notifications"""
    try:
        analysis_result = context['task_instance'].xcom_pull(key='analysis_result')
        
        # Webhook N8N pour les notifications
        webhook_data = {
            'project_id': analysis_result.get('project_id'),
            'status': 'completed',
            'anomalies_count': analysis_result.get('anomaly_summary', {}).get('total_anomalies', 0),
            'quality_score': analysis_result.get('quality_score', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Simuler l'appel webhook N8N
        print(f"Webhook N8N déclenché: {webhook_data}")
        return True
        
    except Exception as e:
        print(f"Erreur déclenchement N8N: {e}")
        return False

def mark_file_as_processed(file_path, **context):
    """Marquer le fichier comme traité"""
    try:
        processed_marker = os.path.join(PROCESSED_PATH, os.path.basename(file_path) + '.processed')
        
        # Créer le dossier si nécessaire
        os.makedirs(PROCESSED_PATH, exist_ok=True)
        
        # Créer le fichier marqueur
        with open(processed_marker, 'w') as f:
            f.write(f"Processed at: {datetime.now().isoformat()}\n")
            
        print(f"Fichier marqué comme traité: {file_path}")
        return True
        
    except Exception as e:
        print(f"Erreur marquage fichier: {e}")
        return False

def cleanup_old_files(**context):
    """Nettoyer les anciens fichiers traités"""
    try:
        import glob
        import time
        
        # Supprimer les fichiers traités de plus de 30 jours
        cutoff_time = time.time() - (30 * 24 * 60 * 60)  # 30 jours
        
        processed_files = glob.glob(os.path.join(PROCESSED_PATH, '*.processed'))
        cleaned_count = 0
        
        for file_path in processed_files:
            if os.path.getmtime(file_path) < cutoff_time:
                os.remove(file_path)
                cleaned_count += 1
                
        print(f"Nettoyage terminé: {cleaned_count} fichiers supprimés")
        return cleaned_count
        
    except Exception as e:
        print(f"Erreur nettoyage: {e}")
        return 0

# Définition des tâches

# 1. Scanner les nouveaux fichiers
scan_files_task = PythonOperator(
    task_id='scan_for_new_files',
    python_callable=scan_for_new_files,
    dag=dag
)

# 2. Traitement conditionnel des fichiers (exemple pour un fichier)
# Dans un vrai scénario, on utiliserait un DynamicTaskMapping ou SubDAG

upload_task = PythonOperator(
    task_id='upload_file_to_bimex',
    python_callable=upload_file_to_bimex,
    op_kwargs={'file_path': '{{ ti.xcom_pull(key="new_files")[0] if ti.xcom_pull(key="new_files") else "" }}'},
    dag=dag
)

analyze_task = PythonOperator(
    task_id='analyze_bim_file',
    python_callable=analyze_bim_file,
    op_kwargs={'project_id': '{{ ti.xcom_pull(task_ids="upload_file_to_bimex") }}'},
    dag=dag
)

# 3. Export vers les plateformes BI (en parallèle)
export_superset_task = PythonOperator(
    task_id='export_to_superset',
    python_callable=export_to_superset,
    dag=dag
)

update_grafana_task = PythonOperator(
    task_id='update_grafana_metrics',
    python_callable=update_grafana_metrics,
    dag=dag
)

create_metabase_task = PythonOperator(
    task_id='create_metabase_dashboard',
    python_callable=create_metabase_dashboard,
    dag=dag
)

trigger_n8n_task = PythonOperator(
    task_id='trigger_n8n_workflow',
    python_callable=trigger_n8n_workflow,
    dag=dag
)

# 4. Finalisation
mark_processed_task = PythonOperator(
    task_id='mark_file_as_processed',
    python_callable=mark_file_as_processed,
    op_kwargs={'file_path': '{{ ti.xcom_pull(key="new_files")[0] if ti.xcom_pull(key="new_files") else "" }}'},
    dag=dag
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_files',
    python_callable=cleanup_old_files,
    dag=dag
)

# Définition des dépendances
scan_files_task >> upload_task >> analyze_task

# Export en parallèle vers toutes les plateformes BI
analyze_task >> [export_superset_task, update_grafana_task, create_metabase_task, trigger_n8n_task]

# Finalisation
[export_superset_task, update_grafana_task, create_metabase_task, trigger_n8n_task] >> mark_processed_task >> cleanup_task
