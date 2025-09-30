"""rename is_verified to kyc_verified on users

Revision ID: 6464672634e8
Revises: 6464672634e7
Create Date: 2025-09-30 06:40:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6464672634e8'
down_revision = '6464672634e7'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Rename users.is_verified -> users.kyc_verified if the old column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'kyc_verified' not in columns and 'is_verified' in columns:
        op.alter_column('users', 'is_verified', new_column_name='kyc_verified', existing_type=sa.Boolean())

    # Create whitelist_requests table if it doesn't exist yet (idempotent)
    if 'whitelist_requests' not in inspector.get_table_names():
        op.create_table(
            'whitelist_requests',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id'), nullable=False),
            sa.Column('investor_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('addresses', sa.Text(), nullable=False),
            sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='whitelistrequeststatus'), nullable=False, server_default='pending'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )

def downgrade() -> None:
    # Best-effort: rename back if present
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('users')]
    if 'is_verified' not in columns and 'kyc_verified' in columns:
        op.alter_column('users', 'kyc_verified', new_column_name='is_verified', existing_type=sa.Boolean())

    # Drop whitelist_requests table if exists
    if 'whitelist_requests' in inspector.get_table_names():
        op.drop_table('whitelist_requests') 