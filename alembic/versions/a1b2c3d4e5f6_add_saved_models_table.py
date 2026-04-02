"""add saved_models table

Revision ID: a1b2c3d4e5f6
Revises: c8b89403ffc1
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'c8b89403ffc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the saved_models table."""
    op.create_table(
        'saved_models',
        sa.Column('user_id',       sa.String(length=60), nullable=False),
        sa.Column('project_id',    sa.String(length=60), nullable=False),
        sa.Column('storage_path',  sa.String(length=512), nullable=False),
        sa.Column('analysis_type', sa.String(length=60), nullable=False),
        sa.Column('task_type',     sa.String(length=30), nullable=False),
        sa.Column('feature_cols',  sa.JSON(), nullable=False),
        sa.Column('label',         sa.String(length=255), nullable=True),
        sa.Column('id',            sa.String(length=60), nullable=False),
        sa.Column('created_at',    sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at',    sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'],    ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_saved_models_user_id',       'saved_models', ['user_id'])
    op.create_index('ix_saved_models_project_id',    'saved_models', ['project_id'])
    op.create_index('ix_saved_models_analysis_type', 'saved_models', ['analysis_type'])


def downgrade() -> None:
    """Drop the saved_models table."""
    op.drop_index('ix_saved_models_analysis_type', table_name='saved_models')
    op.drop_index('ix_saved_models_project_id',    table_name='saved_models')
    op.drop_index('ix_saved_models_user_id',       table_name='saved_models')
    op.drop_table('saved_models')
