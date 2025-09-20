from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base_model import BaseModel, Base
import enum


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Subscription(BaseModel, Base):
    """Subscription Class"""
    __tablename__ = "subscriptions"

    user_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("users.id"), nullable=False
    )
    plan_id: Mapped[str] = mapped_column(
        String(60), ForeignKey("subscription_plans.id"), nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(nullable=False, default="active")
    payment_info: Mapped[dict] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    subscription_plan: Mapped["Plan"] = relationship(
        back_populates="subscriptions", lazy="selectin")

    __table_args__ = (
        Index(
            "uq_user_active_subscription",
            "user_id",
            unique=True,
            postgresql_where=(status == "active"),
        ),
    )
