"""
ML Model persistence for sklearn models using joblib + Supabase Storage.

save_sklearn_model()  — serialise model bundle → Supabase (non-blocking, returns None on failure)
load_sklearn_model()  — deserialise model bundle ← Supabase (raises ValueError on failure)

A "model bundle" is a dict: {"model": <sklearn model>, "scaler": <scaler|None>,
                              "feature_cols": list, "task_type": str}
"""
import io
import os
import logging
import tempfile
from typing import Any, Optional

log = logging.getLogger(__name__)

SUPABASE_BUCKET = "age-vista-data"
MODEL_PREFIX = "sklearn_models"


def _supabase_client():
    """Return a Supabase client or None if credentials are missing."""
    try:
        from supabase import create_client
        from settings.pydantic_config import settings
        url = getattr(settings, "SUPABASE_URL", None)
        key = getattr(settings, "SUPABASE_KEY", None)
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception as exc:
        log.warning("Cannot create Supabase client: %s", exc)
        return None


def save_sklearn_model(bundle: dict, storage_id: str) -> Optional[str]:
    """
    Serialise a model bundle with joblib and upload to Supabase Storage.

    Returns the storage path on success, None on any failure (never raises).
    The caller should log / ignore the None — model saving is non-blocking.
    """
    try:
        import joblib
    except ImportError:
        log.warning("joblib not installed — sklearn model not saved")
        return None

    client = _supabase_client()
    if not client:
        log.debug("Supabase not configured — sklearn model not saved")
        return None

    try:
        buf = io.BytesIO()
        joblib.dump(bundle, buf)
        buf.seek(0)
        model_bytes = buf.read()

        storage_path = f"{MODEL_PREFIX}/{storage_id}.joblib"
        client.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=model_bytes,
            file_options={"content-type": "application/octet-stream"},
        )

        log.info("sklearn model saved to Supabase: %s", storage_path)
        return storage_path

    except Exception as exc:
        log.warning("Failed to save sklearn model to Supabase: %s", exc)
        return None


def load_sklearn_model(storage_path: str) -> dict:
    """
    Download and deserialise a model bundle from Supabase Storage.

    Returns the bundle dict: {"model": ..., "scaler": ..., "feature_cols": ..., "task_type": ...}
    Raises ValueError on any failure.
    """
    try:
        import joblib
    except ImportError:
        raise ValueError("joblib not installed — cannot load sklearn model")

    client = _supabase_client()
    if not client:
        raise ValueError("Supabase not configured — cannot load model")

    try:
        file_data = client.storage.from_(SUPABASE_BUCKET).download(storage_path)
    except Exception as exc:
        raise ValueError(f"Failed to download model from Supabase: {exc}")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tmp:
            tmp.write(file_data)
            tmp_path = tmp.name
        bundle = joblib.load(tmp_path)
    except Exception as exc:
        raise ValueError(f"Failed to deserialise model: {exc}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return bundle
