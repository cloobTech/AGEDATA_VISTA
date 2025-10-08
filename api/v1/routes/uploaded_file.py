from typing import  Optional, Dict, Any
from fastapi import APIRouter, Depends,  HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from api.v1.utils.get_db_session import get_db_session
from services.file_upload.upload_file_class import file_upload_service
from services.file_upload.upload_progress import task_progress_service
from services.sse.server_sent_events import sse_service
# from services.data_processing.helper.select_uploader_type import select_upload_processor
from services.data_processing.user_files.crud import update_user_file, delete_user_file, get_user_file_by_id
from storage.redis_client import get_task_progress, get_temp_data
from schemas.default_response import DefaultResponse
from schemas.upload_dataset import UploadForm
from api.v1.utils.current_user import get_current_user
from models.user import User


router = APIRouter(tags=['File Upload'], prefix='/api/v1/file-upload')


def get_upload_form(
    user_id: str = Form(...),
    file_type: str = Form("tabular"),
    clean_file: bool = Form(False),
    source_type: str = Form('upload'),
    file_url: str | None = Form(None),
) -> UploadForm:
    return UploadForm(
        user_id=user_id, 
        file_type=file_type, 
        clean_file=clean_file, 
        source_type=source_type, 
        file_url=file_url
    )


@router.post("/", status_code=status.HTTP_200_OK)
async def upload_file(
    form: UploadForm = Depends(get_upload_form),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
) -> DefaultResponse:
    """
    Upload file for processing
    """
    try:
        # Convert Pydantic model to dict for service
        form_dict = {
            "user_id": form.user_id,
            "file_type": form.file_type,
            "clean_file": form.clean_file,
            "source_type": form.source_type,
            "file_url": form.file_url
        }
        
        form_data, file_content = await file_upload_service.prepare_upload_data(
            file, form_dict
        )

        result = await file_upload_service.start_file_processing(form_data, file_content)
        
        return DefaultResponse(
            status="success",
            message="File submitted for processing",
            data=result,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        ) from e


@router.get("/upload-progress/{task_id}")
async def stream_task_progress(task_id: str, request: Request):
    """
    Stream task progress via Server-Sent Events
    """
    return await sse_service.stream_task_progress(task_id, request)


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get current task status (one-time check)
    """
    status_data = await task_progress_service.get_task_status(task_id)
    return DefaultResponse(
        status="success",
        message="Task status retrieved",
        data=status_data
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return DefaultResponse(
        status="success",
        message="File upload service is healthy",
        data={"service": "file-upload"}
    )


@router.get('/{file_id}/status', status_code=status.HTTP_200_OK)
async def get_file_upload_status(file_id: str,  current_user: User = Depends(get_current_user)) -> Optional[Dict[str, Any]]:
    """Get file upload status by id"""
    try:
        # response = await get_temp_data(file_id)  # Fetch temporary data instead
        # Fetch temporary data instead
        response = await get_task_progress(file_id)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{file_id}', status_code=status.HTTP_200_OK)
async def get_file_by_id(file_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DefaultResponse:
    """Get file by id"""
    try:
        response = await get_user_file_by_id(file_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/{file_id}', status_code=status.HTTP_200_OK)
async def update_file(file_id: str, data: dict,  session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DefaultResponse:
    """Update file by id"""
    try:
        response = await update_user_file(file_id, data, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DataRequiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.delete('/{file_id}', status_code=status.HTTP_200_OK)
async def delete_file(file_id: str, session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)) -> DefaultResponse:
    """Delete file by id"""
    try:
        response = await delete_user_file(file_id, session)
        return response
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
