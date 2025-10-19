"""kyc

Revision ID: 89e71e461c36
Revises: 4c7f85d4d191
Create Date: 2025-10-19 17:34:25.874096

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '89e71e461c36'
down_revision = '4c7f85d4d191'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ensure enum exists (idempotent)
    op.execute("""
    DO $$ BEGIN
        CREATE TYPE kycstatus AS ENUM ('not_started', 'review', 'verified', 'declined');
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;
    """)

    # create KYC tables if they don't exist
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = set(inspector.get_table_names())

    if 'kyc_clients' not in existing_tables:
        op.create_table(
            'kyc_clients',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('complycube_client_id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('client_type', sa.String(), nullable=False),
            sa.Column('entity_name', sa.String(), nullable=True),
            sa.Column('email', sa.String(), nullable=True),
            sa.Column('status', postgresql.ENUM('not_started', 'review', 'verified', 'declined', name='kycstatus', create_type=False), nullable=True),
            sa.Column('status_text', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('complycube_client_id')
        )

    if 'kyc_personal_details' not in existing_tables:
        op.create_table(
            'kyc_personal_details',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('kyc_client_id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('first_name', sa.String(), nullable=True),
            sa.Column('last_name', sa.String(), nullable=True),
            sa.Column('middle_name', sa.String(), nullable=True),
            sa.Column('date_of_birth', sa.String(), nullable=True),
            sa.Column('nationality', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['kyc_client_id'], ['kyc_clients.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

    if 'kyc_company_details' not in existing_tables:
        op.create_table(
            'kyc_company_details',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('kyc_client_id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('company_name', sa.String(), nullable=True),
            sa.Column('registration_number', sa.String(), nullable=True),
            sa.Column('incorporation_date', sa.String(), nullable=True),
            sa.Column('business_type', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['kyc_client_id'], ['kyc_clients.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )

    if 'kyc_documents' not in existing_tables:
        op.create_table(
            'kyc_documents',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('kyc_client_id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('document_type', sa.String(), nullable=True),
            sa.Column('document_number', sa.String(), nullable=True),
            sa.Column('complycube_document_id', sa.String(), nullable=True),
            sa.Column('status', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['kyc_client_id'], ['kyc_clients.id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    op.drop_table('kyc_documents')
    op.drop_table('kyc_company_details')
    op.drop_table('kyc_personal_details')
    op.drop_table('kyc_clients')
    op.execute("DROP TYPE IF EXISTS kycstatus;")