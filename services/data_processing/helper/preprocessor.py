"""
preprocessor.py
Shared preprocessing utilities for ML analysis functions.
Handles categorical encoding, missing values, and type validation.
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Any

log = logging.getLogger(__name__)


def encode_features(X: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, dict]]:
    """
    Label-encode every non-numeric column in X in-place.
    Returns (encoded_X, encoding_map) where encoding_map[col] = {'type': 'label', 'mapping': {...}}.

    Low-cardinality strings (≤ 50 unique values) are label-encoded.
    High-cardinality strings (> 50) are dropped and logged.
    """
    X = X.copy()
    encoding_map: Dict[str, dict] = {}
    cols_to_drop = []

    for col in X.columns:
        if X[col].dtype == object or str(X[col].dtype) in ('string', 'category'):
            unique_vals = X[col].dropna().unique()
            if len(unique_vals) > 50:
                log.warning(
                    "Column '%s' has %d unique values — too many to encode for ML. "
                    "Dropping it from features.",
                    col, len(unique_vals),
                )
                cols_to_drop.append(col)
                continue

            # Fill NaN before encoding
            X[col] = X[col].fillna('__missing__')
            all_vals = sorted(X[col].unique(), key=str)
            mapping = {v: i for i, v in enumerate(all_vals)}
            X[col] = X[col].map(mapping).astype(int)
            encoding_map[col] = {'type': 'label', 'mapping': mapping}
            log.info("Label-encoded '%s' (%d categories).", col, len(mapping))

    if cols_to_drop:
        X = X.drop(columns=cols_to_drop)

    return X, encoding_map


def fill_missing(X: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values:
    - Numeric columns  → median
    - Object/category  → 'Unknown'
    """
    X = X.copy()
    for col in X.columns:
        if X[col].isnull().any():
            if X[col].dtype == object or str(X[col].dtype) in ('string', 'category'):
                X[col] = X[col].fillna('Unknown')
            else:
                X[col] = X[col].fillna(X[col].median())
    return X


def prepare_X(X: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, dict]]:
    """
    Full feature preprocessing pipeline:
    1. Fill missing values
    2. Label-encode categorical columns
    Returns (clean_X, encoding_map).
    """
    X = fill_missing(X)
    X, enc_map = encode_features(X)
    if X.empty or X.shape[1] == 0:
        raise ValueError(
            "No valid numeric feature columns remain after preprocessing. "
            "Please select numeric columns for this analysis."
        )
    return X, enc_map


def sanitise_result(obj: Any) -> Any:
    """
    Recursively convert numpy types → Python native types for JSON serialization.
    Replaces NaN and Inf with None.
    """
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: sanitise_result(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [sanitise_result(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        v = float(obj)
        return None if (v != v or v == float('inf') or v == float('-inf')) else v
    if isinstance(obj, np.ndarray):
        return sanitise_result(obj.tolist())
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, float):
        return None if (obj != obj or obj == float('inf') or obj == float('-inf')) else obj
    return obj
