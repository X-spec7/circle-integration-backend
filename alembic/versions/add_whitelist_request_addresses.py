"""Add whitelist_request_addresses table with per-address rows and unique constraint

Revision ID: add_whitelist_request_addresses
Revises: b2bfb3bf5c82
Create Date: 2025-10-01 08:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
import uuid

# revision identifiers, used by Alembic.
revision = 'add_whitelist_request_addresses'
down_revision = 'b2bfb3bf5c82'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Create table if not exists
    if 'whitelist_request_addresses' not in inspector.get_table_names():
        op.create_table(
            'whitelist_request_addresses',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('request_id', sa.String(), sa.ForeignKey('whitelist_requests.id', ondelete='CASCADE'), nullable=False),
            sa.Column('project_id', sa.String(), sa.ForeignKey('projects.id'), nullable=False),
            sa.Column('investor_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('address', sa.String(), nullable=False),
            sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='whitelistrequeststatus'), nullable=False, server_default='pending'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )
        # Partial unique index for pending requests per (project_id, address)
        try:
            op.create_index(
                'uq_pending_project_address',
                'whitelist_request_addresses',
                ['project_id', 'address'],
                unique=True,
                postgresql_where=sa.text("status = 'pending'")
            )
        except Exception:
            # Fallback to full unique if partial not supported
            op.create_unique_constraint(
                'uq_project_address',
                'whitelist_request_addresses',
                ['project_id', 'address']
            )

    # Backfill from existing whitelist_requests
    if 'whitelist_requests' in inspector.get_table_names():
        rows = conn.execute(text("SELECT id, project_id, investor_id, addresses, status, created_at FROM whitelist_requests")).fetchall()
        for r in rows:
            addresses = (r.addresses or '').split(',') if r.addresses else []
            for addr in [a.strip() for a in addresses if a.strip()]:
                conn.execute(text(
                    """
                    INSERT INTO whitelist_request_addresses (id, request_id, project_id, investor_id, address, status, created_at)
                    VALUES (:id, :request_id, :project_id, :investor_id, :address, :status, :created_at)
                    ON CONFLICT DO NOTHING
                    """
                ), {
                    'id': str(uuid.uuid4()),
                    'request_id': r.id,
                    'project_id': r.project_id,
                    'investor_id': r.investor_id,
                    'address': addr,
                    'status': r.status,
                    'created_at': r.created_at,
                })


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'whitelist_request_addresses' in inspector.get_table_names():
        try:
            op.drop_index('uq_pending_project_address', table_name='whitelist_request_addresses')
        except Exception:
            try:
                op.drop_constraint('uq_project_address', 'whitelist_request_addresses', type_='unique')
            except Exception:
                pass
        op.drop_table('whitelist_request_addresses') 