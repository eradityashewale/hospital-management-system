"""
Google Cloud Storage Backup Service
Handles database backup upload, list, and restore from GCS
"""
import os
import json
import tempfile
from typing import List, Dict, Optional
from datetime import datetime

from utils.logger import log_info, log_error, log_warning


def _ensure_gcs_available() -> bool:
    """Check if google-cloud-storage is installed."""
    try:
        from google.cloud import storage  # noqa: F401
        return True
    except ImportError:
        return False


def _get_storage_client(credentials_json: Optional[dict] = None,
                        credentials_path: Optional[str] = None):
    """Create GCS client from credentials."""
    from google.cloud import storage
    from google.oauth2 import service_account

    if credentials_json:
        credentials = service_account.Credentials.from_service_account_info(
            credentials_json
        )
        return storage.Client(credentials=credentials)
    if credentials_path and os.path.isfile(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        return storage.Client(credentials=credentials)
    # Use default credentials (e.g. GOOGLE_APPLICATION_CREDENTIALS env var)
    return storage.Client()


class GCSBackupService:
    """Service for uploading and downloading database backups to/from GCS."""

    BUCKET_PREFIX = "hospital-backups"

    def __init__(self, bucket_name: str,
                 credentials_json: Optional[dict] = None,
                 credentials_path: Optional[str] = None):
        self.bucket_name = bucket_name
        self.credentials_json = credentials_json
        self.credentials_path = credentials_path
        self._client = None

    def _get_client(self):
        """Lazy-init GCS client."""
        if self._client is None:
            self._client = _get_storage_client(
                self.credentials_json,
                self.credentials_path
            )
        return self._client

    def upload_backup(self, local_path: str,
                     remote_name: Optional[str] = None) -> str:
        """Upload a backup file to GCS. Returns the remote object name."""
        if not os.path.isfile(local_path):
            raise FileNotFoundError(f"Backup file not found: {local_path}")

        client = self._get_client()
        bucket = client.bucket(self.bucket_name)
        blob_name = remote_name or os.path.basename(local_path)
        blob_path = f"{self.BUCKET_PREFIX}/{blob_name}"
        blob = bucket.blob(blob_path)

        log_info(f"Uploading backup to gs://{self.bucket_name}/{blob_path}")
        blob.upload_from_filename(local_path, content_type="application/x-sqlite3")
        log_info("Backup uploaded successfully")
        return blob_path

    def list_backups(self) -> List[Dict]:
        """List all backup files in the bucket."""
        client = self._get_client()
        bucket = client.bucket(self.bucket_name)
        blobs = bucket.list_blobs(prefix=f"{self.BUCKET_PREFIX}/")

        backups = []
        for blob in blobs:
            if blob.name.endswith(".db") or blob.name.endswith(".db.bak"):
                backups.append({
                    "name": blob.name.split("/")[-1],
                    "full_path": blob.name,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "size": blob.size or 0,
                })
        backups.sort(key=lambda x: x.get("updated") or "", reverse=True)
        return backups

    def download_backup(self, remote_path: str, local_path: str) -> None:
        """Download a backup file from GCS to local path."""
        client = self._get_client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(remote_path)
        log_info(f"Downloading backup from gs://{self.bucket_name}/{remote_path}")
        blob.download_to_filename(local_path)
        log_info("Backup downloaded successfully")


def create_backup_filename() -> str:
    """Generate a timestamped backup filename."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"hospital_backup_{ts}.db"


def is_gcs_available() -> bool:
    """Check if Google Cloud Storage is available."""
    return _ensure_gcs_available()
