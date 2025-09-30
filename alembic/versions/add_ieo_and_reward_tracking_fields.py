"""Add IEO and RewardTracking contract fields to projects

Revision ID: add_ieo_reward_tracking
Revises: 62af17569fbd
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ieo_reward_tracking'
down_revision = '62af17569fbd'
branch_labels = None
depends_on = None


def upgrade():
    # Add new contract address fields (guard if already present)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]

    if 'ieo_contract_address' not in columns:
        op.add_column('projects', sa.Column('ieo_contract_address', sa.String(), nullable=True))
    if 'reward_tracking_contract_address' not in columns:
        op.add_column('projects', sa.Column('reward_tracking_contract_address', sa.String(), nullable=True))
    
    # Add new deployment transaction hash fields
    if 'ieo_deployment_tx' not in columns:
        op.add_column('projects', sa.Column('ieo_deployment_tx', sa.String(), nullable=True))
    if 'reward_tracking_deployment_tx' not in columns:
        op.add_column('projects', sa.Column('reward_tracking_deployment_tx', sa.String(), nullable=True))


def downgrade():
    # Remove the added columns (drop if exist)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]

    if 'reward_tracking_deployment_tx' in columns:
        op.drop_column('projects', 'reward_tracking_deployment_tx')
    if 'ieo_deployment_tx' in columns:
        op.drop_column('projects', 'ieo_deployment_tx')
    if 'reward_tracking_contract_address' in columns:
        op.drop_column('projects', 'reward_tracking_contract_address')
    if 'ieo_contract_address' in columns:
        op.drop_column('projects', 'ieo_contract_address')
