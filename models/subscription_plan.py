# ruff: noqa
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base


class Plan(BaseModel, Base):
    """Subscription Plan Class"""
    __tablename__ = "subscription_plans"

    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    price: Mapped[float] = mapped_column(nullable=False)
    duration_days: Mapped[int] = mapped_column(nullable=False, default=30)

    subscriptions: Mapped["Subscription"] = relationship(
        back_populates="subscription_plan")
