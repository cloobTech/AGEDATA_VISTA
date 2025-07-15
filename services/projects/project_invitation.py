from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, APermissionError
from storage import db
from schemas.default_response import DefaultResponse
from models.project_member import ProjectMember
from models.project_invitation import ProjectInvitation
from models.project import Project
from services.projects.helper import check_existing_member, check_pending_invitation
from services.notifications.crud import create_notification


async def send_email(email: str = "sam@sample.com", message: str = "Hello"):
    """send an email to a user"""
    print(f"Email sent to {email}: {message}")
    pass


async def invite_project_member(project_id: str, raw_data: dict, session: AsyncSession):
    """Send a project invitation to a user"""
    data = raw_data.copy()
    user_ids = data.get("user_ids")  # Optional (if user exists)
    email = data.pop("email", None)  # Optional (if user is not registered)
    acting_user_id = data.pop("acting_user_id")
    role = data.pop('role')
    invitations = []

    if not user_ids:
        raise ValueError("Must Provide atleast one recipient's id")

    acting_user = await db.filter(session, ProjectMember, ProjectMember.project_id == project_id, ProjectMember.user_id == acting_user_id, fetch_one=True)
    if not acting_user or acting_user.role not in ["owner", "admin"]:
        raise APermissionError(
            "Permission denied. Only an owner or admin can send invitations")

    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")

    if user_ids:
        for user_id in user_ids:
            await check_existing_member(session, project_id, user_id)
            await check_pending_invitation(session, project_id, user_id=user_id)

            invitation = ProjectInvitation(
                project_id=project_id,
                invited_user_id=user_id,
                status="pending",
                role=role
            )
            invitations.append(invitation)
            session.add(invitation)

        await create_notification(session, data)

    elif email:
        await check_pending_invitation(session, project_id, email=email)

        invitation = ProjectInvitation(
            project_id=project_id,
            email=email,
            status="pending"
        )
        invitations.append(invitation)
        session.add(invitation)

        await send_email(email, f"You've been invited to join project {project.title}. Register to accept the invitation.")

    await session.commit()

    return DefaultResponse(
        status="success",
        message="Project invitation sent",
        data={"invitation_ids": [inv.id for inv in invitations]}
    )


async def respond_to_invitation(project_id: str, raw_data: dict, session: AsyncSession):
    """Accept or decline a project invitation"""
    data = raw_data.copy()
    invitation_id = data.pop("invitation_id")
    user_id = data.pop("respondent_id")
    response = data.pop("response")

    project = await db.get(session, Project, project_id)
    if not project:
        raise EntityNotFoundError("Project not found")

    invitation = await db.get(session, ProjectInvitation, invitation_id)
    if not invitation or invitation.status != "pending":
        raise EntityNotFoundError("Invalid or expired invitation")

    if response == "accepted":
        # Add user to project members
        new_member = ProjectMember(
            project_id=invitation.project_id,
            user_id=user_id,
            role=invitation.role
        )
        session.add(new_member)

    # Update invitation status
    invitation.status = response

    data['message'] = f"User {response} invitation"

    await create_notification(session, data)

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
