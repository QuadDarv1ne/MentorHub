"""Merge all heads into single head

Revision ID: z999_merge_all_heads
Revises: 313e11c98a64, a1b2c3d4e5f7, b2c3d4e5f6g7, d123456789ab
Create Date: 2026-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'z999_merge_all_heads'
down_revision = ('313e11c98a64', 'a1b2c3d4e5f7', 'b2c3d4e5f6g7', 'd123456789ab')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
