from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.project import Project
from models.user import User
from storage import DBStorage
from services.projects.helper import instantiate_project_members_with_project_owner
from schemas.default_response import DefaultResponse
from sqlalchemy import select


async def get_all_projects(storage: DBStorage):
    """Get all projects from the database"""
    projects = await storage.all(Project)
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


async def get_project_by_id(project_id: str, storage: DBStorage):
    """Get a project by its ID"""
    project = await storage.get(Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    return DefaultResponse(
        status="success",
        message="Project found",
        data=project.to_dict()
    )


async def create_project(project_data: dict, storage: DBStorage):
    """Create a new project"""

    async for session in storage.db_session():
        owner_id = project_data.get("owner_id")
        # owner = await storage.get(User, owner_id)
        result = await session.execute(select(User).filter(User.id == owner_id))
        owner = result.scalar_one_or_none()
        if not owner:
            raise EntityNotFoundError("Must provide a valid owner ID")
        project = Project(**project_data, owner=owner)
        # await storage.merge(owner)
        project_member = instantiate_project_members_with_project_owner(
            owner, project)
        session.add_all([project, project_member])
        await session.commit()
        return DefaultResponse(
            status="success",
            message="Project created",
            data=project.to_dict()
        )


async def update_project(project_id: str, project_data: dict, storage: DBStorage):
    """Update a project by its ID"""
    project = await storage.get(Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    if len(project_data) == 0:
        raise DataRequiredError("No data provided to update project")
    await storage.merge(project)
    await project.update(project_data)
    return DefaultResponse(
        status="success",
        message="Project updated",
        data=project.to_dict()
    )


async def delete_project(project_id: str, storage: DBStorage) -> str:
    """Delete a project by its ID"""
    project = await storage.get(Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    await project.delete()
    return DefaultResponse(
        status="success",
        message="Project deleted",
        data=project_id
    )
