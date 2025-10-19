"""document_signing

Revision ID: e7f0d6ad8665
Revises: 89e71e461c36
Create Date: 2025-10-19 19:12:32.079202

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7f0d6ad8665'
down_revision = '89e71e461c36'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum for document signing status (idempotent)
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE documentsigningstatus AS ENUM ('draft','sent','signed','declined','expired','cancelled');
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
        """
    )

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'document_signings' not in existing_tables:
        op.create_table(
            'document_signings',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('envelope_id', sa.String(), nullable=False),
            sa.Column('document_name', sa.String(), nullable=False),
            sa.Column('document_path', sa.String(), nullable=True),
            sa.Column('document_type', sa.String(), nullable=False),
            sa.Column('status', postgresql.ENUM('draft','sent','signed','declined','expired','cancelled', name='documentsigningstatus', create_type=False), nullable=True),
            sa.Column('signing_service', sa.String(length=50), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('project_id', sa.String(), nullable=True),
            sa.Column('investment_id', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('envelope_id'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
            sa.ForeignKeyConstraint(['investment_id'], ['investments.id']),
        )

    if 'document_signers' not in existing_tables:
        op.create_table(
            'document_signers',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('document_signing_id', sa.String(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('role', sa.String(), nullable=True),
            sa.Column('signer_order', sa.Integer(), nullable=True),
            sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['document_signing_id'], ['document_signings.id']),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    op.drop_table('document_signers')
    op.drop_table('document_signings')
    op.execute("DROP TYPE IF EXISTS documentsigningstatus;")