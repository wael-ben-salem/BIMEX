"""
Convertisseur RVT vers IFC
Utilise l'API Autodesk Platform Services (APS) pour convertir les fichiers Revit en IFC
"""

import os
import logging
import requests
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
import base64

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env non chargé, variables doivent être dans l'environnement

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class RVTConverter:
    def _upload_with_new_api(self, file_path: str, bucket_key: str, object_key: str) -> Optional[str]:
        """Upload avec la nouvelle API OSS v2 (signed URL)"""
        try:
            file_size = os.path.getsize(file_path)
            # 1. Obtenir une URL signée pour l'upload
            signed_url_endpoint = f"{self.base_url}/oss/v2/buckets/{bucket_key}/objects/{object_key}/signeds3upload"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(signed_url_endpoint, headers=headers)
            logger.info(f"📊 Signed URL response: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"❌ Erreur obtention URL signée: {response.status_code} - {response.text}")
                if response.status_code == 403 or "AUTH-012" in response.text:
                    logger.error("Votre compte Autodesk (trial/étudiant) ne permet pas la conversion RVT → IFC. Utilisez un compte payant ou exportez le RVT en IFC depuis Revit.")
                return None
            try:
                signed_data = response.json()
                logger.info(f"📊 Signed data: {signed_data}")
            except json.JSONDecodeError:
                logger.error(f"❌ Réponse non-JSON: {response.text}")
                return None
            urls = signed_data.get('urls', [])
            if not urls:
                logger.error("❌ Pas d'URL d'upload dans la réponse")
                return None
            upload_url = urls[0]
            upload_key = signed_data.get('uploadKey')
            if not upload_url or not upload_key:
                logger.error(f"❌ Pas d'URL d'upload ou uploadKey dans la réponse: {signed_data}")
                return None
            # 2. Upload avec l'URL signée
            with open(file_path, 'rb') as file:
                upload_response = requests.put(upload_url, data=file)
                logger.info(f"📊 Upload response: {upload_response.status_code}")
                if upload_response.status_code in [200, 201]:
                    # 3. Finaliser l'upload
                    complete_endpoint = f"{self.base_url}/oss/v2/buckets/{bucket_key}/objects/{object_key}/signeds3upload"
                    complete_data = {"uploadKey": upload_key}
                    complete_response = requests.post(complete_endpoint, headers=headers, json=complete_data)
                    if complete_response.status_code == 200:
                        object_id = f"urn:adsk.objects:os.object:{bucket_key}:{object_key}"
                        logger.info(f"✅ Fichier RVT uploadé (nouvelle API): {object_id}")
                        return object_id
                    else:
                        logger.error(f"❌ Erreur finalisation upload: {complete_response.status_code} - {complete_response.text}")
                        return None
                else:
                    logger.error(f"❌ Erreur upload: {upload_response.status_code} - {upload_response.text}")
                    return None
        except Exception as e:
            logger.error(f"❌ Erreur upload nouvelle API: {e}")
            return None
    def __init__(self):
        self.client_id = os.getenv('AUTODESK_CLIENT_ID')
        self.client_secret = os.getenv('AUTODESK_CLIENT_SECRET')
        self.access_token = None
        self.base_url = "https://developer.api.autodesk.com"
        self.offline_mode = os.getenv("RVT_OFFLINE_MODE", "false").lower() == "true"

        if self.offline_mode:
            logger.warning("⚠️ Mode hors ligne activé - conversion simulée")

        if not self.client_id or not self.client_secret:
            logger.warning("⚠️ Identifiants Autodesk APS non configurés - conversion désactivée")
            if not self.offline_mode:
                logger.info("💡 Pour activer la conversion : configurez AUTODESK_CLIENT_ID et AUTODESK_CLIENT_SECRET")

    def is_available(self) -> bool:
        return self.offline_mode or (self.client_id is not None and self.client_secret is not None)

    def _get_access_token(self) -> bool:
        url = f"{self.base_url}/authentication/v2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': 'data:read data:write data:create bucket:create bucket:read code:all viewables:read'
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                logger.info("✅ Token Autodesk obtenu")
                return True
            else:
                logger.error(f"❌ Échec obtention token : {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Exception lors de l'authentification : {e}")
            return False

    def _create_bucket_if_not_exists(self, bucket_key: str) -> bool:
        url = f"{self.base_url}/oss/v2/buckets"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "bucketKey": bucket_key.lower(),  # bucketKey doit être en minuscules
            "policyKey": "transient"          # policy "transient" = objets temporaires, peut être "persistent" ou "temporary"
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                logger.info(f"✅ Bucket '{bucket_key}' créé avec succès")
                return True
            elif response.status_code == 409:
                logger.info(f"✅ Bucket '{bucket_key}' existe déjà")
                return True
            else:
                logger.error(f"❌ Erreur création bucket : {response.status_code} {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Exception création bucket : {e}")
            return False


    def _upload_file(self, file_path: str, bucket_key: str, object_key: str) -> Optional[str]:
        """Upload le fichier RVT dans le bucket"""
        url = f"{self.base_url}/oss/v2/buckets/{bucket_key}/objects/{object_key}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/octet-stream'
        }
        try:
            with open(file_path, 'rb') as f:
                response = requests.put(url, headers=headers, data=f)
            if response.status_code in (200, 201):
                object_id = f"urn:adsk.objects:os.object:{bucket_key}:{object_key}"
                logger.info(f"✅ Fichier uploadé : {object_id}")
                return object_id
            else:
                logger.error(f"❌ Erreur upload fichier : {response.status_code} {response.text}")
                if response.status_code == 403:
                    logger.error("403 Forbidden - Vérifiez les permissions et scopes")
                return None
        except Exception as e:
            logger.error(f"❌ Exception upload fichier : {e}")
            return None

    def _start_conversion(self, urn: str) -> bool:
        url = f"{self.base_url}/modelderivative/v2/designdata/job"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        urn_b64 = base64.b64encode(urn.encode()).decode()
        payload = {
            "input": {
                "urn": urn_b64,
                "compressedUrn": False
            },
            "output": {
                "formats": [
                    {
                        "type": "ifc",
                        "views": ["3d"]
                    }
                ]
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in (200, 201):
                logger.info("✅ Conversion lancée")
                return True
            else:
                logger.error(f"❌ Erreur lancement conversion : {response.status_code} {response.text}")
                if response.status_code == 403 or "AUTH-012" in response.text:
                    logger.error("AUTH-012 : Votre compte/app ne possède pas les droits nécessaires.")
                return False
        except Exception as e:
            logger.error(f"❌ Exception lancement conversion : {e}")
            return False

    def _check_conversion_status(self, urn: str) -> Optional[str]:
        urn_b64 = base64.b64encode(urn.encode()).decode()
        url = f"{self.base_url}/modelderivative/v2/designdata/{urn_b64}/manifest"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                manifest = response.json()
                return manifest.get("status")
            else:
                logger.error(f"❌ Erreur check status : {response.status_code} {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Exception check status : {e}")
            return None

    def _download_ifc(self, urn: str, output_path: str) -> bool:
        urn_b64 = base64.b64encode(urn.encode()).decode()
        manifest_url = f"{self.base_url}/modelderivative/v2/designdata/{urn_b64}/manifest"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        try:
            response = requests.get(manifest_url, headers=headers)
            if response.status_code != 200:
                logger.error("❌ Impossible d'obtenir le manifest")
                return False
            manifest = response.json()
            # Cherche le fichier IFC
            ifc_urn = None
            for derivative in manifest.get("derivatives", []):
                if derivative.get("outputType") == "ifc":
                    ifc_urn = derivative.get("urn")
                    break
            if not ifc_urn:
                logger.error("❌ Fichier IFC non trouvé dans les dérivés")
                return False
            download_url = f"{self.base_url}/modelderivative/v2/designdata/{urn_b64}/manifest/{ifc_urn}"
            dl_resp = requests.get(download_url, headers=headers)
            if dl_resp.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(dl_resp.content)
                logger.info(f"✅ Fichier IFC téléchargé : {output_path}")
                return True
            else:
                logger.error(f"❌ Erreur téléchargement IFC : {dl_resp.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Exception téléchargement IFC : {e}")
            return False

    def convert_rvt_to_ifc(self, rvt_path: str, output_ifc_path: str,
                          progress_callback=None) -> Dict[str, Any]:
        if self.offline_mode:
            logger.info("🔄 Mode hors ligne activé, conversion simulée")
            if progress_callback:
                for i in range(0, 101, 20):
                    progress_callback(i, f"Simulation conversion {i}%")
                    time.sleep(0.3)
            with open(output_ifc_path, 'w') as f:
                f.write("ISO-10303-21; -- Simulated IFC file\n")
            return {"success": True, "message": "Conversion simulée", "output_file": output_ifc_path}

        if not self.is_available():
            return {"success": False, "error": "Identifiants APS manquants"}

        # 1. Authentification
        if progress_callback:
            progress_callback(5, "Authentification...")
        if not self._get_access_token():
            return {"success": False, "error": "Erreur authentification"}

        # 2. Création bucket
        bucket_key = "bimexconvert-bucket"
        if not self._create_bucket_if_not_exists(bucket_key):
            return {"success": False, "error": "Erreur création bucket"}

        # 3. Upload fichier
        file_name = Path(rvt_path).name
        object_key = f"{int(time.time())}_{file_name}"
        if progress_callback:
            progress_callback(20, "Upload du fichier...")
        object_id = self._upload_with_new_api(rvt_path, bucket_key, object_key)
        if not object_id:
            return {"success": False, "error": "Erreur upload fichier"}

        # 4. Démarrer conversion
        if progress_callback:
            progress_callback(40, "Démarrage conversion...")
        if not self._start_conversion(object_id):
            return {"success": False, "error": "Erreur lancement conversion"}

        # 5. Attente conversion
        if progress_callback:
            progress_callback(50, "Conversion en cours...")
        max_wait = 600
        start = time.time()
        while True:
            status = self._check_conversion_status(object_id)
            if status == "success":
                break
            elif status == "failed":
                return {"success": False, "error": "Conversion échouée"}
            elif time.time() - start > max_wait:
                return {"success": False, "error": "Timeout conversion"}
            if progress_callback:
                progress_callback(50 + (time.time()-start)/max_wait*40, f"Conversion: {status}")
            time.sleep(10)

        # 6. Télécharger IFC
        if progress_callback:
            progress_callback(90, "Téléchargement fichier IFC...")
        if self._download_ifc(object_id, output_ifc_path):
            if progress_callback:
                progress_callback(100, "Conversion terminée")
            return {"success": True, "message": "Conversion réussie", "output_file": output_ifc_path}
        else:
            return {"success": False, "error": "Erreur téléchargement IFC"}
