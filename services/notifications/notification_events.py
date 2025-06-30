from services.notifications.crud import create_notification
from sqlalchemy.ext.asyncio import AsyncSession
from models.notification_recipient import NotificationRecipient


async def notification_helper(session: AsyncSession, data: dict):
    data_copy = data.copy()
    user_ids = data_copy.pop("user_ids")

    # we can go further to validate if the user ids matches actual users...

    notification = create_notification(data_copy)

    notification.recipients = [
        NotificationRecipient(user_id=user_id) for user_id in user_ids
    ]

    session.add(notification)
