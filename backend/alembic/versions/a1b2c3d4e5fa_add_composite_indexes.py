"""Add composite indexes for common query patterns

Revision ID: a1b2c3d4e5fa
Revises: a1b2c3d4e5f9
Create Date: 2026-07-05 00:00:00.000000

Performance:
- Composite index on notifications(user_id, is_read, created_at) for unread list
- Composite index on messages(sender_id, recipient_id, created_at) for conversations
- Composite index on progress(user_id, course_id) for user progress lookup
- Composite index on mentors(is_available, rating) for search/filter
- Composite index on mentors(specialization) for filtering
- Composite index on reviews(reviewed_id, created_at) for mentor reviews
- Composite index on achievements(user_id, earned_at) for user achievements
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5fa'
down_revision = 'a1b2c3d4e5f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Notifications: user_id + is_read + created_at for unread list queries
    op.create_index(
        'idx_notification_user_unread',
        'notifications',
        ['user_id', 'is_read', 'created_at'],
    )

    # Messages: sender_id + recipient_id + created_at for conversation history
    op.create_index(
        'idx_message_conversation',
        'messages',
        ['sender_id', 'recipient_id', 'created_at'],
    )

    # Progress: user_id + course_id for user progress lookup
    op.create_index(
        'idx_progress_user_course',
        'progress',
        ['user_id', 'course_id'],
    )

    # Mentors: is_available + rating for search/filter
    op.create_index(
        'idx_mentor_available_rating',
        'mentors',
        ['is_available', 'rating'],
    )

    # Mentors: specialization for category filtering
    op.create_index(
        'idx_mentor_specialization',
        'mentors',
        ['specialization'],
    )

    # Reviews: reviewed_id + created_at for mentor review list
    op.create_index(
        'idx_review_reviewed_created',
        'reviews',
        ['reviewed_id', 'created_at'],
    )

    # Achievements: user_id + earned_at for user achievements list
    op.create_index(
        'idx_achievement_user_earned',
        'achievements',
        ['user_id', 'earned_at'],
    )


def downgrade() -> None:
    op.drop_index('idx_achievement_user_earned', table_name='achievements')
    op.drop_index('idx_review_reviewed_created', table_name='reviews')
    op.drop_index('idx_mentor_specialization', table_name='mentors')
    op.drop_index('idx_mentor_available_rating', table_name='mentors')
    op.drop_index('idx_progress_user_course', table_name='progress')
    op.drop_index('idx_message_conversation', table_name='messages')
    op.drop_index('idx_notification_user_unread', table_name='notifications')
