from typing import Annotated
from fastapi import APIRouter, Depends,  HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from api.v1.utils.get_db_session import get_db_session
from services.data_processing.helper.select_uploader_type import select_upload_processor
from services.data_processing.user_files.crud import update_user_file, delete_user_file, get_user_file_by_id
from schemas.default_response import DefaultResponse


router = APIRouter(tags=['File Upload'], prefix='/api/v1/file-upload')


@router.post('/', status_code=status.HTTP_200_OK)
async def upload_file(user_id: Annotated[str, Form()], file_type: Annotated[str, Form()] = "tabular", session: AsyncSession = Depends(get_db_session), file: UploadFile = File(...)) -> DefaultResponse:
    """Upload a file"""
    try:
        response = await select_upload_processor(file, user_id, session, file_type=file_type)
        return DefaultResponse(
            status="success", message="File uploaded successfully", data=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get('/{file_id}', status_code=status.HTTP_200_OK)
async def get_file_by_id(file_id: str, session: AsyncSession = Depends(get_db_session)) -> DefaultResponse:
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
async def update_file(file_id: str, data: dict,  session: AsyncSession = Depends(get_db_session)) -> DefaultResponse:
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
async def delete_file(file_id: str, session: AsyncSession = Depends(get_db_session)) -> DefaultResponse:
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
