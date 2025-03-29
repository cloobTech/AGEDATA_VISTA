# ruff: noqa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base_model import BaseModel, Base


class Project(BaseModel, Base):
    """ Project Class """
    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    visibility: Mapped[str] = mapped_column(
        nullable=False, default="public")  # public or private

    owner: Mapped["User"] = relationship(
        back_populates="owned_projects", uselist=False)
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=True)
    invitations: Mapped[list["ProjectInvitation"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=True
    )
    files: Mapped[list["UploadedFile"]] = relationship(
        back_populates="projects", uselist=True)
    reports: Mapped[list["Report"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=True)
