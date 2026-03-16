from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.default_response import DefaultResponse
from models.notification import Notification
from models.notification_recipient import NotificationRecipient
from errors.exceptions import EntityNotFoundError, DataRequiredError
from storage import db


async def create_notification(session: AsyncSession, data: dict):
    data_copy = data.copy()
    user_ids = data_copy.pop("user_ids")

    notification = Notification(**data_copy)

    notification.recipients = [
        NotificationRecipient(user_id=user_id) for user_id in user_ids
    ]

    session.add(notification)
    # await session.commit()
    # return notification


async def get_user_notifications(session, user_id: str) -> DefaultResponse:
    stmt = (
        select(Notification, NotificationRecipient)
        .join(Notification.recipients)
        .where(NotificationRecipient.user_id == user_id)
        .options(selectinload(Notification.sender))
    )
    result = await session.execute(stmt)
    rows = result.all()
    data = [
        {**notification.to_dict(), "is_read": recipient.is_read}
        for notification, recipient in rows
    ]
    return DefaultResponse(
        status="success",
        message="Notifications found",
        data=data
    )


async def get_notification_by_id(notification_id: str, session: AsyncSession) -> DefaultResponse:
    """Get notification by id"""
    notification = await db.get(session, Notification, notification_id)
    if not notification:
        raise EntityNotFoundError('Notification not found')
    return DefaultResponse(
        status="success",
        message="Notification found",
        data=notification.to_dict()
    )


async def delete_notification(notification_id: str, session: AsyncSession) -> DefaultResponse:
    """Delete notification"""
    notification = await db.get(session, Notification, notification_id)

    if not notification:
        raise EntityNotFoundError('Notification object not found')
    await db.delete(session, notification)
    return DefaultResponse(
        status="success",
        message="Notification deleted successfully",
        data={}
    )


async def update_notification(notification_id: str, notification_data: dict, session: AsyncSession, user_id: str = None) -> DefaultResponse:
    """Update notification"""
    notification = await db.get(session, Notification, notification_id)
    user_id = user_id or notification_data.get("user_id", None)
    if not user_id:
        raise DataRequiredError("Please include the user's id")
    if not notification:
        raise EntityNotFoundError('Notification object not found')
    if not notification_data:
        raise DataRequiredError('Data required')
    recipient = await db.filter(
        session,
        NotificationRecipient,
        NotificationRecipient.user_id == user_id,
        NotificationRecipient.notification_id == notification_id,
        fetch_one=True
    )

    await recipient.update(session, notification_data)

    return DefaultResponse(
        status="success",
        message="Notification updated successfully",
        data={
            "notification_id": notification_id,
            "user_id": user_id,
            "is_read": recipient.is_read,
        }
    )
