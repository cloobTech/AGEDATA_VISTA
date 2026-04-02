"""CRUD operations for the saved_models table — Phase 7B."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.saved_model import SavedModel
from errors.exceptions import EntityNotFoundError


async def create_saved_model(
    user_id: str,
    project_id: str,
    storage_path: str,
    analysis_type: str,
    task_type: str,
    feature_cols: list,
    label: Optional[str] = None,
    session: AsyncSession = None,
) -> dict:
    """Persist a saved-model metadata record and return its dict."""
    obj = SavedModel(
        user_id=user_id,
        project_id=project_id,
        storage_path=storage_path,
        analysis_type=analysis_type,
        task_type=task_type,
        feature_cols=feature_cols,
        label=label,
    )
    await obj.save(session)
    return obj.to_dict()


async def list_saved_models(user_id: str, session: AsyncSession) -> list[dict]:
    """Return all saved models owned by user_id, most-recent first."""
    result = await session.execute(
        select(SavedModel)
        .where(SavedModel.user_id == user_id)
        .order_by(SavedModel.created_at.desc())
    )
    return [row.to_dict() for row in result.scalars().all()]


async def get_saved_model(model_id: str, session: AsyncSession) -> SavedModel:
    """Return a SavedModel by primary key or raise EntityNotFoundError."""
    result = await session.execute(
        select(SavedModel).where(SavedModel.id == model_id)
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise EntityNotFoundError(f"Saved model '{model_id}' not found.")
    return obj


async def delete_saved_model(
    model_id: str, caller_id: str, session: AsyncSession
) -> dict:
    """Delete a saved model record. Raises 403 if caller is not the owner."""
    obj = await get_saved_model(model_id, session)
    if str(obj.user_id) != str(caller_id):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to delete this model.",
        )
    result = obj.to_dict()
    await obj.delete(session)
    return result
