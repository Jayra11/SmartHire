"""
Persistence layer for Jetski SmartHire.

Uses Google Cloud Firestore to persist screening results (and their
resume text + embeddings, which power the RAG features) so data
survives restarts and can be queried across instances.

Falls back to an in-memory dict when GOOGLE_CLOUD_PROJECT / Firestore
isn't configured, so local development still works without GCP credentials.
"""
import os
from typing import Optional

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
USE_FIRESTORE = bool(GOOGLE_CLOUD_PROJECT)

COLLECTION = "screening_results"

_db = None
_memory_store: dict = {}

if USE_FIRESTORE:
    try:
        from google.cloud import firestore

        _db = firestore.Client(project=GOOGLE_CLOUD_PROJECT)
    except Exception as e:  # pragma: no cover - defensive fallback
        print(f"[database] Could not initialize Firestore, falling back to in-memory store: {e}")
        USE_FIRESTORE = False


def save_result(result_id: str, data: dict) -> None:
    if USE_FIRESTORE and _db is not None:
        _db.collection(COLLECTION).document(result_id).set(data)
    else:
        _memory_store[result_id] = data


def get_result(result_id: str) -> Optional[dict]:
    if USE_FIRESTORE and _db is not None:
        doc = _db.collection(COLLECTION).document(result_id).get()
        return doc.to_dict() if doc.exists else None
    return _memory_store.get(result_id)


def list_results() -> list:
    if USE_FIRESTORE and _db is not None:
        docs = _db.collection(COLLECTION).stream()
        return [d.to_dict() for d in docs]
    return list(_memory_store.values())


def delete_result(result_id: str) -> bool:
    if USE_FIRESTORE and _db is not None:
        ref = _db.collection(COLLECTION).document(result_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True
    if result_id in _memory_store:
        del _memory_store[result_id]
        return True
    return False


def database_backend_name() -> str:
    return "Google Cloud Firestore" if USE_FIRESTORE else "in-memory (dev fallback)"
