"""
Fix payments columns after merge: add flags, investor wallet, rename escrow tx hash to ieo tx hash, drop stripe column

Revision ID: fix_payments_columns_post_merge
Revises: 8d98890fc905
Create Date: 2025-10-08
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_payments_columns_post_merge'
down_revision = '8d98890fc905'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'payments' not in inspector.get_table_names():
        return
    columns = [c['name'] for c in inspector.get_columns('payments')]

    if 'crypto_payout_succeeded' not in columns:
        op.add_column('payments', sa.Column('crypto_payout_succeeded', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'investment_recorded' not in columns:
        op.add_column('payments', sa.Column('investment_recorded', sa.Boolean(), nullable=False, server_default=sa.false()))
    if 'investor_wallet_address' not in columns:
        op.add_column('payments', sa.Column('investor_wallet_address', sa.String(), nullable=True))

    # Rename escrow_transaction_hash -> ieo_transaction_hash if needed
    # Some Postgres backends need explicit copy; we do add new then drop old for idempotency.
    if 'escrow_transaction_hash' in columns and 'ieo_transaction_hash' not in columns:
        op.add_column('payments', sa.Column('ieo_transaction_hash', sa.String(), nullable=True))
        op.drop_column('payments', 'escrow_transaction_hash')

    # Drop stripe_payment_intent_id if exists
    if 'stripe_payment_intent_id' in columns:
        op.drop_column('payments', 'stripe_payment_intent_id')


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'payments' not in inspector.get_table_names():
        return
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

