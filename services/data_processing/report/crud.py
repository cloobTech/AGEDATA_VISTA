from models.report import Report
from models.project import Project
from storage import db
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError
from services.data_processing.report.ai_report import interpret_result_with_ai


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
