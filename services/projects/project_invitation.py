from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, EntityConflictError
from storage import db
from schemas.default_response import DefaultResponse
from models.project_member import ProjectMember
from models.project_invitation import ProjectInvitation
from models.project import Project


def send_notification(user_id: str, message: str):
    """send a notification to a user"""
    pass

def send_email(email: str, message: str):
    """send an email to a user"""
    pass

async def invite_project_member(data: dict, session: AsyncSession):
    """Send a project invitation to a user"""
    project_id = data.get("project_id")
    user_id = data.get("user_id")  # Optional (if user exists)
    email = data.get("email")  # Optional (if user is not registered)

    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")

    # If user exists, check if they are already in the project
    if user_id:
        existing_member = await db.filter(
            session, ProjectMember,
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
            fetch_one=True
        )
        if existing_member:
            raise EntityConflictError("User is already a project member")

    # Create an invitation
    invitation = ProjectInvitation(
        project_id=project_id,
        invited_user_id=user_id if user_id else None,
        email=email if not user_id else None,
        status="pending"
    )

    session.add(invitation)
    await session.commit()

    # Send notification if user exists, or send an email if not registered
    if user_id:
        await send_notification(user_id, f"You have been invited to join project {project.name}")
    else:
        await send_email(email, f"You've been invited to join project {project.name}. Register to accept the invitation.")

    return DefaultResponse(
        status="success",
        message="Project invitation sent",
        data={"invitation_id": invitation.id}
    )


async def respond_to_invitation(data: dict, session: AsyncSession):
    """Accept or decline a project invitation"""
    invitation_id = data.get("invitation_id")
    user_id = data.get("user_id")
    response = data.get("response")  # "accepted" or "declined"

    invitation = await db.get(session, ProjectInvitation, invitation_id)
    if not invitation or invitation.status != "pending":
        raise EntityNotFoundError("Invalid or expired invitation")

    if response == "accepted":
        # Add user to project members
        new_member = ProjectMember(
            project_id=invitation.project_id,
            user_id=user_id,
            role="member"
        )
        session.add(new_member)

    # Update invitation status
    invitation.status = response
    await session.commit()

    return DefaultResponse(
        status="success",
        message=f"Invitation {response}",
        data={}
    )


# async def check_pending_invitations(user_email: str, session: AsyncSession):
#     """Check if a newly registered user has pending invitations"""
#     invitations = await db.filter(
#         session, ProjectInvitation,
#         ProjectInvitation.email == user_email,
#         ProjectInvitation.status == "pending"
#     )
#     for invitation in invitations:
#         # Update the invitation to assign the new user ID
#         invitation.invited_user_id = user.id
#         await session.commit()

#         # Notify the user
#         await send_notification(user.id, f"You have been invited to join project {invitation.project.name}")
