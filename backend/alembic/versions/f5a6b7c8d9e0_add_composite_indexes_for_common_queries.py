"""add composite indexes for common queries

Revision ID: f5a6b7c8d9e0
Revises: e4f5g6h7i8j9
Create Date: 2026-03-08 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f5a6b7c8d9e0"
down_revision = "e4f5g6h7i8j9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Создаем составные индексы для оптимизации частых запросов:
    - Поиск менторов по специализации + доступности + рейтингу
    - Поиск курсов по категории + активности + рейтингу
    - Сессии по студенту + статусу
    - Сессии по ментору + времени
    """

    # Mentors search index - для поиска менторов по специализации и доступности
    op.create_index(
        op.f("ix_mentors_search"),
        "mentors",
        ["specialization", "is_available", "rating"],
        if_not_exists=True
    )

    # Courses category search index - для поиска курсов по категории
    op.create_index(
        op.f("ix_courses_category_search"),
        "courses",
        ["category", "is_active", "rating"],
        if_not_exists=True
    )

    # Sessions student status index - для получения сессий студента по статусу
    op.create_index(
        op.f("ix_sessions_student_status"),
        "sessions",
        ["student_id", "status"],
        if_not_exists=True
    )

    # Sessions mentor time index - для получения сессий ментора по времени
    op.create_index(
        op.f("ix_sessions_mentor_start_time"),
        "sessions",
        ["mentor_id", sa.desc("start_time")],
        if_not_exists=True
    )

    # Users role active index - для получения активных пользователей по роли
    op.create_index(
        op.f("ix_users_role_active"),
        "users",
        ["role", "is_active"],
        if_not_exists=True
    )

    # Notifications user unread index - для получения непрочитанных уведомлений
    op.create_index(
        op.f("ix_notifications_user_unread"),
        "notifications",
        ["user_id", "is_read"],
        if_not_exists=True
    )


def downgrade() -> None:
    """Удаляем составные индексы"""

    op.drop_index(op.f("ix_notifications_user_unread"), table_name="notifications", if_exists=True)
    op.drop_index(op.f("ix_users_role_active"), table_name="users", if_exists=True)
    op.drop_index(op.f("ix_sessions_mentor_start_time"), table_name="sessions", if_exists=True)
    op.drop_index(op.f("ix_sessions_student_status"), table_name="sessions", if_exists=True)
    op.drop_index(op.f("ix_courses_category_search"), table_name="courses", if_exists=True)
    op.drop_index(op.f("ix_mentors_search"), table_name="mentors", if_exists=True)
