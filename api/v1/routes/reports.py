from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.utils.get_db_session import get_db_session
from services.data_processing.report.crud import get_user_reports, get_report_by_id, delete_report
from errors.exceptions import EntityNotFoundError
from schemas.default_response import DefaultResponse
from api.v1.utils.current_user import get_current_user
from models.user import User
from utils.audit_log import audit


router = APIRouter(tags=['Analysis Reports'], prefix='/api/v1/reports')


@router.get('/', status_code=status.HTTP_200_OK)
async def fetch_user_reports(
    user_id: str,
    analysis_group: str | None = None,
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum records to return"),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> DefaultResponse:
    """Get all reports for a user, optionally filtered by analysis_group.

    Supports pagination via `skip` and `limit` query parameters.
    """
    # IDOR guard: callers may only fetch their own reports
    if str(user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    try:
        reports = await get_user_reports(user_id, analysis_group, session, skip=skip, limit=limit)
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
        return await get_report_by_id(report_id, session, caller_id=current_user.id)
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
        result = await delete_report(report_id, session, caller_id=current_user.id)
        audit("DELETE_REPORT", user_id=str(current_user.id), resource_id=report_id,
              resource_type="report")
        return result
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
