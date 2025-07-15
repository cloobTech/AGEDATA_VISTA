"""Add role column to project_invitations

Revision ID: 34ab56789cde
Revises: 12fc259627ad
Create Date: 2025-07-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34ab56789cde'
down_revision: Union[str, None] = '12fc259627ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add role column to project_invitations."""

    # 1️⃣ Add column, allow NULL at first for old rows
    op.add_column('project_invitations',
        sa.Column('role', sa.String(), nullable=True)
    )

    # 2️⃣ Backfill old rows with a safe default
    op.execute(
        "UPDATE project_invitations SET role = 'viewer' WHERE role IS NULL"
    )

    # 3️⃣ Set column to NOT NULL
    op.alter_column(
        'project_invitations',
        'role',
        existing_type=sa.String(),
        nullable=False
    )


def downgrade() -> None:
    """Remove role column from project_invitations."""

    op.drop_column('project_invitations', 'role')
