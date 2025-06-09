import tempfile
import os
import warnings
from typing import Dict, Any
from supabase import create_client
from keras.models import load_model
from settings.pydantic_config import settings
import tensorflow as tf

def load_model_from_supabase(
    model_name: str,
    bucket_name: str = "age-vista-data",
    supabase_url: str = settings.SUPABASE_URL,
    supabase_key: str = settings.SUPABASE_KEY
) -> Any:
    """
    Load a trained Keras model from Supabase storage bucket with GPU warning suppression.
    
    Args:
        model_name: Name of the model file (without extension)
        bucket_name: Supabase storage bucket name
        supabase_url: Supabase project URL
        supabase_key: Supabase project key
        
    Returns:
        Loaded Keras model
        
    Raises:
        ValueError: If loading fails
    """
    try:
        # Suppress GPU-related warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        tf.get_logger().setLevel('ERROR')
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and Key must be provided.")

        supabase = create_client(supabase_url, supabase_key)
        
        # Define the storage path
        storage_path = f"neural_networks/{model_name}.keras"
        
        # Download and load with context manager
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Suppress warnings during download and loading
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Download the model
                file_data = supabase.storage.from_(bucket_name).download(storage_path)
                
                # Save to temporary file
                temp_model_path = os.path.join(tmp_dir, f"{model_name}.keras")
                with open(temp_model_path, 'wb') as f:
                    f.write(file_data)
                
                # Load the model with custom objects if needed
                model = load_model(temp_model_path)
                
                # Handle the metrics warning
                if hasattr(model, 'compile_metrics'):
                    try:
                        model.compile_metrics = []
                    except:
                        pass
            
        return model

    except Exception as e:
        raise ValueError(f"Failed to load model from Supabase: {str(e)}")