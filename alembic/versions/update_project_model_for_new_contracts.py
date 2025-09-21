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
    # Remove old fields
    op.drop_column('projects', 'target_amount')
    op.drop_column('projects', 'price_per_token')
    op.drop_column('projects', 'total_supply')
    op.drop_column('projects', 'escrow_contract_address')
    op.drop_column('projects', 'escrow_deployment_tx')
    
    # Add new fields
    op.add_column('projects', sa.Column('initial_supply', sa.BigInteger(), nullable=False, server_default='1000000'))
    op.add_column('projects', sa.Column('delay_days', sa.Integer(), nullable=False, server_default='7'))
    op.add_column('projects', sa.Column('min_investment', sa.Integer(), nullable=False, server_default='100'))
    op.add_column('projects', sa.Column('max_investment', sa.Integer(), nullable=False, server_default='1000000'))


def downgrade():
    # Add back old fields
    op.add_column('projects', sa.Column('target_amount', sa.Numeric(15, 2), nullable=True))
    op.add_column('projects', sa.Column('price_per_token', sa.Numeric(10, 4), nullable=True))
    op.add_column('projects', sa.Column('total_supply', sa.BigInteger(), nullable=True))
    op.add_column('projects', sa.Column('escrow_contract_address', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('escrow_deployment_tx', sa.String(), nullable=True))
    
    # Remove new fields
    op.drop_column('projects', 'max_investment')
    op.drop_column('projects', 'min_investment')
    op.drop_column('projects', 'delay_days')
    op.drop_column('projects', 'initial_supply')
