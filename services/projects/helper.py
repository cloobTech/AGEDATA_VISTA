from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import  EntityConflictError
from storage import db
from models.project_member import ProjectMember
from models.project_invitation import ProjectInvitation
from models.project_member import ProjectMember


def instantiate_project_members_with_project_owner(owner, project) -> ProjectMember:
    """Basically, This function will be called when a user creates a new project"""

    project_member = ProjectMember(
        user_id=owner.id, project_id=project.id, role="owner")
    return project_member



async def check_existing_member(session: AsyncSession, project_id: str, user_id: str):
    existing_member = await db.filter(
        session, ProjectMember,
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
        fetch_one=True
    )
    if existing_member:
        raise EntityConflictError("User is already a project member")


async def check_pending_invitation(session: AsyncSession, project_id: str, user_id: str = None, email: str = None):
    if user_id:
        pending_invitation = await db.filter(
            session, ProjectInvitation,
            ProjectInvitation.project_id == project_id,
            ProjectInvitation.invited_user_id == user_id,
            ProjectInvitation.status == "pending",
            fetch_one=True
        )
        if pending_invitation:
            raise EntityConflictError("User already has a pending invitation")
    if email:
        pending_invitation = await db.filter(
            session, ProjectInvitation,
            ProjectInvitation.project_id == project_id,
            ProjectInvitation.email == email,
            ProjectInvitation.status == "pending",
            fetch_one=True
        )
        if pending_invitation:
            raise EntityConflictError("Email already has a pending invitation")