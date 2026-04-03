"""set status not null for upload folder

Revision ID: 6b93038c4967
Revises: 23c0791f2474
Create Date: 2025-10-05 18:41:16.425019

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b93038c4967'
down_revision: Union[str, None] = '23c0791f2474'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: status column was already added in 23c0791f2474."""
    pass


def downgrade() -> None:
    """No-op: column managed by 23c0791f2474."""
    pass
