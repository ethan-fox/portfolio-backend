"""split_guessr_into_two_tables

Revision ID: 00_04_00
Revises: 00_03_00
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '00_04_00'
down_revision: Union[str, None] = '00_03_00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Drop old guessr table (no data migration)
    op.drop_index('idx_guessr_date', table_name='guessr')
    op.drop_table('guessr')

    # Step 2: Create new guessr table (daily puzzle set)
    op.create_table(
        'guessr',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('date', name='uq_guessr_date')
    )
    op.create_index('ix_guessr_date', 'guessr', ['date'])

    # Step 3: Create new guessr_puzzle table (individual puzzles)
    op.create_table(
        'guessr_puzzle',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('guessr_id', sa.Integer(), nullable=False),
        sa.Column('puzzle_number', sa.Integer(), nullable=False),
        sa.Column('puzzle_type', sa.String(), nullable=False),
        sa.Column('answer', sa.Integer(), nullable=False),
        sa.Column('config', JSONB(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['guessr_id'], ['guessr.id'], name='fk_guessr_puzzle_guessr_id'),
        sa.UniqueConstraint('guessr_id', 'puzzle_number', name='uq_guessr_puzzle_number')
    )
    op.create_index('ix_guessr_puzzle_guessr_id', 'guessr_puzzle', ['guessr_id'])


def downgrade() -> None:
    # Drop new tables
    op.drop_index('ix_guessr_puzzle_guessr_id', table_name='guessr_puzzle')
    op.drop_table('guessr_puzzle')
    op.drop_index('ix_guessr_date', table_name='guessr')
    op.drop_table('guessr')

    # Recreate old single-table design
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
