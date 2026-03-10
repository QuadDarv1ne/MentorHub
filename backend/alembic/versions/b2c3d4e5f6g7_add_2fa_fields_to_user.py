"""add 2FA fields to user model

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-10 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add 2FA columns to users table
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(length=255), nullable=True))
    
    # Create index for 2FA lookups
    op.create_index('ix_users_2fa', 'users', ['two_factor_enabled'])


def downgrade():
    # Drop index
    op.drop_index('ix_users_2fa', table_name='users')
    
    # Remove 2FA columns
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
