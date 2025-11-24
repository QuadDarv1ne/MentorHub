"""
MentorHub Backend - Main Entry Point
FastAPI application initialization and configuration
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

from app.config import settings, is_production
from app.database import engine, Base, SessionLocal
from app.api import auth, users, mentors, sessions, messages, payments, courses, reviews, progress, stats
from app.middleware.security_advanced import SecurityMiddleware


# ==================== LOGGING SETUP ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== SENTRY SETUP ====================
if SENTRY_AVAILABLE and settings.SENTRY_DSN and is_production():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )
    logger.info("✅ Sentry initialized")
elif settings.SENTRY_DSN and not SENTRY_AVAILABLE:
    logger.warning("⚠️ Sentry DSN настроен, но sentry-sdk не установлен")


# ==================== DATABASE STARTUP/SHUTDOWN ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    Manages database connections and other resources
    """
    # STARTUP
    logger.info("🚀 Starting MentorHub API...")
    logger.info(f"📊 Database URL: {settings.DATABASE_URL[:50]}...")
    
    # Create tables (with retry logic for Amvera)
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            import time
            if attempt > 0:
                logger.info(f"⏳ Retrying database connection (attempt {attempt + 1}/{max_retries})...")
                time.sleep(retry_delay)
            
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created/verified")
            break
        except Exception as e:
            logger.error(f"❌ Error creating database tables (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                logger.error("❌ Failed to connect to database after all retries")
                # Don't raise in production, let app start anyway
                if not is_production():
                    raise
    
    # Log startup info
    logger.info(f"📊 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔒 Debug mode: {settings.DEBUG}")
    logger.info(f"🌍 CORS origins: {settings.CORS_ORIGINS}")
    
    yield  # Application runs here
    
    # SHUTDOWN
    logger.info("🛑 Shutting down MentorHub API...")
    logger.info("✅ MentorHub API shutdown complete")


# ==================== CREATE FASTAPI APP ====================
app = FastAPI(
    title=settings.APP_NAME,
    description="Open-source IT mentorship platform API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if not is_production() else None,
    redoc_url="/redoc" if not is_production() else None,
    openapi_url="/openapi.json" if not is_production() else None,
)


# ==================== MIDDLEWARE SETUP ====================

# Advanced Security Middleware (SQL injection, XSS, CSRF, etc.)
app.add_middleware(SecurityMiddleware)
logger.info("✅ Advanced Security middleware added")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)
logger.info("✅ CORS middleware added")

# Trusted Host Middleware (for production)
if is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )
    logger.info("✅ Trusted Host middleware added")

# GZIP Middleware for compression
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)
logger.info("✅ GZIP middleware added")


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Validation error",
            "errors": exc.errors(),
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if is_production():
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error",
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(exc),
                "detail": str(exc),
            },
        )


# ==================== REQUEST/RESPONSE LOGGING ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    
    # Skip logging for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    logger.info(f"📨 {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.info(f"📤 {response.status_code} {request.method} {request.url.path}")
    
    return response


# ==================== ROUTES SETUP ====================

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not is_production() else None,
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        db_status = "disconnected"
        # Check database connection
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
        
        return {
            "status": "healthy" if db_status == "connected" else "degraded",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": db_status,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": "Service unavailable",
                "database": "disconnected",
            },
        )


# Ready check endpoint (Kubernetes)
@app.get("/ready", tags=["Health"])
async def ready_check():
    """Readiness check for Kubernetes"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {"ready": True}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"ready": False},
        )


# Detailed health check endpoint
@app.get("/api/v1/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with all system metrics"""
    try:
        from app.utils.health import get_full_health_check
        health_data = await get_full_health_check()
        
        if health_data["status"] == "healthy":
            return health_data
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_data,
            )
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "error": str(e)
            },
        )


# ==================== API ROUTES ====================
api_prefix = "/api/v1"

# Auth routes
app.include_router(
    auth.router,
    prefix=f"{api_prefix}/auth",
    tags=["Authentication"],
)
logger.info("✅ Auth routes loaded")

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
    prefix=f"{api_prefix}",
    tags=["Reviews"],
)
logger.info("✅ Review routes loaded")


app.include_router(
    progress.router,
    prefix=f"{api_prefix}",
    tags=["Progress"],
)
logger.info("✅ Progress routes loaded")

# Stats routes
app.include_router(
    stats.router,
    prefix=f"{api_prefix}",
    tags=["Statistics"],
)
logger.info("✅ Stats routes loaded")


# ==================== STARTUP EVENTS ====================

# Note: Using lifespan context manager instead of deprecated @app.on_event
# Startup/shutdown logic is handled in the lifespan() function above


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app=app,
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
