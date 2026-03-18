"""add additional performance indexes

Revision ID: a1b2c3d4e5f7
Revises: f5a6b7c8d9e0
Create Date: 2026-03-18 14:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f7"
down_revision = "f5a6b7c8d9e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Добавляем дополнительные индексы для оптимизации производительности:
    - lessons.course_id + order - для сортировки уроков в курсе
    - course_enrollments composite - для получения прогресса пользователя
    - payments composite - для истории платежей пользователя
    - sessions scheduled_at - для поиска сессий по времени
    """

    # Lessons course order index - для получения уроков курса с сортировкой
    op.create_index(
        op.f("ix_lessons_course_order"),
        "lessons",
        ["course_id", "order"],
        if_not_exists=True
    )

    # Course enrollments user progress index - для получения прогресса пользователя по курсам
    op.create_index(
        op.f("ix_course_enrollments_user_progress"),
        "course_enrollments",
        ["user_id", "completed"],
        if_not_exists=True
    )

    # Payments user history index - для получения истории платежей пользователя
    op.create_index(
        op.f("ix_payments_user_created"),
        "payments",
        ["student_id", sa.desc("created_at")],
        if_not_exists=True
    )

    # Sessions scheduled time index - для поиска сессий по времени
    op.create_index(
        op.f("ix_sessions_scheduled_at"),
        "sessions",
        ["scheduled_at"],
        if_not_exists=True
    )

    # Messages created_at index - для сортировки сообщений по времени
    op.create_index(
        op.f("ix_messages_created_at_desc"),
        "messages",
        [sa.desc("created_at")],
        if_not_exists=True
    )

    # Reviews course rating index - для подсчета рейтинга курса
    op.create_index(
        op.f("ix_reviews_course_rating"),
        "reviews",
        ["course_id", "rating"],
        if_not_exists=True
    )


def downgrade() -> None:
    """Удаляем дополнительные индексы"""

    op.drop_index(op.f("ix_reviews_course_rating"), table_name="reviews", if_exists=True)
    op.drop_index(op.f("ix_messages_created_at_desc"), table_name="messages", if_exists=True)
    op.drop_index(op.f("ix_sessions_scheduled_at"), table_name="sessions", if_exists=True)
    op.drop_index(op.f("ix_payments_user_created"), table_name="payments", if_exists=True)
    op.drop_index(op.f("ix_course_enrollments_user_progress"), table_name="course_enrollments", if_exists=True)
    op.drop_index(op.f("ix_lessons_course_order"), table_name="lessons", if_exists=True)
