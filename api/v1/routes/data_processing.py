from fastapi import APIRouter, Depends, HTTPException, status, Request
from celery.result import AsyncResult
from pydantic import BaseModel
from typing import List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.analysis import select_analysis
from services.data_processing.large_data.big_data_task import perform_big_data_analysis_task
from services.data_processing.report.large_data_report import get_large_data_report_by_id, list_large_data_reports, delete_large_data_report, update_large_data_report
from services.data_processing.helper import data_loader
from services.data_processing.helper.url_loader import load_dataframe_from_url, get_url_preview
from schemas.data_processing import AnalysisInput, BigDataAnalysisInput
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user
from errors.exceptions import EntityNotFoundError
from storage.redis_sync_client import get_task_progress_sync
from storage import db
from models.uploaded_file import UploadedFile
from models.user import User
import uuid
import os
from services.sse.server_sent_events import sse_service

_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_UPLOADS_DATASETS_DIR = os.path.join(_BACKEND_ROOT, "uploads", "datasets")


class PredictRequest(BaseModel):
    data: List[Any]  # list of dicts, one per row


class URLDatasetRequest(BaseModel):
    url: str
    project_id: Optional[str] = None


class URLPreviewRequest(BaseModel):
    url: str

router = APIRouter(tags=['Data Processing'], prefix='/api/v1/analysis')


