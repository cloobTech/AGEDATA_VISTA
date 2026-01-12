from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from models.base_model import BaseModel, Base


class UploadedFile(BaseModel, Base):
    __tablename__ = "uploaded_files"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id"), nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    size: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    extension: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=True, default="PROCESSING")
    public_id: Mapped[str] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(
        back_populates="files", uselist=False)
    projects: Mapped["Project"] = relationship(
        back_populates="files", uselist=True)
