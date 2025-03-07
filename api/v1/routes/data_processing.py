from fastapi import APIRouter, Depends,  HTTPException, status, Form, UploadFile, File
from services.data_processing import regression, data_loader, spark_session
from typing import Annotated


router = APIRouter(tags=['Data Processing'], prefix='/api/v1/data-processing')


@router.post('/regression', status_code=status.HTTP_200_OK)
async def perform_regression(features_col: Annotated[str, Form()], label_col: Annotated[str, Form()], file: UploadFile = File(...), regression_type: Annotated[str, Form()] ="linear", spark_instance = Depends(spark_session.get_spark_session)):
    """Perform linear regression"""
    try:
        data  = data_loader.load_data(spark_instance, file.file, file.filename)
        features_col_list = features_col.split(',')
        response =  regression.perform_regression(regression_type, data,features_col_list, label_col)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e