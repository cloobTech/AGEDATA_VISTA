from fastapi import APIRouter, Depends,  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing import regression
from services.data_processing.helper import data_loader
from schemas.data_progressing import RegressionInput
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session


router = APIRouter(tags=['Data Processing'], prefix='/api/v1/data-processing')


@router.post('/regression', status_code=status.HTTP_200_OK)
async def perform_regression(inputs: RegressionInput, storage: AsyncSession = Depends(get_db_session)) -> DefaultResponse:
    """Perform linear regression"""
    try:
        data = await data_loader.load_data_with_pandas(inputs.file_id, storage)
        response = regression.perform_regression(
            inputs.regression_type, data, inputs.features_col, inputs.label_col)
        return DefaultResponse(status='success', message='Regression performed successfully', data=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
