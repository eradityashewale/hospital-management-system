/**
 * Backup & Restore (Google Cloud Storage) Module
 */

const BackupAPI = {
    getStatus: () => apiCall('/backup/gcs/status'),
    upload: (data) => apiCall('/backup/gcs/upload', 'POST', data),
    list: (data) => apiCall('/backup/gcs/list', 'POST', data),
    restore: (data) => apiCall('/backup/gcs/restore', 'POST', data),
};

function showBackup() {
    setActiveNav('backup');
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="card">
            <h2>☁️ Cloud Backup & Restore</h2>
            <p style="color: var(--gray-600); margin-bottom: var(--spacing-lg);">
                Backup your database to Google Cloud Storage. If your account crashes, connect with your GCS credentials and restore.
            </p>
            <div id="backup-status"></div>
            <div id="backup-form" style="margin-top: var(--spacing-lg);"></div>
            <div id="backup-list" style="margin-top: var(--spacing-xl);"></div>
        </div>
    `;
    loadBackupStatus();
}

async function loadBackupStatus() {
    const el = document.getElementById('backup-status');
    try {
        const res = await BackupAPI.getStatus();
        const available = res.gcs_available;
        el.innerHTML = `
            <div class="alert ${available ? 'alert-success' : 'alert-warning'}">
                ${available
                    ? '✅ Google Cloud Storage is ready. Configure below to backup and restore.'
                    : '⚠️ Install google-cloud-storage: <code>pip install google-cloud-storage</code>'}
            </div>
        `;
        if (available) {
            renderBackupForm();
        }
    } catch (e) {
        el.innerHTML = `<div class="alert alert-error">Failed to check status: ${e.message}</div>`;
    }
}

function renderBackupForm() {
    const formEl = document.getElementById('backup-form');
    const listEl = document.getElementById('backup-list');
    formEl.innerHTML = `
        <div class="card" style="background: var(--gray-50); padding: var(--spacing-lg);">
            <h3 style="margin-bottom: var(--spacing-md);">Configuration</h3>
            <div style="display: flex; flex-direction: column; gap: var(--spacing-md); max-width: 480px;">
                <div>
                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">Bucket Name</label>
                    <input type="text" id="backup-bucket" placeholder="my-hospital-backups" class="input">
                </div>
                <div>
                    <label style="display: block; font-weight: 500; margin-bottom: 4px;">Service Account JSON</label>
                    <textarea id="backup-credentials" rows="6" placeholder='Paste your GCS service account JSON here...' class="input" style="font-family: monospace; font-size: var(--font-size-sm);"></textarea>
                    <small style="color: var(--gray-500);">Create a service account key in Google Cloud Console → IAM → Service Accounts</small>
                </div>
                <div style="display: flex; gap: var(--spacing-md); flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="doUploadBackup()" id="btn-upload">📤 Upload Backup</button>
                    <button class="btn btn-secondary" onclick="loadBackupList()" id="btn-list">📋 List Backups</button>
                </div>
            </div>
        </div>
    `;
    listEl.innerHTML = '';
}

function getBackupConfig() {
    const bucket = document.getElementById('backup-bucket')?.value?.trim();
    let creds = document.getElementById('backup-credentials')?.value?.trim();
    if (!bucket) {
        showNotification('Bucket name is required', 'error');
        return null;
    }
    if (!creds) {
        showNotification('Service account JSON is required', 'error');
        return null;
    }
    try {
        creds = JSON.parse(creds);
    } catch {
        showNotification('Invalid JSON in credentials field', 'error');
        return null;
    }
    return { bucket_name: bucket, credentials_json: creds };
}

async function doUploadBackup() {
    const config = getBackupConfig();
    if (!config) return;
    const btn = document.getElementById('btn-upload');
    btn.disabled = true;
    btn.textContent = 'Uploading...';
    try {
        await BackupAPI.upload(config);
        showNotification('Backup uploaded to Google Cloud successfully!', 'success');
        loadBackupList();
    } catch (e) {
        showNotification('Upload failed: ' + e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '📤 Upload Backup';
    }
}

async function loadBackupList() {
    const config = getBackupConfig();
    if (!config) return;
    const listEl = document.getElementById('backup-list');
    listEl.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    try {
        const res = await BackupAPI.list(config);
        const backups = res.backups || [];
        if (backups.length === 0) {
            listEl.innerHTML = '<div class="card"><p style="color: var(--gray-500);">No backups found in this bucket.</p></div>';
            return;
        }
        listEl.innerHTML = `
            <div class="card">
                <h3 style="margin-bottom: var(--spacing-md);">Available Backups</h3>
                <p style="color: var(--gray-600); margin-bottom: var(--spacing-md);">Select a backup to restore. This will replace your current database.</p>
                <div class="table-container">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Backup Name</th>
                                <th>Date</th>
                                <th>Size</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            ${backups.map(b => `
                                <tr>
                                    <td>${escapeHtml(b.name)}</td>
                                    <td>${b.updated ? new Date(b.updated).toLocaleString() : '-'}</td>
                                    <td>${formatBytes(b.size)}</td>
                                    <td>
                                        <button class="btn btn-sm btn-secondary" data-backup-path="${escapeHtml(b.full_path)}" onclick="doRestoreBackup(this.dataset.backupPath)">
                                            Restore
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } catch (e) {
        listEl.innerHTML = `<div class="alert alert-error">Failed to list backups: ${e.message}</div>`;
    }
}

async function doRestoreBackup(backupPath) {
    const config = getBackupConfig();
    if (!config) return;
    if (!confirm('This will replace your current database with the selected backup. Continue?')) return;
    const listEl = document.getElementById('backup-list');
    const prevHtml = listEl.innerHTML;
    listEl.innerHTML = '<div class="loading"><div class="spinner"></div><p>Restoring...</p></div>';
    try {
        await BackupAPI.restore({ ...config, backup_path: backupPath });
        showNotification('Database restored! Please refresh the page.', 'success');
        setTimeout(() => window.location.reload(), 1500);
    } catch (e) {
        listEl.innerHTML = prevHtml;
        showNotification('Restore failed: ' + e.message, 'error');
    }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatBytes(bytes) {
    if (!bytes) return '-';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
