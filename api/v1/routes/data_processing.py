from fastapi import APIRouter, Depends,  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.analysis import regression, descriptive, test
from services.data_processing.helper import data_loader
from schemas.data_progressing import RegressionInput, DescriptiveAnalysisInput
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session
from errors.exceptions import EntityNotFoundError


router = APIRouter(tags=['Data Processing'], prefix='/api/v1/data-processing')


@router.post('/regression', status_code=status.HTTP_200_OK)
async def perform_regression(inputs: RegressionInput, storage: AsyncSession = Depends(get_db_session)) -> DefaultResponse:
    """Perform linear regression"""
    try:
        data = await data_loader.load_data_with_pandas(inputs.file_id,  storage, inputs.columns)
        response = await regression.perform_regression(
            inputs, data, session=storage)
        return DefaultResponse(status='success', message='Regression performed successfully', data=response)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/descriptive-analysis', status_code=status.HTTP_200_OK)
async def perform_descriptive_analysis(inputs: DescriptiveAnalysisInput, storage: AsyncSession = Depends(get_db_session)) -> DefaultResponse:
    """Perform descriptive analysis"""
    try:
        data = await data_loader.load_data_with_pandas(inputs.file_id, storage, inputs.columns)
        response = await descriptive.perform_descriptive_analysis(
            data, inputs, storage)
        return DefaultResponse(status='success', message='Descriptive analysis performed successfully', data=response)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/test', status_code=status.HTTP_200_OK)
async def perform_descriptive_analysis(inputs: DescriptiveAnalysisInput) -> DefaultResponse:
    """Perform descriptive analysis"""
    try:
        response = await descriptive.perform_descriptive_analysis(inputs)
        return DefaultResponse(status='success', message='Descriptive analysis performed successfully', data=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
