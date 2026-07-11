"""add_subscriptions_table

Revision ID: a1b2c3d4e5f8
Revises: z999_merge_all_heads
Create Date: 2026-03-22

"""
import sqlalchemy as sa
from sqlalchemy import Enum as SAEnum

from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f8'
down_revision = 'z999_merge_all_heads'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    subscription_status = SAEnum(
        'trial', 'active', 'past_due', 'cancelled', 'expired',
        name='subscriptionstatus',
        create_type=True
    )

    subscription_tier = SAEnum(
        'free', 'basic', 'pro', 'premium',
        name='subscriptiontier',
        create_type=True
    )

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
        sa.Column('tier', subscription_tier, nullable=False, default='free'),
        sa.Column('status', subscription_status, nullable=False, default='free'),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('default_payment_method', sa.String(length=255), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )

    # Create indexes
    op.create_index('idx_subscription_user_id', 'subscriptions', ['user_id'])
    op.create_index('idx_subscription_stripe_customer', 'subscriptions', ['stripe_customer_id'])
    op.create_index('idx_subscription_stripe_subscription', 'subscriptions', ['stripe_subscription_id'])
    op.create_index('idx_subscription_status', 'subscriptions', ['status'])
    op.create_index('idx_subscription_tier', 'subscriptions', ['tier'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_subscription_tier', table_name='subscriptions')
    op.drop_index('idx_subscription_status', table_name='subscriptions')
    op.drop_index('idx_subscription_stripe_subscription', table_name='subscriptions')
    op.drop_index('idx_subscription_stripe_customer', table_name='subscriptions')
    op.drop_index('idx_subscription_user_id', table_name='subscriptions')

    # Drop table
    op.drop_table('subscriptions')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
    op.execute('DROP TYPE IF EXISTS subscriptiontier')
