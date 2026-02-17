#!/usr/bin/env python3
"""
Standalone Restore Script - Run when database is corrupted or app won't start.
Restores database from Google Cloud Storage without needing the main app.

Usage:
    python scripts/restore_from_gcs.py --bucket MY_BUCKET --credentials path/to/key.json
    python scripts/restore_from_gcs.py --bucket MY_BUCKET --credentials path/to/key.json --backup hospital_backup_20250101_120000.db

Environment alternative:
    set GOOGLE_APPLICATION_CREDENTIALS=path\to\key.json
    python scripts/restore_from_gcs.py --bucket MY_BUCKET
"""
import argparse
import json
import os
import sys

# Add project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.cloud_backup import GCSBackupService, is_gcs_available
from backend.database import get_app_data_dir


def main():
    parser = argparse.ArgumentParser(
        description="Restore hospital database from Google Cloud Storage"
    )
    parser.add_argument(
        "--bucket",
        required=True,
        help="GCS bucket name",
    )
    parser.add_argument(
        "--credentials",
        help="Path to service account JSON, or paste JSON string",
    )
    parser.add_argument(
        "--backup",
        help="Backup filename (e.g. hospital_backup_20250101_120000.db). If not set, lists backups.",
    )
    args = parser.parse_args()

    if not is_gcs_available():
        print("Error: Install google-cloud-storage: pip install google-cloud-storage")
        sys.exit(1)

    creds_json = None
    creds_path = None
    if args.credentials:
        if args.credentials.startswith("{"):
            try:
                creds_json = json.loads(args.credentials)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in --credentials")
                sys.exit(1)
        elif os.path.isfile(args.credentials):
            creds_path = args.credentials
        else:
            print(f"Error: Credentials file not found: {args.credentials}")
            sys.exit(1)
    elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    service = GCSBackupService(
        bucket_name=args.bucket,
        credentials_json=creds_json,
        credentials_path=creds_path,
    )

    if not args.backup:
        print("Available backups:")
        backups = service.list_backups()
        if not backups:
            print("  No backups found.")
            sys.exit(0)
        for b in backups:
            print(f"  - {b['name']} ({b.get('updated', 'unknown')})")
        print("\nRun with --backup <filename> to restore.")
        sys.exit(0)

    db_path = os.path.join(get_app_data_dir(), "hospital.db")
    tmp_path = db_path + ".restore_tmp"
    backup_path = args.backup
    if not backup_path.startswith("hospital-backups/"):
        backup_path = f"hospital-backups/{backup_path}"

    print(f"Downloading {backup_path}...")
    service.download_backup(backup_path, tmp_path)
    print(f"Restoring to {db_path}...")
    if os.path.exists(db_path):
        os.replace(tmp_path, db_path)
    else:
        os.rename(tmp_path, db_path)
    print("Restore complete. You can now start the application.")
    sys.exit(0)


if __name__ == "__main__":
    main()
