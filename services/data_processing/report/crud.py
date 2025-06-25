from typing import Optional
from models.report import Report
from models.project import Project
from models.user import User
from storage import db
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError
from services.data_processing.report.ai_report import interpret_result_with_ai
from schemas.default_response import DefaultResponse


async def create_report(data: dict, session: AsyncSession):
    """Create a new report"""

    project_id = data.get("project_id")
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    data['ai_report'] = interpret_result_with_ai(data['summary'])
    report = Report(**data)
    await report.save(session)
    return report.to_dict()


async def get_user_reports(
    user_id: str,
    analysis_group: Optional[str],
    session: AsyncSession
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
        # Convert filters to a readable string format
    
        return DefaultResponse(
            status="success",
            message=f"No Reports found with the given filters: {analysis_group}",
            data=[]
        )

    exclude_items = ["_class_", "updated_at", "ai_report",
                     "project_id", "summary", "visualizations"]

    # Convert reports to dictionary format
    transformed_report = [report.to_dict(
        exclude=exclude_items) for report in reports]

    return DefaultResponse(
        status="success",
        message=f"Reports found ",
        data=transformed_report
    )


async def get_report_by_id(report_id: str, session: AsyncSession) -> DefaultResponse:
    """Get a single report by its ID"""
    # Retrieve the report using the abstracted `find_by` method
    report = await db.find_by(session, Report, id=report_id)
    if not report:
        raise EntityNotFoundError("Report not found")

    return DefaultResponse(
        status="success",
        message="Report found",
        data=report.to_dict()
    )


async def delete_report(report_id: str, session: AsyncSession) -> DefaultResponse:
    """Delete a report by its ID"""
    # Retrieve the report using the abstracted `get` method
    report = await db.get(session, Report, report_id)
    if not report:
        raise EntityNotFoundError("Report not found")

    # Delete the report
    await db.delete(session, report)

    return DefaultResponse(
        status="success",
        message="Report deleted successfully",
        data={}
    )
