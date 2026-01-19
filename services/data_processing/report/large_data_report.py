from storage import db
from storage.celery_db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.default_response import DefaultResponse
from models.big_data_result import BigDataResult
from models.user import User
from errors.exceptions import EntityNotFoundError
from services.data_processing.report.ai_report import interpret_result_with_ai


def create_large_data_report(
    report_data: dict,
) -> None:
    """Create a new large data report"""

    report_data['ai_insights'] = interpret_result_with_ai(
        report_data['data_summary'])
    new_report = BigDataResult(**report_data)

    with SessionLocal() as session:
        session.add(new_report)  # Save the report to the database new_report
        session.commit()


async def get_large_data_report_by_id(
    report_id: str,
    session: AsyncSession

) -> DefaultResponse:
    """Retrieve a large data report by its ID"""

    report = await db.get(session, BigDataResult, report_id)
    if not report:
        return DefaultResponse(
            status="error",
            message="Large data report not found",
            data={}
        )
    return DefaultResponse(
        status="success",
        message="Large data report retrieved successfully",
        data=report.to_dict()
    )


async def delete_large_data_report(
    report_id: str,
    session: AsyncSession
) -> DefaultResponse:
    """Delete a large data report by its ID"""

    report = await db.get(session, BigDataResult, report_id)
    if not report:
        return DefaultResponse(
            status="error",
            message="Large data report not found",
            data={}
        )
    await report.delete(session)
    return DefaultResponse(
        status="success",
        message="Large data report deleted successfully",
        data={}
    )


async def list_large_data_reports(
        user_id: str,
    session: AsyncSession
) -> DefaultResponse:
    """List all large data reports"""
    user = await db.get(session, User, user_id)
    if not user:
        return DefaultResponse(
            status="error",
            message="User not found",
            data={}
        )

    reports = await db.filter(session, BigDataResult, BigDataResult.user_id == user_id)
    if not reports:
        return DefaultResponse(
            status="success",
            message="No large data reports found",
            data=[]
        )
    report_list = [report.to_dict() for report in reports]
    return DefaultResponse(
        status="success",
        message="Large data reports retrieved successfully",
        data=report_list
    )


async def update_large_data_report(
    report_id: str,
    update_data: dict,
    session: AsyncSession
) -> DefaultResponse:
    """Update a large data report by its ID"""

    report = await db.get(session, BigDataResult, report_id)
    if not report:
        return DefaultResponse(
            status="error",
            message="Large data report not found",
            data={}
        )

    await report.update(session, update_data)

    return DefaultResponse(
        status="success",
        message="Large data report updated successfully",
        data=report.to_dict()
    )
