"""
Add wallet_addresses table, investor_wallet_address to investments, and last_processed_block to projects
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import uuid

# revision identifiers, used by Alembic.
revision = 'add_wallet_address_and_sync_fields'
down_revision = 'b2bfb3bf5c82'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Create wallet_addresses table if not exists
    if 'wallet_addresses' not in inspector.get_table_names():
        op.create_table(
            'wallet_addresses',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('address', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )
        # Unique index on address
        try:
            op.create_unique_constraint('uq_wallet_addresses_address', 'wallet_addresses', ['address'])
        except Exception:
            pass

    # Add investor_wallet_address to investments
    inv_cols = [c['name'] for c in inspector.get_columns('investments')] if 'investments' in inspector.get_table_names() else []
    if 'investments' in inspector.get_table_names() and 'investor_wallet_address' not in inv_cols:
        op.add_column('investments', sa.Column('investor_wallet_address', sa.String(), nullable=True))

    # Add last_processed_block to projects
    proj_cols = [c['name'] for c in inspector.get_columns('projects')] if 'projects' in inspector.get_table_names() else []
    if 'projects' in inspector.get_table_names() and 'last_processed_block' not in proj_cols:
        op.add_column('projects', sa.Column('last_processed_block', sa.BigInteger(), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Drop last_processed_block from projects
    if 'projects' in inspector.get_table_names():
        proj_cols = [c['name'] for c in inspector.get_columns('projects')]
        if 'last_processed_block' in proj_cols:
            op.drop_column('projects', 'last_processed_block')

    # Drop investor_wallet_address from investments
    if 'investments' in inspector.get_table_names():
        inv_cols = [c['name'] for c in inspector.get_columns('investments')]
        if 'investor_wallet_address' in inv_cols:
            op.drop_column('investments', 'investor_wallet_address')

    # Drop wallet_addresses table
    if 'wallet_addresses' in inspector.get_table_names():
        try:
            op.drop_constraint('uq_wallet_addresses_address', 'wallet_addresses', type_='unique')
        except Exception:
            pass
        op.drop_table('wallet_addresses') 