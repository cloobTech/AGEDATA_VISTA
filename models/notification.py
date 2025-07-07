# ruff: noqa
from sqlalchemy import String,  Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base


class Notification(BaseModel, Base):
    """Notification Class"""
    __tablename__ = "notifications"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_type: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    resource_id: Mapped[str] = mapped_column(nullable=False)
    sender_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    sender: Mapped["User"] = relationship(
        back_populates="sent_notifications"
    )

    recipients: Mapped[list["NotificationRecipient"]] = relationship(
        back_populates="notification",
        cascade="all, delete-orphan"
    )
