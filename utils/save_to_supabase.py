import tempfile
import os
from typing import Dict, Any
from supabase import create_client
from keras.models import save_model
from settings.pydantic_config import settings


async def save_model_to_supabase(
    model: Any,
    model_name: str,
    bucket_name: str = "age-vista-data",
    supabase_url: str = settings.SUPABASE_URL,
    supabase_key: str = settings.SUPABASE_KEY
) -> Dict[str, Any]:
    """
    Save a trained Keras model to a Supabase storage bucket.
    """
    try:

        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and Key must be provided.")

        supabase = create_client(supabase_url, supabase_key)

        # Save model to temp file
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_path = os.path.join(tmp_dir, f"{model_name}.keras")
            save_model(model, model_path)

            # Upload to Supabase
            storage_path = f"neural_networks/{model_name}.keras"
            with open(model_path, 'rb') as f:
                res = supabase.storage.from_(bucket_name).upload(
                    storage_path,
                    f,  # file-like object
                    {"content-type": "application/octet-stream"}
                )

        return {
            "storage_path": storage_path,
            "bucket": bucket_name,
            "model_name": model_name,
        }

    except Exception as e:
        raise ValueError(f"Failed to upload to supabase storage: {e}")