@router.post('/', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
@router.post('', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def perform_test(inputs: AnalysisInput, storage: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    """Perform test analysis"""

    try:
        # IDOR guard: verify the requesting user owns the file
        if inputs.file_id:
            _file = await db.get(storage, UploadedFile, inputs.file_id)
            if not _file:
                raise HTTPException(status_code=404, detail="File not found")
            if str(_file.user_id) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Forbidden")

        data = await data_loader.load_data_with_pandas(inputs.file_id, storage, inputs.columns)
        response = await select_analysis.perform_analysis(data, inputs, storage)
        return DefaultResponse(status='success', message='analysis performed successfully', data=response)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/models/{report_id}/predict', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def predict_with_saved_model(
    report_id: str,
    body: PredictRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Run predictions on new data using a previously saved sklearn model."""
    try:
        from storage import db
        from models.report import Report
        from services.data_processing.model_store.model_store import load_sklearn_model
        import pandas as pd

        report = await db.find_by(session, Report, id=report_id)
        if not report:
            raise EntityNotFoundError("Report not found")

        # IDOR guard: verify the caller is the project owner or a member
        from models.project import Project
        from models.project_member import ProjectMember
        from sqlalchemy import select as _sa_select
        _project = await db.get(session, Project, report.project_id)
        if _project:
            _is_owner = str(_project.owner_id) == str(current_user.id)
            if not _is_owner:
                _mem_result = await session.execute(
                    _sa_select(ProjectMember).where(
                        ProjectMember.project_id == _project.id,
                        ProjectMember.user_id == current_user.id,
                    )
                )
                if not _mem_result.scalar_one_or_none():
                    raise HTTPException(status_code=403, detail="Forbidden")

        model_path = (report.summary or {}).get("model_storage_path")
        if not model_path:
            raise ValueError(
                "No saved model found for this report. "
                "Only SVM and Gradient Boosting models support prediction reuse."
            )

        bundle = load_sklearn_model(model_path)
        model = bundle["model"]
        scaler = bundle.get("scaler")
        feature_cols = bundle.get("feature_cols")

        # Build DataFrame from request data
        df = pd.DataFrame(body.data)

        # Reorder / select feature columns if available
        if feature_cols:
            missing = [c for c in feature_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Input data is missing required columns: {missing}. "
                    f"Expected columns: {feature_cols}"
                )
            df = df[feature_cols]

        X = df.values.astype(float)

        # Apply scaler if it was used during training
        if scaler is not None:
            X = scaler.transform(X)

        predictions = model.predict(X).tolist()
        probabilities = None
        if hasattr(model, "predict_proba"):
            try:
                probabilities = model.predict_proba(X).tolist()
            except Exception:
                pass

        return DefaultResponse(
            status="success",
            message="Predictions completed",
            data={
                "predictions": predictions,
                "probabilities": probabilities,
                "n_samples": len(predictions),
                "feature_cols_used": feature_cols,
            }
        )

    except EntityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post('/big-data', status_code=status.HTTP_202_ACCEPTED, response_model=DefaultResponse)
async def perform_big_data_analysis(
    inputs: BigDataAnalysisInput,
    current_user: User = Depends(get_current_user),
):
    """Start big data analysis using PySpark and Celery"""

    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Start Celery task
        task = perform_big_data_analysis_task.apply_async(
            args=[inputs.model_dump(), current_user.id],
            task_id=task_id
        )

        return DefaultResponse(
            status='success',
            message='Big data analysis started successfully',
            data={'task_id': task.id}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start analysis: {str(e)}"
        )


# NOTE: Static routes (/big-data/reports, /big-data/status, /stream-progress)
# MUST be declared BEFORE parameterized routes (/big-data/{task_id}/...) to avoid shadowing.

@router.get('/big-data/reports', response_model=DefaultResponse)
async def list_big_data_reports_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """List all big data reports for the current user"""

    try:
        reports_response = await list_large_data_reports(current_user.id, session)
        return reports_response

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list big data reports: {str(e)}"
        ) from e


@router.get('/stream-progress/{task_id}')
async def stream_data_processing_progress_endpoint(task_id: str, request: Request):
    """
    Stream data processing progress via Server-Sent Events
    """
    return await sse_service.stream_task_progress(task_id, request)


@router.get('/big-data/{task_id}/status', response_model=DefaultResponse)
async def get_analysis_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a big data analysis task"""

    try:
        # Try to get progress from Redis first
        progress_data: dict = get_task_progress_sync(task_id) or {}

        if not progress_data:
            # Fallback to Celery's result
            task_result = AsyncResult(task_id)
            status = task_result.status
            message = (
                "Task completed successfully." if task_result.successful()
                else f"Task failed: {task_result.result}" if task_result.failed()
                else "Task is pending or running."
            )

            return DefaultResponse(
                status=status,
                message=message,
                data={
                    "progress": 100 if task_result.successful() else 0
                }
            )

        # Redis data available
        return DefaultResponse(
            status=progress_data.get("status", "PROGRESS"),
            message=f"Task is {progress_data.get('progress', 0)}% complete.",
            data=progress_data
        )

    except Exception as e:
        return DefaultResponse(
            status="FAILURE",
            message=f"Error retrieving task status: {str(e)}",
            data={}
        )


@router.get('/big-data/{task_id}/result', response_model=DefaultResponse)
async def get_big_data_analysis_result(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get the result of a big data analysis task"""

    try:
        result_response = await get_large_data_report_by_id(task_id, session)
        return result_response

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analysis result: {str(e)}"
        ) from e


@router.get('/big-data/{project_id}/report', response_model=DefaultResponse)
async def get_big_data_project_report(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get big data report by project ID — alias for result endpoint used by BigData.jsx"""

    try:
        result_response = await get_large_data_report_by_id(project_id, session)
        return result_response

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve project report: {str(e)}"
        ) from e


@router.delete('/big-data/{report_id}', response_model=DefaultResponse)
async def delete_big_data_report_endpoint(
    report_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a big data report by its ID"""

    try:
        delete_response = await delete_large_data_report(report_id, session)
        return delete_response

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete big data report: {str(e)}"
        ) from e


@router.put('/big-data/{report_id}', response_model=DefaultResponse)
async def update_big_data_report_endpoint(
    report_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Update a big data report by its ID"""

    try:
        update_response = await update_large_data_report(report_id, update_data, session)
        return update_response

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update big data report: {str(e)}"
        ) from e


@router.post('/dataset-from-url/', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
@router.post('/dataset-from-url', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def load_dataset_from_url(
    body: URLDatasetRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Download a dataset from a URL, save it locally, and create an UploadedFile record."""
    try:
        df, filename = await load_dataframe_from_url(body.url)

        # Ensure uploads/datasets directory exists
        os.makedirs(_UPLOADS_DATASETS_DIR, exist_ok=True)

        # Derive extension from filename, default to csv
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'csv'
        if ext not in ('csv', 'tsv', 'xlsx', 'xls', 'json', 'parquet'):
            ext = 'csv'

        # Save as CSV for consistent downstream loading
        file_id = str(uuid.uuid4())
        save_name = f"{file_id}_{filename}"
        if not save_name.endswith(('.csv', '.tsv', '.xlsx', '.xls', '.json', '.parquet')):
            save_name = f"{file_id}_{filename}.csv"
            ext = 'csv'

        save_path = os.path.join(_UPLOADS_DATASETS_DIR, save_name)
        df.to_csv(save_path, index=False)
        file_size = os.path.getsize(save_path)
        local_url = f"/uploads/datasets/{save_name}"

        uploaded_file = UploadedFile(
            id=file_id,
            user_id=current_user.id,
            project_id=body.project_id,
            name=filename,
            size=str(file_size),
            url=local_url,
            extension='csv',
            status='SUCCESS',
            public_id=None,
        )
        db.new(session, uploaded_file)
        await db.save(session)

        return DefaultResponse(
            status='success',
            message=f'Dataset loaded from URL: {filename}',
            data={
                'id': file_id,
                'name': filename,
                'url': local_url,
                'extension': 'csv',
                'size': str(file_size),
                'rows': len(df),
                'columns': list(df.columns),
                'project_id': body.project_id,
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/dataset-from-url/preview/', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
@router.post('/dataset-from-url/preview', status_code=status.HTTP_200_OK, response_model=DefaultResponse)
async def preview_dataset_from_url(
    body: URLPreviewRequest,
    current_user: User = Depends(get_current_user),
):
    """Fetch a dataset from a URL and return a column preview without saving."""
    try:
        df, filename = await load_dataframe_from_url(body.url)

        preview_rows = df.head(5).fillna('').to_dict(orient='records')
        column_info = [
            {'name': col, 'dtype': str(df[col].dtype), 'sample': str(df[col].iloc[0]) if len(df) > 0 else ''}
            for col in df.columns
        ]

        return DefaultResponse(
            status='success',
            message=f'Preview loaded for: {filename}',
            data={
                'filename': filename,
                'rows': len(df),
                'columns': list(df.columns),
                'column_info': column_info,
                'preview': preview_rows,
                'shape': list(df.shape),
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/precondition-tests/')
@router.post('/precondition-tests')
async def run_precondition_tests_endpoint(
    payload: dict,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    import traceback
    import logging as _logging
    _log = _logging.getLogger(__name__)

    file_id  = payload.get('file_id')
    columns  = payload.get('columns') or None
    run_ts   = bool(payload.get('run_time_series', True))
    run_norm = bool(payload.get('run_normality', True))
    max_cols = min(int(payload.get('max_columns', 10)), 15)

    if not file_id:
        raise HTTPException(status_code=422, detail='file_id is required')

    # IDOR guard: verify the requesting user owns the file
    _pct_file = await db.get(session, UploadedFile, file_id)
    if not _pct_file:
        raise HTTPException(status_code=404, detail='File not found')
    if str(_pct_file.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail='Forbidden')

    try:
        df = await data_loader.load_data_with_pandas(file_id, session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Could not load file: {type(e).__name__}: {str(e)}'
        )

    try:
        from services.data_processing.analysis.precondition_tests import run_precondition_tests
        result = run_precondition_tests(
            df,
            columns=columns,
            run_time_series=run_ts,
            run_normality=run_norm,
            max_columns=max_cols,
        )
        return result
    except Exception as e:
        _log.error('Precondition tests error: %s', traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f'Precondition tests failed: {type(e).__name__}: {str(e)}'
        )
