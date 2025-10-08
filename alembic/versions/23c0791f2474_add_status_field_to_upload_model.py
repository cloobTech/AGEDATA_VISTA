from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '23c0791f2474'
down_revision = '571be0dcf9cf'
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Add the column with a temporary default
    op.add_column(
        'uploaded_files',
        sa.Column('status', sa.String(), nullable=True, server_default='PROCESSING')
    )

    # 2️⃣ Remove the server default so future inserts don't auto-fill unless app sets it
    op.alter_column('uploaded_files', 'status', server_default=None)


def downgrade():
    op.drop_column('uploaded_files', 'status')
