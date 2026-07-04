"""
FastAPI Dependencies
Shared dependencies for routes: authentication, database, pagination, etc.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Generator, Optional

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

import jwt

from app.config import settings
from app.database import SessionLocal
from app.models import User
from app.models.user import UserRole
from app.schemas import PaginationParams

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


# ==================== DATABASE DEPENDENCY ====================


def get_db() -> Generator[Session, None, None]:
    """Get database session with proper error handling."""
    db = SessionLocal()
    try:
        yield db
        # Don't auto-commit here - let endpoints manage their own commits
        # This prevents double-commit issues
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        raise
    finally:
        db.close()


# ==================== AUTHENTICATION DEPENDENCIES ====================


class TokenPayload:
    """Token payload model"""

    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> TokenPayload:
    """Verify JWT token and return token payload"""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience="mentorhub",
            issuer="mentorhub-api",
            options={"require": ["aud", "iss", "exp"]},
        )

        sub_value = payload.get("sub")
        if sub_value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing sub",
            )

        user_id: int = int(sub_value)
        email: str = payload.get("email")
        role: str = payload.get("role")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing email",
            )

        return TokenPayload(user_id=user_id, email=email, role=role or "student")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired") from None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token") from e


def get_current_user(
    token: TokenPayload = Depends(verify_token),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == token.user_id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin role"""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")
    return current_user


def get_current_mentor(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify mentor role"""
    if current_user.role not in (UserRole.MENTOR, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only mentors can access this resource")

    if not current_user.mentor_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not have a mentor profile")

    return current_user


def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify student role"""
    if current_user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can access this resource")
    return current_user


# ==================== OPTIONAL AUTHENTICATION ====================


def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None

    try:
        token_payload = verify_token(credentials)
        user = db.query(User).filter(User.id == token_payload.user_id).first()
        return user if user and user.is_active else None
    except HTTPException:
        return None


# ==================== PAGINATION DEPENDENCY ====================


def get_pagination(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(
        default=settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Items per page"
    ),
) -> PaginationParams:
    """Get pagination parameters from query params"""
    return PaginationParams(page=page, page_size=page_size)


# ==================== QUERY PARAMETERS DEPENDENCIES ====================


def get_search_query(q: Optional[str] = Query(None, min_length=1, max_length=100)) -> Optional[str]:
    """Get search query parameter"""
    return q


def get_sort_param(
    sort_by: str = Query(default="created_at", pattern="^[a-zA-Z_]+$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> tuple[str, str]:
    """Get sorting parameters"""
    return sort_by, sort_order


def get_filters(
    skip_archived: bool = Query(default=True),
    is_active: Optional[bool] = Query(default=None),
) -> dict:
    """Get filter parameters"""
    filters = {}
    if skip_archived:
        filters["is_active"] = True
    elif is_active is not None:
        filters["is_active"] = is_active
    return filters


# ==================== RESOURCE OWNERSHIP DEPENDENCIES ====================


def verify_user_ownership(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> bool:
    """Verify that current user owns the resource"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this resource")
    return True


def get_mentor_by_id(mentor_id: int, db: Session = Depends(get_db)):
    """Get mentor by ID and verify exists"""
    from app.models import Mentor

    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    return mentor


def get_session_by_id(session_id: int, db: Session = Depends(get_db)):
    """Get session by ID and verify exists"""
    from app.models import Session as SessionModel

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


def verify_session_access(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> object:
    """Verify that current user has access to session (as mentor, student, or admin)"""
    from app.models import Session as SessionModel

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    is_mentor = session.mentor_id == current_user.id
    is_student = session.student_id == current_user.id
    is_admin = current_user.is_admin

    if not (is_mentor or is_student or is_admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this session")

    return session


# ==================== RATE LIMITING DEPENDENCY ====================


class RateLimiter:
    """Simple in-memory rate limiter with periodic cleanup"""

    def __init__(self, requests: int = 100, period: int = 3600):
        self.requests = requests
        self.period = period
        self.clients = defaultdict(list)
        self._last_cleanup = datetime.now(timezone.utc)

    def _cleanup_stale_clients(self) -> None:
        """Remove clients with no recent requests to prevent memory leaks"""
        now = datetime.now(timezone.utc)
        # Only cleanup every 5 minutes
        if (now - self._last_cleanup).total_seconds() < 300:
            return

        self._last_cleanup = now
        cutoff = now - timedelta(seconds=self.period)
        stale_keys = [
            client_id for client_id, timestamps in self.clients.items()
            if not timestamps or timestamps[-1] <= cutoff
        ]
        for key in stale_keys:
            del self.clients[key]

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=self.period)

        self._cleanup_stale_clients()

        self.clients[client_id] = [req_time for req_time in self.clients[client_id] if req_time > cutoff]

        if len(self.clients[client_id]) >= self.requests:
            return False

        self.clients[client_id].append(now)
        return True


_rate_limiter = (
    RateLimiter(requests=settings.RATE_LIMIT_REQUESTS, period=settings.RATE_LIMIT_PERIOD)
    if settings.RATE_LIMIT_ENABLED
    else None
)

# Webhook rate limiter - более строгие лимиты для webhook endpoints
# Webhook провайдеры обычно отправляют 100-1000 запросов в час
_webhook_rate_limiter = (
    RateLimiter(requests=500, period=3600)  # 500 запросов в час
    if settings.RATE_LIMIT_ENABLED
    else None
)


def rate_limit_dependency(
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> bool:
    """Rate limiting dependency"""
    if not _rate_limiter:
        return True

    client_id = f"user_{current_user.id}" if current_user else "anonymous"

    if not _rate_limiter.is_allowed(client_id):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    return True


def webhook_rate_limit_dependency(request: Request) -> bool:
    """
    Специальный rate limiter для webhook endpoints.
    Использует IP адрес для идентификации, так как webhook'и не имеют авторизации.
    """
    if not _webhook_rate_limiter:
        return True

    # Используем IP адрес + path для более точной идентификации
    client_ip = request.client.host if request.client else "unknown"
    client_id = f"webhook_{client_ip}_{request.url.path}"

    if not _webhook_rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Webhook rate limit exceeded"
        )

    return True
