"""create_guessr_table

Revision ID: 00_03_00
Revises: 00_02_00
Create Date: 2025-12-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '00_03_00'
down_revision: Union[str, None] = '00_02_00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'guessr',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('puzzle_number', sa.Integer(), nullable=False),
        sa.Column('puzzle_type', sa.String(), nullable=False),
        sa.Column('answer', sa.Integer(), nullable=False),
        sa.Column('config', JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', 'puzzle_number', name='uq_guessr_date_puzzle_number')
    )

    op.create_index('idx_guessr_date', 'guessr', ['date'])


def downgrade() -> None:
    op.drop_index('idx_guessr_date', table_name='guessr')
    op.drop_table('guessr')
