"""add oauth fields to user model

Revision ID: a1b2c3d4e5f6
Revises: f5a6b7c8d9e0
Create Date: 2026-03-10 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f5a6b7c8d9e0'
branch_labels = None
depends_on = None


def upgrade():
    # Add OAuth columns to users table
    op.add_column('users', sa.Column('oauth_provider', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(length=255), nullable=True))
    
    # Make hashed_password nullable for OAuth users
    op.alter_column('users', 'hashed_password',
               existing_type=sa.String(length=255),
               nullable=True)
    
    # Set is_verified to True for existing users (they can be migrated)
    op.execute("UPDATE users SET is_verified = TRUE WHERE is_verified = FALSE")
    
    # Create index for OAuth lookups
    op.create_index('ix_users_oauth', 'users', ['oauth_provider', 'oauth_id'])


def downgrade():
    # Drop index
    op.drop_index('ix_users_oauth', table_name='users')
    
    # Remove OAuth columns
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
    
    # Make hashed_password NOT NULL again
    op.alter_column('users', 'hashed_password',
               existing_type=sa.String(length=255),
               nullable=False)
