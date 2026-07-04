"""
Cloud storage layer for Jetski SmartHire.

Uses Google Cloud Storage to persist uploaded resume files.
Falls back to local disk (./local_storage) when GCS isn't configured,
so the app still runs fine for local development without GCP credentials.
"""
import os
import uuid
from pathlib import Path
from typing import Optional

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
USE_CLOUD_STORAGE = bool(GCS_BUCKET_NAME)

LOCAL_STORAGE_DIR = Path("./local_storage/resumes")
LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

_bucket = None
if USE_CLOUD_STORAGE:
    try:
        from google.cloud import storage as gcs

        _client = gcs.Client()
        _bucket = _client.bucket(GCS_BUCKET_NAME)
    except Exception as e:  # pragma: no cover - defensive fallback
        print(f"[storage] Could not initialize GCS client, falling back to local disk: {e}")
        USE_CLOUD_STORAGE = False


def save_resume_file(file_content: bytes, filename: str) -> str:
    """
    Persist an uploaded resume file.
    Returns a storage reference (gs:// URI or local path) that can be
    used later to retrieve the file.
    """
    safe_name = f"{uuid.uuid4()}_{filename}"

    if USE_CLOUD_STORAGE and _bucket is not None:
        blob = _bucket.blob(f"resumes/{safe_name}")
        blob.upload_from_string(file_content)
        return f"gs://{GCS_BUCKET_NAME}/resumes/{safe_name}"

    local_path = LOCAL_STORAGE_DIR / safe_name
    local_path.write_bytes(file_content)
    return str(local_path)


def get_resume_file(storage_ref: str) -> Optional[bytes]:
    """Retrieve a previously stored resume file's raw bytes."""
    if storage_ref.startswith("gs://") and USE_CLOUD_STORAGE and _bucket is not None:
        blob_path = storage_ref.replace(f"gs://{GCS_BUCKET_NAME}/", "")
        blob = _bucket.blob(blob_path)
        if not blob.exists():
            return None
        return blob.download_as_bytes()

    path = Path(storage_ref)
    if path.exists():
        return path.read_bytes()
    return None


def storage_backend_name() -> str:
    return "Google Cloud Storage" if USE_CLOUD_STORAGE else "local disk (dev fallback)"
