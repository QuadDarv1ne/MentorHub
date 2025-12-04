"""add performance indexes on frequently used columns

Revision ID: e4f5g6h7i8j9
Revises: 4a3b2c1d5e6f
Create Date: 2025-12-04 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4f5g6h7i8j9"
down_revision = "4a3b2c1d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Создаем индексы для оптимизации производительности часто используемых запросов:
    - users.email - для быстрого поиска по email при авторизации
    - sessions.status - для фильтрации активных сессий
    - sessions.created_at DESC - для сортировки по дате
    - mentor_sessions.user_id - для получения сессий пользователя
    - payments.status - для фильтрации платежей по статусу
    - courses.is_active - для получения активных курсов
    """
    
    # Users email index - для быстрого поиска при авторизации
    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
        if_not_exists=True
    )
    
    # Sessions status index - для фильтрации активных/завершенных сессий
    op.create_index(
        op.f("ix_sessions_status"),
        "sessions",
        ["status"],
        if_not_exists=True
    )
    
    # Sessions created_at index - для сортировки по дате
    op.create_index(
        op.f("ix_sessions_created_at_desc"),
        "sessions",
        [sa.desc("created_at")],
        if_not_exists=True
    )
    
    # Mentor sessions user_id index - для получения сессий конкретного пользователя
    op.create_index(
        op.f("ix_mentor_sessions_user_id"),
        "mentor_sessions",
        ["user_id"],
        if_not_exists=True
    )
    
    # Mentor sessions mentor_id index - для получения сессий конкретного ментора
    op.create_index(
        op.f("ix_mentor_sessions_mentor_id"),
        "mentor_sessions",
        ["mentor_id"],
        if_not_exists=True
    )
    
    # Payments status index - для фильтрации платежей по статусу
    op.create_index(
        op.f("ix_payments_status"),
        "payments",
        ["status"],
        if_not_exists=True
    )
    
    # Payments user_id index - для получения платежей пользователя
    op.create_index(
        op.f("ix_payments_user_id"),
        "payments",
        ["user_id"],
        if_not_exists=True
    )
    
    # Courses is_active index - для получения активных курсов
    op.create_index(
        op.f("ix_courses_is_active"),
        "courses",
        ["is_active"],
        if_not_exists=True
    )
    
    # Courses instructor_id index - для получения курсов ментора
    op.create_index(
        op.f("ix_courses_instructor_id"),
        "courses",
        ["instructor_id"],
        if_not_exists=True
    )
    
    # Course enrollments user_id index - для получения курсов пользователя
    op.create_index(
        op.f("ix_course_enrollments_user_id"),
        "course_enrollments",
        ["user_id"],
        if_not_exists=True
    )
    
    # Course enrollments course_id index - для получения студентов курса
    op.create_index(
        op.f("ix_course_enrollments_course_id"),
        "course_enrollments",
        ["course_id"],
        if_not_exists=True
    )
    
    # Mentor users user_id index - для связи ментора с пользователем
    op.create_index(
        op.f("ix_mentors_user_id"),
        "mentors",
        ["user_id"],
        unique=True,
        if_not_exists=True
    )


def downgrade() -> None:
    """Удаляем все созданные индексы"""
    
    op.drop_index(op.f("ix_mentors_user_id"), table_name="mentors", if_exists=True)
    op.drop_index(op.f("ix_course_enrollments_course_id"), table_name="course_enrollments", if_exists=True)
    op.drop_index(op.f("ix_course_enrollments_user_id"), table_name="course_enrollments", if_exists=True)
    op.drop_index(op.f("ix_courses_instructor_id"), table_name="courses", if_exists=True)
    op.drop_index(op.f("ix_courses_is_active"), table_name="courses", if_exists=True)
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments", if_exists=True)
    op.drop_index(op.f("ix_payments_status"), table_name="payments", if_exists=True)
    op.drop_index(op.f("ix_mentor_sessions_mentor_id"), table_name="mentor_sessions", if_exists=True)
    op.drop_index(op.f("ix_mentor_sessions_user_id"), table_name="mentor_sessions", if_exists=True)
    op.drop_index(op.f("ix_sessions_created_at_desc"), table_name="sessions", if_exists=True)
    op.drop_index(op.f("ix_sessions_status"), table_name="sessions", if_exists=True)
    op.drop_index(op.f("ix_users_email"), table_name="users", if_exists=True)
