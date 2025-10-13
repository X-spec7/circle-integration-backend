"""add notifications

Revision ID: 4c7f85d4d191
Revises: c392754b05ed
Create Date: 2025-10-13 17:12:21.229873

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4c7f85d4d191'
down_revision = 'c392754b05ed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user notification preference (default true)
    op.add_column('users', sa.Column('notifications_enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False))

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.VARCHAR(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.VARCHAR(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.VARCHAR(), nullable=False),
        sa.Column('message', sa.TEXT(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.Column('read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('read_at', sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])


def downgrade() -> None:
    # Drop notifications table and user column
    op.drop_index('ix_notifications_user_id', table_name='notifications')
    op.drop_table('notifications')
    op.drop_column('users', 'notifications_enabled')