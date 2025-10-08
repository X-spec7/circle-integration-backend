"""
add payment flags and investor wallet address for fiat flow

Revision ID: add_payment_flags_investor_wallet
Revises: 
Create Date: 2025-10-08
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_payment_flags_investor_wallet'
down_revision = 'fec2410c5474'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('payments')]

    if 'crypto_payout_succeeded' not in columns:
        op.add_column('payments', sa.Column('crypto_payout_succeeded', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'investment_recorded' not in columns:
        op.add_column('payments', sa.Column('investment_recorded', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'investor_wallet_address' not in columns:
        op.add_column('payments', sa.Column('investor_wallet_address', sa.String(), nullable=True))

    # Rename escrow_transaction_hash -> ieo_transaction_hash
    if 'escrow_transaction_hash' in columns and 'ieo_transaction_hash' not in columns:
        op.add_column('payments', sa.Column('ieo_transaction_hash', sa.String(), nullable=True))
        # backfill is not needed; keep old data if needed in app layer
        op.drop_column('payments', 'escrow_transaction_hash')

    # Drop stripe_payment_intent_id if exists
    if 'stripe_payment_intent_id' in columns:
        op.drop_column('payments', 'stripe_payment_intent_id')


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('payments')]

    if 'crypto_payout_succeeded' in columns:
        op.drop_column('payments', 'crypto_payout_succeeded')
    if 'investment_recorded' in columns:
        op.drop_column('payments', 'investment_recorded')
    if 'investor_wallet_address' in columns:
        op.drop_column('payments', 'investor_wallet_address')

    if 'ieo_transaction_hash' in columns:
        op.add_column('payments', sa.Column('escrow_transaction_hash', sa.String(), nullable=True))
        op.drop_column('payments', 'ieo_transaction_hash')


