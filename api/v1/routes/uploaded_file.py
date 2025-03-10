from typing import Annotated
from fastapi import APIRouter, Depends,  HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from api.v1.utils.get_db_session import get_db_session
from services.data_processing.helper.upload_file import process_small_file


router = APIRouter(tags=['File Upload'], prefix='/api/v1/file-upload')


@router.post('/', status_code=status.HTTP_200_OK)
async def upload_file(user_id: Annotated[str, Form()], session: AsyncSession = Depends(get_db_session), file: UploadFile = File(...)):
    """Upload a file"""
    try:
        response = await process_small_file(file, user_id, session)
        return {"data": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e