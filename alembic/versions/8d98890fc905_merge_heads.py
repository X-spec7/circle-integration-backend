"""merge heads

Revision ID: 8d98890fc905
Revises: add_payment_flags_investor_wallet
Create Date: 2025-10-08 21:53:48.441146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d98890fc905'
down_revision = ('add_payment_flags_investor_wallet', 'fec2410c5474')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 