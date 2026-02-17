# Database Backup to Google Cloud Storage

Back up your hospital database to Google Cloud Storage so you can restore it if your account or data is lost.

---

## Setup

### 1. Create a Google Cloud bucket

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project (or use existing)
3. Open **Cloud Storage** → **Buckets** → **Create bucket**
4. Choose a name (e.g. `my-hospital-backups`) and region
5. Create the bucket

### 2. Create a service account key

1. Go to **IAM & Admin** → **Service Accounts**
2. **Create service account** — give it a name (e.g. `hospital-backup`)
3. Grant role: **Storage Object Admin** (to read/write objects)
4. **Keys** → **Add key** → **Create new key** → **JSON**
5. Download the JSON file and keep it secure

### 3. Install dependency

```bash
pip install google-cloud-storage
```

---

## Using the Web UI

1. Start the app (web or desktop)
2. Go to **☁️ Backup** in the navigation
3. Enter:
   - **Bucket name** — your GCS bucket
   - **Service account JSON** — paste the contents of your downloaded JSON key
4. **Upload Backup** — backs up the database to GCS
5. **List Backups** — shows available backups
6. **Restore** — picks a backup and restores (replaces current database)

---

## Crash recovery (standalone restore)

If the app won’t start (e.g. corrupted database), use the restore script:

```bash
# List available backups
python scripts/restore_from_gcs.py --bucket YOUR_BUCKET --credentials path/to/key.json

# Restore a specific backup
python scripts/restore_from_gcs.py --bucket YOUR_BUCKET --credentials path/to/key.json --backup hospital_backup_20250101_120000.db
```

Or with environment variable:

```bash
set GOOGLE_APPLICATION_CREDENTIALS=path\to\key.json
python scripts/restore_from_gcs.py --bucket YOUR_BUCKET --backup hospital_backup_20250101_120000.db
```

---

## Security notes

- Keep the service account JSON key private
- Do not commit it to version control
- Use a bucket with restricted access
- Credentials are only sent to the API for the duration of the request; they are not stored
