from sqlalchemy.future import select
import cloudinary.api
from fastapi import UploadFile
from io import BytesIO
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from errors.exceptions import EntityNotFoundError,  DataRequiredError
from storage import db
from schemas.default_response import DefaultResponse
from models.user import User
from utils.extract_cloudinary_public_id import extract_cloudinary_public_id_and_type
from models.notification import Notification
from models.notification_recipient import NotificationRecipient
from models.report import Report
from models.project import Project
from models.project_member import ProjectMember


async def get_all_users(session: AsyncSession):
    users = await db.all(session, User)
    if not users:
        return DefaultResponse(
            status="success",
            message="No users found",
            data=[]
        )
    user_data = [user.to_dict() for user in users.values()]
    return DefaultResponse(
        status="success",
        message="Users found",
        data=user_data
    )


async def get_user_by_id(user_id: str, params: str, session: AsyncSession):
    param_list = [param.strip()
                  for param in params.split(",")] if params else None
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    if param_list:
        for relationship in param_list:
            try:
                await getattr(user.awaitable_attrs, relationship)
            except AttributeError:
                pass
    return DefaultResponse(
        status="success",
        message="User found",
        data=user.to_dict(include=param_list)
    )


async def update_user(user_id: str, user_data: dict, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    if not user_data:
        raise DataRequiredError("Must provide data to update")
    await user.update(session, user_data)
    return DefaultResponse(
        status="success",
        message="User updated",
        data=user.to_dict()
    )


async def upload_user_picture(file: UploadFile, user_id: str, session: AsyncSession):
    """Upload a picture to Cloudinary and associate it with a user."""
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("Must provide a valid user ID")

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png", "gif"]:
        raise ValueError(
            f"Unsupported file type: {file_extension}. Use 'jpg', 'jpeg', 'png', or 'gif'.")

    # Read and validate file content
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10 MB
        raise ValueError("File size exceeds the 10 MB limit.")

    # Delete the existing profile picture from Cloudinary if it exists
    if user.profile_picture:
        public_id, _ = extract_cloudinary_public_id_and_type(
            (user.profile_picture))
        try:
            public_id = public_id
            cloudinary.api.delete_resources(
                public_id, resource_type="image", type="upload")
        except Exception as e:
            raise ValueError(
                f"Failed to delete existing profile picture: {str(e)}")

    # Upload the new picture to Cloudinary
    response = cloudinary.uploader.upload(
        BytesIO(file_content),
        folder="AgeDataUserPictures",
        resource_type="image",
        overwrite=True
    )

    # Update user profile picture URL and save
    user.profile_picture = response["secure_url"]
    await user.save(session)

    return DefaultResponse(
        status="success",
        message="User picture uploaded successfully",
        data=user.to_dict()
    )


async def delete_user(user_id: str, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    await db.delete(session, user)
    return DefaultResponse(
        status="success",
        message="User deleted",
        data=user.to_dict()
    )


# async def get_user_notifications(user_id: str, session: AsyncSession):
#     user = await db.get(session, User, user_id)
#     if not user:
#         raise EntityNotFoundError("User not found")
#     notification_rows = await db.filter_join_pair(
#         session,
#         Notification,
#         NotificationRecipient,
#         Notification.id == NotificationRecipient.notification_id,
#         NotificationRecipient.user_id == user_id
#     )

#     notifications = []
#     for notification, recipient in notification_rows:
#         notifications.append({
#             **notification.to_dict(),
#             "is_read": recipient.is_read
#         })

#     return DefaultResponse(
#         status="success",
#         message="User's notification fetched successfully",
#         data=notifications
#     )


async def get_user_notifications(user_id: str, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")

    stmt = (
        select(Notification, NotificationRecipient)
        .join(NotificationRecipient, Notification.id == NotificationRecipient.notification_id)
        .where(NotificationRecipient.user_id == user_id)
        .options(
            selectinload(Notification.sender),
            selectinload(NotificationRecipient.user)
        )
    )
    result = await session.execute(stmt)
    rows = result.all()

    notifications = []
    for notification, recipient in rows:
        notifications.append({
            **notification.to_dict(),
            "is_read": recipient.is_read,
            "sender": {
                "id": notification.sender.id,
                "email": notification.sender.email,
                "first_name": notification.sender.first_name,
                "last_name": notification.sender.last_name,
                "profile_picture": notification.sender.profile_picture,
            },
            "recipient_user": {
                "id": recipient.user.id,
                "email": recipient.user.email,
                "first_name": recipient.user.first_name,
                "last_name": recipient.user.last_name,
                "profile_picture": recipient.user.profile_picture
            }
        })

    return DefaultResponse(
        status="success",
        message="User's notifications fetched successfully",
        data=notifications
    )


async def get_user_report_statistics(user_id: str, session: AsyncSession):
    # Grouped counts
    grouped = await db.count_grouped_join(
        session,
        Report,
        Project,
        Report.project_id == Project.id,
        Report.analysis_group,
        Project.owner_id == user_id
    )

    # Total projects
    project_count = await db.count_where(
        session,
        Project,
        Project.owner_id == user_id
    )

    # 👉 Get recent top 3 reports with name & analysis_group
    stmt = (
        select(Report.title, Report.analysis_group)
        .join(Project, Report.project_id == Project.id)
        .where(Project.owner_id == user_id)
        .order_by(desc(Report.created_at))  # Make sure you have this!
        .limit(3)
    )
    recent_reports_result = await session.execute(stmt)
    recent_reports = [
        {"name": row[0], "analysis_group": row[1]}
        for row in recent_reports_result.fetchall()
    ]

    result = {
        "total_reports": sum([row[1] for row in grouped]),
        "total_project": project_count,
        "breakdown": [
            {"analysis_group": row[0], "count": row[1]}
            for row in grouped
        ],
        "recent_reports": recent_reports
    }

    return DefaultResponse(
        status="success",
        message="User's statistics fetched successfully",
        data=result
    )


# async def get_user_projects(user_id: str, session: AsyncSession):
#     """Get user's projects"""

#     projects = await db.filter_join(
#         session,
#         Project,
#         ProjectMember,
#         Project.id == ProjectMember.project_id,
#         ProjectMember.user_id == user_id
#     )

#     results = [project.to_dict() for project in projects]

#     return DefaultResponse(
#         status="success",
#         message="Projects fetched",
#         data=results
#     )


async def get_user_projects(user_id: str, session: AsyncSession):
    """Get user's projects with owner's name"""

    # Better: explicit join with User
    stmt = (
        select(Project, User)
        .join(ProjectMember, Project.id == ProjectMember.project_id)
        .join(User, Project.owner_id == User.id)
        .where(ProjectMember.user_id == user_id)
    )

    results = await session.execute(stmt)
    rows = results.all()

    data = []
    for project, owner in rows:
        proj_dict = project.to_dict()
        proj_dict["owner_name"] = f"{owner.first_name} {owner.last_name}"
        data.append(proj_dict)

    return DefaultResponse(
        status="success",
        message="Projects fetched",
        data=data
    )
