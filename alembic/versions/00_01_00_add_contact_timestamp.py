"""add contact timestamp

Revision ID: 00_01_00
Revises: 00_00_00
Create Date: 2025-11-02 09:07:23.287148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00_01_00'
down_revision: Union[str, None] = '00_00_00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'contact',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )


def downgrade() -> None:
    op.drop_column('contact', 'created_at')
