"""Add security constraints and performance indexes

Revision ID: a1b2c3d4e5f9
Revises: a1b2c3d4e5f8
Create Date: 2026-04-04 12:00:00.000000

Improvements:
- Add unique constraints to prevent race conditions
- Add cascade delete for dependent entities
- Rename notification.type to notification_type (reserved word)
- Add foreign key indexes for performance
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f9'
down_revision = 'a1b2c3d4e5f8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add constraints and indexes for security and performance"""

    # 1. Add unique constraint to reviews (prevent duplicate reviews)
    op.create_unique_constraint(
        'uq_review_user_course',
        'reviews',
        ['user_id', 'course_id']
    )

    # 2. Add unique constraint to course_enrollments (prevent duplicate enrollments)
    op.create_unique_constraint(
        'uq_enrollment_user_course',
        'course_enrollments',
        ['user_id', 'course_id']
    )

    # 3. Rename notification.type to notification_type (reserved word fix)
    # For PostgreSQL:
    op.alter_column('notifications', 'type', new_column_name='notification_type', existing_type=sa.Enum())

    # 4. Add CASCADE delete to notification.user_id foreign key
    # Drop old FK and create new one with ondelete='CASCADE'
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
    op.create_foreign_key(
        'notifications_user_id_fkey',
        'notifications', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # 5. Add missing indexes for performance (if they don't exist)
    # These are safe to add - they'll be skipped if already exist
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'], if_not_exists=True)
    op.create_index('ix_reviews_user_id', 'reviews', ['user_id'], if_not_exists=True)
    op.create_index('ix_reviews_course_id', 'reviews', ['course_id'], if_not_exists=True)
    op.create_index('ix_progress_user_id', 'progress', ['user_id'], if_not_exists=True)
    op.create_index('ix_progress_course_id', 'progress', ['course_id'], if_not_exists=True)
    op.create_index('ix_progress_lesson_id', 'progress', ['lesson_id'], if_not_exists=True)


def downgrade() -> None:
    """Revert constraints and indexes"""

    # Remove indexes
    op.drop_index('ix_progress_lesson_id', 'progress')
    op.drop_index('ix_progress_course_id', 'progress')
    op.drop_index('ix_progress_user_id', 'progress')
    op.drop_index('ix_reviews_course_id', 'reviews')
    op.drop_index('ix_reviews_user_id', 'reviews')
    op.drop_index('ix_notifications_user_id', 'notifications')

    # Revert FK to non-CASCADE
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
    op.create_foreign_key(
        'notifications_user_id_fkey',
        'notifications', 'users',
        ['user_id'], ['id']
    )

    # Rename column back
    op.alter_column('notifications', 'notification_type', new_column_name='type', existing_type=sa.Enum())

    # Remove unique constraints
    op.drop_constraint('uq_enrollment_user_course', 'course_enrollments', type_='unique')
    op.drop_constraint('uq_review_user_course', 'reviews', type_='unique')
