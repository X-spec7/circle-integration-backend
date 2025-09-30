"""merge heads

Revision ID: b2bfb3bf5c82
Revises: 6464672634e8, remove_end_date
Create Date: 2025-09-30 07:47:32.647203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2bfb3bf5c82'
down_revision = ('6464672634e8', 'remove_end_date')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 