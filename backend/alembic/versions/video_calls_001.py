"""create video calls tables

Revision ID: video_calls_001
Revises: chat_rooms_001
Create Date: 2026-03-21

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'video_calls_001'
down_revision = 'chat_rooms_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create video_calls table
    op.create_table(
        'video_calls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('call_type', sa.Enum('one_on_one', 'group', name='calltype'), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=True),
        sa.Column('room_id', sa.Integer(), nullable=True),
        sa.Column('agora_channel', sa.String(length=255), nullable=False),
        sa.Column('agora_token', sa.String(length=2048), nullable=True),
        sa.Column('status', sa.Enum('scheduled', 'in_progress', 'completed', 'cancelled', 'missed', name='callstatus'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['participant_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['room_id'], ['chat_rooms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_calls_creator_id'), 'video_calls', ['creator_id'], unique=False)
    op.create_index(op.f('ix_video_calls_participant_id'), 'video_calls', ['participant_id'], unique=False)
    op.create_index(op.f('ix_video_calls_room_id'), 'video_calls', ['room_id'], unique=False)
    op.create_index(op.f('ix_video_calls_agora_channel'), 'video_calls', ['agora_channel'], unique=True)
    op.create_index(op.f('ix_video_calls_status'), 'video_calls', ['status'], unique=False)
    op.create_index(op.f('ix_video_calls_scheduled_at'), 'video_calls', ['scheduled_at'], unique=False)
    op.create_index(op.f('ix_video_calls_created_at'), 'video_calls', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_video_calls_created_at'), table_name='video_calls')
    op.drop_index(op.f('ix_video_calls_scheduled_at'), table_name='video_calls')
    op.drop_index(op.f('ix_video_calls_status'), table_name='video_calls')
    op.drop_index(op.f('ix_video_calls_agora_channel'), table_name='video_calls')
    op.drop_index(op.f('ix_video_calls_room_id'), table_name='video_calls')
    op.drop_index(op.f('ix_video_calls_participant_id'), table_name='video_calls')
    op.drop_index(op.f('ix_video_calls_creator_id'), table_name='video_calls')
    op.drop_table('video_calls')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS callstatus')
    op.execute('DROP TYPE IF EXISTS calltype')
