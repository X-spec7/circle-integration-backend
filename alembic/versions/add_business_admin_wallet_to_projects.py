"""Add business admin wallet to projects

Revision ID: add_business_admin_wallet
Revises: update_project_model_new_contracts
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_business_admin_wallet'
down_revision = 'update_project_model_new_contracts'
branch_labels = None
depends_on = None


def upgrade():
    # Add business_admin_wallet column to projects table if missing
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]
    if 'business_admin_wallet' not in columns:
        op.add_column('projects', sa.Column('business_admin_wallet', sa.String(), nullable=True))


def downgrade():
    # Remove business_admin_wallet column if present
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('projects')]
    if 'business_admin_wallet' in columns:
        op.drop_column('projects', 'business_admin_wallet')
