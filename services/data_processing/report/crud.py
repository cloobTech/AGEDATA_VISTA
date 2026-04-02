import logging
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from models.report import Report
from models.project import Project
from models.project_member import ProjectMember
from models.user import User
from storage import db
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError
from services.data_processing.report.ai_report import interpret_result_with_ai
from schemas.default_response import DefaultResponse

_log = logging.getLogger(__name__)


async def create_report(data: dict, session: AsyncSession):
    """Create a new report"""

    project_id = data.get("project_id")
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")

    # AI report generation is a non-blocking enhancement.
    # If the Groq/AI call fails for any reason (invalid key, oversized content,
    # model unavailable, network error), the analysis result is still saved and
    # returned — ai_report will simply be None.
    try:
        data['ai_report'] = interpret_result_with_ai(data.get('summary', {}))
    except Exception as exc:
        _log.warning(
            "AI report generation skipped (non-fatal): %s: %s",
            type(exc).__name__, exc,
        )
        data['ai_report'] = None

    report = Report(**data)
    await report.save(session)
    return report.to_dict()


async def get_user_reports(
    user_id: str,
    analysis_group: Optional[str],
    session: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> DefaultResponse:
    """Get all reports for a user, optionally filtered by analysis_group"""

    # Check if the user exists
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")

    # Retrieve all projects the user is associated with
    projects = await db.filter(
        session, Project, Project.members.any(user_id=user_id)
    )
    if not projects:
        raise EntityNotFoundError("No projects found for the user")

    # Collect project IDs
    project_ids = [project.id for project in projects]

    # Build filters for the query
    filters = [Report.project_id.in_(project_ids)]
    if analysis_group:
        filters.append(Report.analysis_group == analysis_group)

    # Retrieve reports using the abstracted filter method
    reports = await db.filter(session, Report, *filters)

    # If no reports are found, return an empty list
    if not reports:
        return DefaultResponse(
            status="success",
            message=f"No Reports found with the given filters: {analysis_group}",
            data=[]
        )

    # Apply pagination (Phase 2I)
    page = reports[skip: skip + limit]

    exclude_items = ["_class_", "updated_at", "ai_report",
                     "project_id", "summary", "visualizations"]

    # Convert reports to dictionary format
    transformed_report = [report.to_dict(
        exclude=exclude_items) for report in page]

    return DefaultResponse(
        status="success",
        message=f"Reports found ",
        data=transformed_report
    )


async def _check_report_access(report: Report, caller_id: str, session: AsyncSession) -> None:
    """Raise HTTP 403 if the caller does not own the report's project and is not a member."""
    project = await db.get(session, Project, report.project_id)
    if not project:
        raise EntityNotFoundError("Associated project not found")
    if str(project.owner_id) == str(caller_id):
        return
    result = await session.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.user_id == caller_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="Forbidden")


async def get_report_by_id(report_id: str, session: AsyncSession, caller_id: str | None = None) -> DefaultResponse:
    """Get a single report by its ID.

    caller_id: when provided, enforces project ownership/membership.
    """
    report = await db.find_by(session, Report, id=report_id)
    if not report:
        raise EntityNotFoundError("Report not found")

    if caller_id is not None:
        await _check_report_access(report, caller_id, session)

    return DefaultResponse(
        status="success",
        message="Report found",
        data=report.to_dict()
    )


async def delete_report(report_id: str, session: AsyncSession, caller_id: str | None = None) -> DefaultResponse:
    """Delete a report by its ID.

    caller_id: when provided, only project owner/members may delete.
    """
    report = await db.get(session, Report, report_id)
    if not report:
        raise EntityNotFoundError("Report not found")

    if caller_id is not None:
        await _check_report_access(report, caller_id, session)

    await db.delete(session, report)

    return DefaultResponse(
        status="success",
        message="Report deleted successfully",
        data={}
    )
