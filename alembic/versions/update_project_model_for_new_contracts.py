"""Update project model for new contracts

Revision ID: update_project_model_new_contracts
Revises: add_ieo_reward_tracking
Create Date: 2024-01-15 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_project_model_new_contracts'
down_revision = 'add_ieo_reward_tracking'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]

    # Remove old fields if they exist
    for col in ['target_amount', 'price_per_token', 'total_supply', 'escrow_contract_address', 'escrow_deployment_tx']:
        if col in columns:
            op.drop_column('projects', col)

    # Recompute columns after drops
    columns = [c['name'] for c in inspector.get_columns('projects')]

    # Add new fields if missing
    if 'initial_supply' not in columns:
        op.add_column('projects', sa.Column('initial_supply', sa.BigInteger(), nullable=False, server_default='1000000'))
    if 'delay_days' not in columns:
        op.add_column('projects', sa.Column('delay_days', sa.Integer(), nullable=False, server_default='7'))
    if 'min_investment' not in columns:
        op.add_column('projects', sa.Column('min_investment', sa.Integer(), nullable=False, server_default='100'))
    if 'max_investment' not in columns:
        op.add_column('projects', sa.Column('max_investment', sa.Integer(), nullable=False, server_default='1000000'))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]

    # Add back old fields if missing
    if 'target_amount' not in columns:
        op.add_column('projects', sa.Column('target_amount', sa.Numeric(15, 2), nullable=True))
    if 'price_per_token' not in columns:
        op.add_column('projects', sa.Column('price_per_token', sa.Numeric(10, 4), nullable=True))
    if 'total_supply' not in columns:
        op.add_column('projects', sa.Column('total_supply', sa.BigInteger(), nullable=True))
    if 'escrow_contract_address' not in columns:
        op.add_column('projects', sa.Column('escrow_contract_address', sa.String(), nullable=True))
    if 'escrow_deployment_tx' not in columns:
        op.add_column('projects', sa.Column('escrow_deployment_tx', sa.String(), nullable=True))

    # Remove new fields if present
    for col in ['max_investment', 'min_investment', 'delay_days', 'initial_supply']:
        if col in columns:
            op.drop_column('projects', col)
