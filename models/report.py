# ruff: noqa
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base


class Report(BaseModel, Base):
    """Report Class"""
    __tablename__ = "reports"

    project_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(nullable=False, index=True)
    summary: Mapped[dict] = mapped_column(JSON, nullable=True)
    visualizations: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_report: Mapped[str] = mapped_column(nullable=True)
    analysis_group: Mapped[str] = mapped_column(nullable=False)

    project: Mapped["Project"] = relationship(
        back_populates="reports")
