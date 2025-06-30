from sqlalchemy.ext.asyncio import AsyncSession
from schemas.default_response import DefaultResponse
from models.notification import Notification
from models.notification_recipient import NotificationRecipient
from errors.exceptions import EntityNotFoundError, DataRequiredError
from storage import db


async def create_notification(session: AsyncSession, data: dict):
    data_copy = data.copy()
    user_ids = data_copy.pop("user_ids")

    # we can go further to validate if the user ids matches actual users...

    notification = Notification(**data_copy)

    notification.recipients = [
        NotificationRecipient(user_id=user_id) for user_id in user_ids
    ]

    session.add(notification)


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
        data=None
    )


async def update_notification(notification_id: str, notification_data: dict, session: AsyncSession) -> DefaultResponse:
    """Update notification"""
    notification = await db.get(session, Notification, notification_id)
    if not notification:
        raise EntityNotFoundError('Notification object not found')
    if not notification_data:
        raise DataRequiredError('Data required')
    await notification.update(session, notification_data)

    return DefaultResponse(
        status="success",
        message="Notification updated successfully",
        data=notification.to_dict()
    )
