from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, APermissionError
from models.project import Project
from models.user import User
from models.project_member import ProjectMember
from schemas.default_response import DefaultResponse
from storage import db


class ProjectRole(str, Enum):
    """Enumeration of valid project member roles.

    Using str+Enum means the values compare correctly against DB strings:
      ProjectRole("owner") == "owner"  → True

    Replace bare string comparisons with ProjectRole to prevent typo-based
    privilege escalation (e.g. "Owner" vs "owner").
    """
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


_PRIVILEGED_ROLES = {ProjectRole.OWNER, ProjectRole.ADMIN}
_PROTECTED_ROLES = {ProjectRole.OWNER, ProjectRole.ADMIN}


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
    # Use enum comparison to prevent typo-based privilege escalation
    try:
        acting_role = ProjectRole(acting_user.role) if acting_user else None
    except ValueError:
        acting_role = None
    if not acting_user or acting_role not in _PRIVILEGED_ROLES:
        raise APermissionError(
            "Permission denied. Only an owner or admin can remove members.")
    try:
        member_role = ProjectRole(project_member.role)
    except ValueError:
        member_role = None
    if member_role in _PROTECTED_ROLES:
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
    try:
        acting_role = ProjectRole(acting_user.role) if acting_user else None
    except ValueError:
        acting_role = None
    if not acting_user or acting_role not in _PRIVILEGED_ROLES:
        raise APermissionError(
            "Permission denied. Only an owner or admin can update a member's role.")
    await project_member.update(session, data)
    return DefaultResponse(
        status="success",
        message="Operation successful",
        data=project_member.to_dict()
    )
