# ruff: noqa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base


class NotificationRecipient(BaseModel, Base):
    """Link between Notifications and Users with read status"""
    __tablename__ = "notification_recipients"

    notification_id: Mapped[str] = mapped_column(
        ForeignKey("notifications.id"), primary_key=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)

    notification: Mapped["Notification"] = relationship(
        back_populates="recipients"
    )
    user: Mapped["User"] = relationship(
        back_populates="notification_recipients"
    )
