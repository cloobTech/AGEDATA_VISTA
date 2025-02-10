from errors.exceptions import EntityNotFoundError
from models.project import Project
from models.user import User
from models.project_member import ProjectMember
from models.project import Project
from schemas.default_response import DefaultResponse
from storage import DBStorage


async def add_project_member(data: dict, storage: DBStorage):
    """ Add  a new member to a project"""
    project_id = data.get("project_id")
    user_id = data.get("user_id")
    project = await storage.get(Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    user = await storage.get(User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    await storage.merge(user)
    await storage.merge(project)
    project_member = ProjectMember(project=project, user=user)
    await project_member.save()
    return DefaultResponse(
        status="success",
        message="Project member created",
        data=project_member.to_dict()
    )


async def remove_project_member(data: dict, storage: DBStorage):
    """Remove a project member"""
    project_id = data.get("project_id")
    member_id = data.get("member_id")
    acting_user_id = data.get("acting_user_id")
    project = await storage.get(Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    project_member = await storage.filter(ProjectMember, project_id=project_id, user_id=member_id, first=True)
    if not project_member:
        raise EntityNotFoundError("User is not a member of this project")
    acting_user = await storage.filter(ProjectMember, project_id=project_id, user_id=acting_user_id, first=True)
    if not acting_user or acting_user.role not in ["owner", "admin"]:
        raise EntityNotFoundError(
            "Permission denied. Only an owner or admin can remove members.")
    if project_member.role in ["owner", "admin"]:
        raise EntityNotFoundError(
            "Permission denied. You cannot remove an owner or admin.")
    await project_member.delete()
    return DefaultResponse(
        status="success",
        message="Project member removed",
        data=project_member.to_dict()
    )


async def update_project_member_access(data: dict, storage: DBStorage):
    """Update a project member's role access"""
    project_id = data.get("project_id")
    member_id = data.get("member_id")
    acting_user_id = data.get("acting_user_id")
    project = await storage.get(Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")
    project_member = await storage.filter(ProjectMember, project_id=project_id, user_id=member_id, first=True)
    if not project_member:
        raise EntityNotFoundError("User is not a member of this project")
    acting_user = await storage.filter(ProjectMember, project_id=project_id, user_id=acting_user_id, first=True)
    if not acting_user or acting_user.role not in ["owner", "admin"]:
        raise EntityNotFoundError(
            "Permission denied. Only an owner or admin can update a  member's role.")
    await project_member.update(data)
    return DefaultResponse(
        status="success",
        message="Operation successful",
        data=project_member.to_dict()
    )
