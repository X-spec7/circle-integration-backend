"""merge heads for wallet+whitelist addresses

Revision ID: fec2410c5474
Revises: add_wallet_address_and_sync_fields, add_whitelist_request_addresses
Create Date: 2025-10-02 17:39:19.812599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fec2410c5474'
down_revision = ('add_wallet_address_and_sync_fields', 'add_whitelist_request_addresses')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 