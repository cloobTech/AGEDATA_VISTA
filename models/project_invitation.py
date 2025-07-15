# ruff: noqa
# pyright: ignore-all

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base_model import BaseModel, Base


class ProjectInvitation(BaseModel, Base):
    """"Invite a user to a project"""
    __tablename__ = "project_invitations"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), nullable=False)
    invited_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=True)
    role: Mapped[str] = mapped_column(nullable=False, default="viewer")

    # Email if the user isn't on the platform
    email: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(default="pending", nullable=False)

    project: Mapped["Project"] = relationship(back_populates="invitations")
    invited_user: Mapped["User"] = relationship(
        back_populates="invitations")
