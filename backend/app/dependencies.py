"""
FastAPI Dependencies
Shared dependencies for routes: authentication, database, pagination, etc.
"""

import logging
from typing import Generator, Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
try:
    import jwt
except ImportError:
    # Fallback для PyJWT
    try:
        import jwt as PyJWT_jwt
        jwt = PyJWT_jwt
    except ImportError:
        raise ImportError("Необходимо установить PyJWT: pip install PyJWT")

from app.config import settings
from app.database import SessionLocal
from app.models import User
from app.schemas import PaginationParams


logger = logging.getLogger(__name__)
security = HTTPBearer()


# ==================== DATABASE DEPENDENCY ====================

def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    Dependency for all routes that need database access
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
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


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenPayload:
    """
    Verify JWT token and return token payload
    
    Usage:
        @app.get("/protected")
        def protected_route(token: TokenPayload = Depends(verify_token)):
            ...
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # sub может быть строкой или числом, преобразуем в int
        sub_value = payload.get("sub")
        if sub_value is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing sub",
            )
        
        user_id: int = int(sub_value)  # Преобразуем в int
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing email",
            )
        
        return TokenPayload(user_id=user_id, email=email, role=role or "student")
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )


def get_current_user(
    token: TokenPayload = Depends(verify_token),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user
    Combines token verification with database lookup
    
    Usage:
        @app.get("/me")
        def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    """
    user = db.query(User).filter(User.id == token.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify admin role
    
    Usage:
        @app.delete("/users/{user_id}")
        def delete_user(user_id: int, admin: User = Depends(get_current_admin)):
            ...
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this resource",
        )
    
    return current_user


def get_current_mentor(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify mentor role
    
    Usage:
        @app.post("/mentors/courses")
        def create_course(mentor: User = Depends(get_current_mentor)):
            ...
    """
    if current_user.role.value not in ["mentor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mentors can access this resource",
        )
    
    if not current_user.mentor_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a mentor profile",
        )
    
    return current_user


def get_current_student(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify student role
    
    Usage:
        @app.post("/courses/{course_id}/enroll")
        def enroll_course(course_id: int, student: User = Depends(get_current_student)):
            ...
    """
    if current_user.role.value not in ["student", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this resource",
        )
    
    return current_user


# ==================== OPTIONAL AUTHENTICATION ====================

async def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    Useful for endpoints that work with or without authentication
    
    Usage:
        @app.get("/courses")
        def get_courses(current_user: Optional[User] = Depends(get_current_user_optional)):
            if current_user:
                # Show user-specific data
            else:
                # Show public data
    """
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
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Items per page"
    ),
) -> PaginationParams:
    """
    Get pagination parameters from query params
    
    Usage:
        @app.get("/users")
        def get_users(
            pagination: PaginationParams = Depends(get_pagination),
            db: Session = Depends(get_db)
        ):
            users = db.query(User).offset(pagination.skip).limit(pagination.limit).all()
            return {"total": total, "data": users}
    """
    return PaginationParams(page=page, page_size=page_size)


# ==================== QUERY PARAMETERS DEPENDENCIES ====================

def get_search_query(q: Optional[str] = Query(None, min_length=1, max_length=100)) -> Optional[str]:
    """Get search query parameter"""
    return q


def get_sort_param(
    sort_by: str = Query(default="created_at", regex="^[a-zA-Z_]+$"),
    sort_order: str = Query(default="desc", regex="^(asc|desc)$"),
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
    """
    Verify that current user owns the resource
    
    Usage:
        @app.put("/users/{user_id}")
        def update_user(
            user_id: int,
            is_owner: bool = Depends(verify_user_ownership),
            db: Session = Depends(get_db)
        ):
            ...
    """
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource",
        )
    
    return True


def get_mentor_by_id(
    mentor_id: int,
    db: Session = Depends(get_db),
):
    """Get mentor by ID and verify exists"""
    from app.models import Mentor
    
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    
    if not mentor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor not found",
        )
    
    return mentor


def get_session_by_id(
    session_id: int,
    db: Session = Depends(get_db),
):
    """Get session by ID and verify exists"""
    from app.models import Session as SessionModel
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    return session


def verify_session_access(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verify that current user has access to session
    Either as mentor or student
    """
    from app.models import Session as SessionModel
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    is_mentor = session.mentor_id == current_user.id
    is_student = session.student_id == current_user.id
    is_admin = current_user.role.value == "admin"
    
    if not (is_mentor or is_student or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this session",
        )
    
    return session


# ==================== RATE LIMITING DEPENDENCY ====================

from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests: int = 100, period: int = 3600):
        self.requests = requests
        self.period = period
        self.clients = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period)
        
        # Remove old requests
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self.clients[client_id]) >= self.requests:
            return False
        
        # Add current request
        self.clients[client_id].append(now)
        return True


_rate_limiter = RateLimiter(
    requests=settings.RATE_LIMIT_REQUESTS,
    period=settings.RATE_LIMIT_PERIOD,
) if settings.RATE_LIMIT_ENABLED else None


def rate_limit_dependency(
    current_user: User = Depends(get_current_user),
) -> bool:
    """
    Rate limiting dependency
    
    Usage:
        @app.get("/expensive-operation")
        def expensive_op(limited: bool = Depends(rate_limit_dependency)):
            ...
    """
    if not _rate_limiter:
        return True
    
    client_id = f"user_{current_user.id}"
    
    if not _rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum requests per hour exceeded.",
        )
    
    return True
