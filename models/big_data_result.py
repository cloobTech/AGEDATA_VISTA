# ruff: noqa
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base


class BigDataResult(BaseModel, Base):
    """BigDataResult Class"""
    __tablename__ = "big_data_results"

    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    data_summary: Mapped[dict] = mapped_column(JSON, nullable=True)
    data_visualizations: Mapped[dict] = mapped_column(JSON, nullable=True)
    analysis_results: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_insights: Mapped[str] = mapped_column(nullable=True)


    user: Mapped["User"] = relationship(
        back_populates="big_data_results")