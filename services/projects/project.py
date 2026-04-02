from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.project import Project
from models.user import User
from models.project_member import ProjectMember
from storage import db
from services.projects.helper import instantiate_project_members_with_project_owner
from schemas.default_response import DefaultResponse
from schemas.project import CreateProject

# Whitelist of SQLAlchemy relationship names that may be eagerly loaded.
# Never allow user-controlled strings to be used as attribute names without
# checking against this set first.
ALLOWED_RELATIONSHIPS = {"members", "reports", "files", "settings", "invitations"}


async def _check_project_access(project: Project, caller_id: str, session: AsyncSession) -> None:
    """Raise HTTP 403 if caller is neither the project owner nor a project member."""
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


async def get_all_projects(session: AsyncSession, user_id: str) -> DefaultResponse:
    """Get all projects owned by or shared with the given user"""
    # Projects the user owns OR is a member of via collaboration
    result = await session.execute(
        select(Project)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .where(
            or_(
                Project.owner_id == user_id,
                ProjectMember.user_id == user_id,
            )
        )
        .distinct()
    )
    projects = result.scalars().all()
    if not projects:
        return DefaultResponse(
            status="success",
            message="No projects found",
            data=[]
        )
    return DefaultResponse(
        status="success",
        message="Projects found",
        data=[project.to_dict() for project in projects]
    )


async def get_project_by_id(project_id: str, params: str, session: AsyncSession, caller_id: str | None = None):
    """Get a project by its ID.

    caller_id: the ID of the authenticated user making the request.
    When provided, enforces that the caller is the owner or a project member.
    """
    param_list = [param.strip()
                  for param in params.split(",")] if params else None
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")

    # Ownership / membership gate
    if caller_id is not None:
        await _check_project_access(project, caller_id, session)

    # Load eagerly requested relationships — only from the whitelist
    if param_list:
        for relationship in param_list:
            if relationship not in ALLOWED_RELATIONSHIPS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid relationship parameter: '{relationship}'"
                )
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


async def update_project(project_id: str, project_data: dict, session: AsyncSession, caller_id: str | None = None):
    """Update a project by its ID.

    caller_id: when provided, only the project owner may update.
    """
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    if caller_id is not None and str(project.owner_id) != str(caller_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    if len(project_data) == 0:
        raise DataRequiredError("No data provided to update project")
    await project.update(session, project_data)
    return DefaultResponse(
        status="success",
        message="Project updated",
        data=project.to_dict()
    )


async def delete_project(project_id: str, session: AsyncSession, caller_id: str | None = None) -> str:
    """Delete a project by its ID.

    caller_id: when provided, only the project owner may delete.
    """
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    if caller_id is not None and str(project.owner_id) != str(caller_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    await project.delete(session)
    return DefaultResponse(
        status="success",
        message="Project deleted",
        data={"project_id": project_id}
    )
