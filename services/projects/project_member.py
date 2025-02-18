from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, APermissionError
from models.project import Project
from models.user import User
from models.project_member import ProjectMember
from schemas.default_response import DefaultResponse
from storage import db


async def add_project_member(data: dict, session: AsyncSession):
    """ Add  a new member to a project"""
    project_member_id = data.get(
        "project_member_id")  # This should be table containing project members
    user_id = data.get("user_id")
    project_member_table = await db.get(session, ProjectMember, project_member_id)
    if not project_member_table:
        raise EntityNotFoundError("Project member not found")
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    # await project_member.save(session)
    return DefaultResponse(
        status="success",
        message="Project member created",
        data={}
    )


async def remove_project_member(data: dict, session: AsyncSession):
    """Remove a project member"""
    project_id = data.get("project_id")
    member_id = data.get("member_id")
    acting_user_id = data.get("acting_user_id")
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    project_member = await db.filter(session, ProjectMember, ProjectMember.project_id == project_id, ProjectMember.user_id == member_id, fetch_one=True)
    if not project_member:
        raise EntityNotFoundError("User is not a member of this project")
    acting_user = await db.filter(session, ProjectMember, ProjectMember.project_id == project_id, ProjectMember.user_id == acting_user_id, fetch_one=True)
    if not acting_user or acting_user.role not in ["owner", "admin"]:
        raise APermissionError(
            "Permission denied. Only an owner or admin can remove members.")
    if project_member.role in ["owner", "admin"]:
        raise APermissionError(
            "Permission denied. You cannot remove an owner or admin.")
    await project_member.delete(session)
    return DefaultResponse(
        status="success",
        message="Project member removed",
        data=project_member.to_dict()
    )


async def update_project_member_access(data: dict, session: AsyncSession):
    """Update a project member's role access"""
    project_id = data.get("project_id")
    member_id = data.get("member_id")
    acting_user_id = data.get("acting_user_id")
    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    project_member = await db.filter(session, ProjectMember, ProjectMember.project_id==project_id, ProjectMember.user_id==member_id, fetch_one=True)
    if not project_member:
        raise EntityNotFoundError("User is not a member of this project")
    acting_user = await db.filter(session, ProjectMember, ProjectMember.project_id == project_id, ProjectMember.user_id == acting_user_id, fetch_one=True)
    if not acting_user or acting_user.role not in ["owner", "admin"]:
        raise APermissionError(
            "Permission denied. Only an owner or admin can update a  member's role.")
    await project_member.update(session, data)
    return DefaultResponse(
        status="success",
        message="Operation successful",
        data=project_member.to_dict()
    )
