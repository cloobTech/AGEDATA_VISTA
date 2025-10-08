from fastapi import APIRouter, Depends,  HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.utils.get_db_session import get_db_session
from services.data_processing.report.crud import get_user_reports, get_report_by_id, delete_report
from errors.exceptions import EntityNotFoundError
from schemas.default_response import DefaultResponse
from api.v1.utils.current_user import get_current_user
from models.user import User


router = APIRouter(tags=['Analysis Reports'], prefix='/api/v1/reports')


@router.get('/', status_code=status.HTTP_200_OK)
async def fetch_user_reports(
    user_id: str,
    analysis_group: str | None = None,  # Add query parameter
    session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)
) -> DefaultResponse:
    """Get all reports for a user, optionally filtered by analysis_group"""
    try:
        reports = await get_user_reports(user_id, analysis_group, session)
        return reports

    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get('/{report_id}', status_code=status.HTTP_200_OK)
async def fetch_report_by_id(
    report_id: str,
    session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)
) -> DefaultResponse:
    """Get a single report by its ID"""
    try:
        return await get_report_by_id(report_id, session)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete('/{report_id}', status_code=status.HTTP_200_OK)
async def delete_report_by_id(
    report_id: str,
    session: AsyncSession = Depends(get_db_session), current_user: User = Depends(get_current_user)
) -> DefaultResponse:
    """Delete a report by its ID"""
    try:
        return await delete_report(report_id, session)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
