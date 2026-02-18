"""
X-ray report file storage helper.
Copies files into app data directory and removes them on delete.
"""
import os
import re
import shutil
from typing import Optional, Tuple

# Use same app data dir as database; avoid circular import by importing the function only when needed
def _get_app_data_dir() -> str:
    from backend.database import get_app_data_dir
    return get_app_data_dir()


def _sanitize_basename(name: str) -> str:
    """Sanitize filename for safe storage (alphanumeric, dash, underscore, dot)."""
    base, ext = os.path.splitext(name)
    safe_base = re.sub(r"[^\w\-]", "_", base or "file")[:80]
    safe_ext = re.sub(r"[^\w.]", "", ext)[:20]
    return (safe_base + safe_ext) if safe_ext else safe_base


def save_xray_file(
    patient_id: str,
    report_id: str,
    source_path: str,
) -> Tuple[bool, Optional[str]]:
    """
    Copy the file at source_path into app data dir under xray_reports/{patient_id}/.
    Returns (success, dest_path). dest_path is the full path to store in DB; None on failure.
    """
    if not source_path or not os.path.isfile(source_path):
        return False, None
    try:
        app_dir = _get_app_data_dir()
        base_dir = os.path.join(app_dir, "xray_reports", patient_id)
        os.makedirs(base_dir, exist_ok=True)
        original_name = os.path.basename(source_path)
        safe_name = _sanitize_basename(original_name)
        dest_name = f"{report_id}_{safe_name}"
        dest_path = os.path.join(base_dir, dest_name)
        shutil.copy2(source_path, dest_path)
        return True, dest_path
    except OSError:
        return False, None
    except Exception:
        return False, None


def delete_xray_file(file_path: str) -> bool:
    """
    Remove the file at file_path if it exists. Optionally remove parent dir if empty.
    Returns True if file was removed or did not exist, False on error.
    """
    if not file_path:
        return True
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
        parent = os.path.dirname(file_path)
        if os.path.isdir(parent) and not os.listdir(parent):
            try:
                os.rmdir(parent)
            except OSError:
                pass
        return True
    except OSError:
        return False
    except Exception:
        return False
