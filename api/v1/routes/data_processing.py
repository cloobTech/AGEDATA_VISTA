from fastapi import APIRouter, Depends, HTTPException, status, Request
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.analysis import select_analysis
from services.data_processing.large_data.big_data_task import perform_big_data_analysis_task
from services.data_processing.helper import data_loader
from schemas.data_processing import AnalysisInput, BigDataAnalysisInput
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user
from errors.exceptions import EntityNotFoundError
from storage.redis_sync_client import get_task_progress_sync
from models.user import User
import uuid
from services.sse.server_sent_events import sse_service

router = APIRouter(tags=['Data Processing'], prefix='/api/v1/analysis')


@router.post('/', status_code=status.HTTP_200_OK,   response_model=DefaultResponse)
async def perform_test(inputs: AnalysisInput, storage: AsyncSession = Depends(get_db_session),  current_user: User = Depends(get_current_user)):
    """Perform test analysis"""

    try:
        data = await data_loader.load_data_with_pandas(inputs.file_id, storage, inputs.columns)
        response = await select_analysis.perform_analysis(data, inputs, storage)
        # response = await select_analysis.perform_analysis("https://res.cloudinary.com/ddheqirld/image/upload/v1749218367/user_images/w89hhh7kt01mynpf0xa9.png", inputs, storage)
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
            args=[inputs.model_dump()],
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
            progress_data = {
                'status': task_result.status,
                'progress': 100 if task_result.successful() else 0,
                'message': str(task_result.result) if task_result.failed() else ""
            }

        return DefaultResponse(
            status='success',
            message='Analysis status retrieved successfully',
            data=progress_data
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.get('/stream-progress/{task_id}')
async def stream_data_processing_progress_endpoint(task_id: str, request: Request):
    """
    Stream data processing progress via Server-Sent Events
    """
    return await sse_service.stream_task_progress(task_id, request)
