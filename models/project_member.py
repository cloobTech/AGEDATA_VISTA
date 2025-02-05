from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base_model import BaseModel, Base


class ProjectMember(BaseModel, Base):
    """ Project Member Class """
    __tablename__ = "project_members"

    project_id: Mapped[str] = mapped_column(
        ForeignKey('projects.id'), nullable=False)
    user_id: Mapped[str] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    # admin, viewer, editor and member
    role: Mapped[str] = mapped_column(nullable=False, default="editor")

    project: Mapped["Project"] = relationship(
        back_populates="members", uselist=False)
    user: Mapped["User"] = relationship(
        back_populates="projects", uselist=False)
