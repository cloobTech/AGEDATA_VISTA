from fastapi import APIRouter, Depends,  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.analysis import select_analysis
from services.data_processing.helper import data_loader
from schemas.data_processing import AnalysisInput
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user
from errors.exceptions import EntityNotFoundError
from models.user import User

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
