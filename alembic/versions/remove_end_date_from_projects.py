"""Remove end_date column from projects table

Revision ID: remove_end_date
Revises: add_business_admin_wallet
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_end_date'
down_revision = 'add_business_admin_wallet'
branch_labels = None
depends_on = None


def upgrade():
    """Remove end_date column from projects table"""
    # Remove the end_date column
    op.drop_column('projects', 'end_date')


def downgrade():
    """Add end_date column back to projects table"""
    # Add the end_date column back
    op.add_column('projects', sa.Column('end_date', sa.DateTime(), nullable=True))
