"""create_user_table

Revision ID: 00_02_00
Revises: 00_01_00
Create Date: 2025-11-19 18:14:55.871644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision: str = '00_02_00'
down_revision: Union[str, None] = '00_01_00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('google_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('picture_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('last_login_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('google_id'),
        sa.UniqueConstraint('email')
    )

    op.create_index('idx_user_google_id', 'users', ['google_id'])
    op.create_index('idx_user_email', 'users', ['email'])


def downgrade() -> None:
    op.drop_index('idx_user_email', table_name='users')
    op.drop_index('idx_user_google_id', table_name='users')
    op.drop_table('users')
