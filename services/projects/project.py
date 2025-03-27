from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.project import Project
from models.user import User
from storage import db
from services.projects.helper import instantiate_project_members_with_project_owner
from schemas.default_response import DefaultResponse
from schemas.project import CreateProject


async def get_all_projects(session: AsyncSession) -> DefaultResponse:
    """Get all projects from the database"""
    projects = await db.all(session, Project)
    if not projects:
        return DefaultResponse(
            status="success",
            message="No projects found",
            data=[]
        )
    project_data = [project.to_dict() for project in projects.values()]
    return DefaultResponse(
        status="success",
        message="Projects found",
        data=project_data
    )


async def get_project_by_id(project_id: str, params: str, session: AsyncSession):
    """Get a project by its ID"""
    param_list = [param.strip()
                  for param in params.split(",")] if params else None
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    if param_list:
        for relationship in param_list:
            try:
                await getattr(project.awaitable_attrs, relationship)
            except AttributeError:
                pass
    return DefaultResponse(
        status="success",
        message="Project found",
        data=project.to_dict(include=param_list)
    )


async def create_project(data: CreateProject, session: AsyncSession):
    """Create a new project"""
    project_data = data.model_dump()
    owner_id = project_data.get("owner_id")
    owner = await db.get(session, User, owner_id)
    if not owner:
        raise EntityNotFoundError("Must provide a valid owner ID")
    project = Project(**project_data)
    project_member = instantiate_project_members_with_project_owner(
        owner, project)
    db.add_all(session, [project, project_member])
    await db.save(session)
    return DefaultResponse(
        status="success",
        message="Project created",
        data=project.to_dict()
    )


async def update_project(project_id: str, project_data: dict, session: AsyncSession):
    """Update a project by its ID"""
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    if len(project_data) == 0:
        raise DataRequiredError("No data provided to update project")
    await project.update(session, project_data)
    return DefaultResponse(
        status="success",
        message="Project updated",
        data=project.to_dict()
    )


async def delete_project(project_id: str, session: AsyncSession) -> str:
    """Delete a project by its ID"""
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    await project.delete()
    return DefaultResponse(
        status="success",
        message="Project deleted",
        data=project_id
    )
