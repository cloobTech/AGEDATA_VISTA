"""
GET  /api/v1/models/          — list saved models for the current user
POST /api/v1/models/{id}/predict — run prediction using a saved model
DELETE /api/v1/models/{id}    — delete a saved model record

Phase 7C.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user
from models.user import User
from services.ml.saved_model_crud import list_saved_models, get_saved_model, delete_saved_model
from errors.exceptions import EntityNotFoundError
from utils.audit_log import audit

router = APIRouter(tags=["Saved Models"], prefix="/api/v1/models")


class PredictRequest(BaseModel):
    """CSV-style rows to predict: list of dicts keyed by feature column name."""
    rows: list[dict[str, Any]]


@router.get("/", status_code=status.HTTP_200_OK)
async def list_models(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Return all saved model metadata for the authenticated user."""
    return await list_saved_models(str(current_user.id), session)


@router.post("/{model_id}/predict", status_code=status.HTTP_200_OK)
async def predict(
    model_id: str,
    body: PredictRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Run inference using a previously saved sklearn model.

    The caller must supply `rows` — a list of dicts where each key is one of
    the model's `feature_cols`.  Extra keys are silently ignored; missing keys
    raise a 422 error before inference starts.

    Returns:
        {"predictions": [...], "probabilities": [...] | null}
    """
    try:
        meta = await get_saved_model(model_id, session)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # IDOR guard
    if str(meta.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not body.rows:
        raise HTTPException(status_code=422, detail="'rows' must not be empty.")

    feature_cols = meta.feature_cols

    # Validate all required columns are present
    missing = [c for c in feature_cols if c not in body.rows[0]]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Input rows are missing required feature columns: {missing}",
        )

    import pandas as pd
    from services.data_processing.model_store.model_store import load_sklearn_model

    try:
        bundle = load_sklearn_model(meta.storage_path)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    model  = bundle["model"]
    scaler = bundle.get("scaler")

    df = pd.DataFrame(body.rows)[feature_cols]

    if scaler is not None:
        X = scaler.transform(df)
    else:
        X = df.values

    predictions = model.predict(X).tolist()

    probabilities = None
    if hasattr(model, "predict_proba"):
        try:
            probabilities = model.predict_proba(X).tolist()
        except Exception:
            pass

    return {
        "model_id":     model_id,
        "analysis_type": meta.analysis_type,
        "task_type":    meta.task_type,
        "feature_cols": feature_cols,
        "predictions":  predictions,
        "probabilities": probabilities,
        "n_rows":       len(predictions),
    }


@router.delete("/{model_id}", status_code=status.HTTP_200_OK)
async def delete_model(
    model_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a saved model record (does NOT remove the Supabase storage file)."""
    try:
        result = await delete_saved_model(model_id, str(current_user.id), session)
        audit("DELETE_SAVED_MODEL", user_id=str(current_user.id), resource_id=model_id,
              resource_type="saved_model")
        return result
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
