"""
API роуты
Обработчики маршрутов FastAPI
"""

import logging

from fastapi import FastAPI

from app.api import (
    achievements,
    admin,
    analytics,
    auth,
    backups,
    calendar,
    chat_rooms,
    courses,
    email_verification,
    export,
    health,
    mentors,
    messages,
    monitoring,
    notifications,
    payments,
    progress,
    push_notifications,
    reviews,
    sessions,
    stats,
    subscriptions,
    two_factor,
    users,
    video_calls,
    websocket,
)
logger = logging.getLogger(__name__)


def register_routes(app: FastAPI) -> None:
    """
    Register all API routes for the application.

    Args:
        app: FastAPI application instance
    """
    api_prefix = "/api/v1"
    logger.info("📍 Registering API routes...")

    # Health routes
    app.include_router(
        health.router,
        prefix=api_prefix,
    )
    logger.info("✅ Health routes loaded")

    # Auth routes
    app.include_router(
        auth.router,
        prefix=f"{api_prefix}/auth",
        tags=["Authentication"],
    )
    logger.info("✅ Auth routes loaded")

    # Email verification routes
    app.include_router(
        email_verification.router,
        prefix=f"{api_prefix}/email",
        tags=["Email Verification"],
    )
    logger.info("✅ Email verification routes loaded")

    # User routes
    app.include_router(
        users.router,
        prefix=f"{api_prefix}/users",
        tags=["Users"],
    )
    logger.info("✅ User routes loaded")

    # Mentor routes
    app.include_router(
        mentors.router,
        prefix=f"{api_prefix}/mentors",
        tags=["Mentors"],
    )
    logger.info("✅ Mentor routes loaded")

    # Session routes
    app.include_router(
        sessions.router,
        prefix=f"{api_prefix}/sessions",
        tags=["Sessions"],
    )
    logger.info("✅ Session routes loaded")

    # Message routes
    app.include_router(
        messages.router,
        prefix=f"{api_prefix}/messages",
        tags=["Messages"],
    )
    logger.info("✅ Message routes loaded")

    # Payment routes
    app.include_router(
        payments.router,
        prefix=f"{api_prefix}/payments",
        tags=["Payments"],
    )
    logger.info("✅ Payment routes loaded")

    # Course routes
    app.include_router(
        courses.router,
        prefix=f"{api_prefix}/courses",
        tags=["Courses"],
    )
    logger.info("✅ Course routes loaded")

    # Review routes
    app.include_router(
        reviews.router,
        prefix=api_prefix,
        tags=["Reviews"],
    )
    logger.info("✅ Review routes loaded")

    # Progress routes
    app.include_router(
        progress.router,
        prefix=api_prefix,
        tags=["Progress"],
    )
    logger.info("✅ Progress routes loaded")

    # Stats routes
    app.include_router(
        stats.router,
        prefix=api_prefix,
        tags=["Statistics"],
    )
    logger.info("✅ Stats routes loaded")

    # Achievement routes
    app.include_router(
        achievements.router,
        prefix=f"{api_prefix}/achievements",
        tags=["Achievements"],
    )
    logger.info("✅ Achievement routes loaded")

    # Monitoring routes
    app.include_router(
        monitoring.router,
        prefix=f"{api_prefix}/admin",
        tags=["Monitoring"],
    )
    logger.info("✅ Monitoring routes loaded")

    # Backup routes
    app.include_router(
        backups.router,
        prefix=f"{api_prefix}/admin",
        tags=["Backups"],
    )
    logger.info("✅ Backup routes loaded")

    # WebSocket routes
    app.include_router(
        websocket.router,
        tags=["WebSocket"],
    )
    logger.info("✅ WebSocket routes loaded")

    # Notification routes
    app.include_router(
        notifications.router,
        prefix=api_prefix,
        tags=["Notifications"],
    )
    logger.info("✅ Notification routes loaded")

    # Analytics routes
    app.include_router(
        analytics.router,
        prefix=api_prefix,
        tags=["Analytics"],
    )
    logger.info("✅ Analytics routes loaded")

    # Push notifications routes
    app.include_router(
        push_notifications.router,
        prefix=api_prefix,
        tags=["Push Notifications"],
    )
    logger.info("✅ Push notifications routes loaded")

    # Two-Factor Authentication routes
    app.include_router(
        two_factor.router,
        prefix=api_prefix,
        tags=["Two-Factor Authentication"],
    )
    logger.info("✅ Two-Factor Authentication routes loaded")

    # Data Export routes (GDPR compliance)
    app.include_router(
        export.router,
        prefix=api_prefix,
        tags=["Data Export"],
    )
    logger.info("✅ Data Export routes loaded")

    # Chat Rooms routes
    app.include_router(
        chat_rooms.router,
        prefix=api_prefix,
        tags=["Chat Rooms"],
    )
    logger.info("✅ Chat Rooms routes loaded")

    # Video Calls routes
    app.include_router(
        video_calls.router,
        prefix=f"{api_prefix}/video-calls",
        tags=["Video Calls"],
    )
    logger.info("✅ Video Calls routes loaded")

    # Calendar Integration routes
    app.include_router(
        calendar.router,
        prefix=api_prefix,
        tags=["Calendar Integration"],
    )
    logger.info("✅ Calendar Integration routes loaded")

    # Subscription routes
    app.include_router(
        subscriptions.router,
        prefix=api_prefix,
        tags=["Subscriptions"],
    )
    logger.info("✅ Subscription routes loaded")

    # Admin routes (admin panel API)
    app.include_router(
        admin.router,
        prefix=f"{api_prefix}/admin",
        tags=["Admin"],
    )
    logger.info("✅ Admin routes loaded")

    logger.info("✅ All API routes registered successfully")
