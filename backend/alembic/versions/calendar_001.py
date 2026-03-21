"""create calendar integration tables

Revision ID: calendar_001
Revises: video_calls_001
Create Date: 2026-03-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'calendar_001'
down_revision = 'video_calls_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create calendar_syncs table
    op.create_table(
        'calendar_syncs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.Enum('google', 'outlook', name='calendarprovider'), nullable=False),
        sa.Column('access_token', sa.String(length=2048), nullable=False),
        sa.Column('refresh_token', sa.String(length=2048), nullable=True),
        sa.Column('token_expiry', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calendar_id', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_past_days', sa.Integer(), nullable=False, default=30),
        sa.Column('sync_future_days', sa.Integer(), nullable=False, default=90),
        sa.Column('auto_sync', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendar_syncs_user_id'), 'calendar_syncs', ['user_id'], unique=True)
    op.create_index(op.f('ix_calendar_syncs_is_active'), 'calendar_syncs', ['is_active'], unique=False)
    op.create_index(op.f('ix_calendar_syncs_created_at'), 'calendar_syncs', ['created_at'], unique=False)

    # Create calendar_events table
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.Enum('google', 'outlook', name='calendarprovider'), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=512), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_all_day', sa.Boolean(), nullable=False, default=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('is_synced', sa.Boolean(), nullable=False, default=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('video_call_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
        sa.ForeignKeyConstraint(['video_call_id'], ['video_calls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendar_events_user_id'), 'calendar_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_external_id'), 'calendar_events', ['external_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_start_time'), 'calendar_events', ['start_time'], unique=False)
    op.create_index(op.f('ix_calendar_events_created_at'), 'calendar_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_calendar_events_session_id'), 'calendar_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_video_call_id'), 'calendar_events', ['video_call_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_calendar_events_video_call_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_session_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_created_at'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_start_time'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_external_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_user_id'), table_name='calendar_events')
    op.drop_table('calendar_events')
    
    op.drop_index(op.f('ix_calendar_syncs_created_at'), table_name='calendar_syncs')
    op.drop_index(op.f('ix_calendar_syncs_is_active'), table_name='calendar_syncs')
    op.drop_index(op.f('ix_calendar_syncs_user_id'), table_name='calendar_syncs')
    op.drop_table('calendar_syncs')
    
    # Drop enum
    op.execute('DROP TYPE IF EXISTS calendarprovider')
