"""seed_default_subscription_plans

Revision ID: 2f776f957be2
Revises: e98be0d1a6c5
Create Date: 2026-03-14 22:50:30.916968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f776f957be2'
down_revision: Union[str, None] = 'e98be0d1a6c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed default subscription plans if the table is empty."""
    import uuid
    from datetime import datetime, timezone

    bind = op.get_bind()

    # Only seed if the table is empty
    count = bind.execute(sa.text("SELECT COUNT(*) FROM subscription_plans")).scalar()
    if count and count > 0:
        return  # Already seeded — skip

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")

    plans = [
        {
            "id": str(uuid.uuid4()),
            "name": "trial",
            "price": 0.0,
            "duration_days": 36500,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pro",
            "price": 19.99,
            "duration_days": 30,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Enterprise",
            "price": 99.99,
            "duration_days": 30,
            "created_at": now,
            "updated_at": now,
        },
    ]

    subscription_plans_table = sa.table(
        "subscription_plans",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("price", sa.Float),
        sa.column("duration_days", sa.Integer),
        sa.column("created_at", sa.String),
        sa.column("updated_at", sa.String),
    )

    op.bulk_insert(subscription_plans_table, plans)


def downgrade() -> None:
    """Remove the seeded default plans by name."""
    op.execute(
        sa.text(
            "DELETE FROM subscription_plans WHERE name IN ('trial', 'Pro', 'Enterprise')"
        )
    )
