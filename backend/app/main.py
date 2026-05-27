"""
MentorHub Backend - Main Entry Point

FastAPI application initialization and configuration.
This module orchestrates all components: lifespan, middleware, routes, and error handlers.
"""

import logging
import os
import socket
from typing import List, Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

# ==================== LOGGING SETUP ====================
from pythonjsonlogger import jsonlogger

from app.api import register_routes
from app.config import is_production, settings
from app.lifespan import get_shutdown_event, initialize_redis_client, lifespan
from app.middleware.setup import register_middleware
from app.utils.error_handlers import register_error_handlers
from app.utils.prometheus import metrics_endpoint

if settings.LOG_FORMAT == "json":
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    log_handler.setFormatter(formatter)
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        handlers=[log_handler],
    )
else:
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
logger = logging.getLogger(__name__)


# ==================== AUTO PORT DETECTION ====================
def is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """Check if port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_free_port(
    start_port: int = 8000,
    max_attempts: int = 100,
    host: str = "0.0.0.0",
    exclude_ports: Optional[List[int]] = None
) -> int:
    """Find first available port starting from start_port."""
    exclude_ports = exclude_ports or []
    for port in range(start_port, start_port + max_attempts):
        if port in exclude_ports or not is_port_available(port, host):
            continue
        return port
    raise RuntimeError(f"Failed to find free port in range {start_port}-{start_port + max_attempts}")


def resolve_port(preferred_port: int = 8000) -> int:
    """Resolve port for server startup."""
    exclude_ports = [3000, 12600, 19001, 19005, 19006, 6060, 6061, 81]
    env_port = os.environ.get("PORT")
    if env_port:
        preferred_port = int(env_port)
    if is_port_available(preferred_port):
        logger.info(f"✅ Port {preferred_port} is available")
        return preferred_port
    logger.warning(f"⚠️ Port {preferred_port} is busy, searching for free port...")
    free_port = find_free_port(preferred_port + 1, exclude_ports=exclude_ports)
    logger.info(f"✅ Found free port: {free_port}")
    return free_port


# ==================== CREATE FASTAPI APP ====================
app = FastAPI(
    title=settings.APP_NAME,
    description="Open-source IT mentorship platform API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ==================== INITIALIZE COMPONENTS ====================

# Initialize Redis client
redis_client = initialize_redis_client()

# Register middleware
register_middleware(app, redis_client)

# Register error handlers
register_error_handlers(app)

# Register API routes
register_routes(app)


# ==================== ENDPOINTS ====================

@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe for Kubernetes/Docker."""
    if get_shutdown_event().is_set():
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "shutting_down", "message": "Service is shutting down"}
        )
    return {"status": "ready"}


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """Liveness probe for Kubernetes/Docker."""
    return {"status": "alive"}


@app.get("/api", tags=["API Info"])
async def api_info():
    """API Information and documentation."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Open-source IT mentorship platform API",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "features": [
            "User Management", "Mentor System", "Sessions", "Messaging",
            "Payments", "Courses", "Reviews", "Progress Tracking",
            "Achievements", "Notifications"
        ]
    }


@app.get("/", tags=["Root"])
@app.head("/", tags=["Root"], include_in_schema=False)
async def root():
    """Welcome endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not is_production() else None,
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return empty favicon to prevent 404 errors."""
    return Response(status_code=204)


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint."""
    return await metrics_endpoint()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    if request.url.path in ["/health", "/health/ready", "/health/live", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    logger.info(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 {response.status_code} {request.method} {request.url.path}")
    return response


# ==================== OPENAPI CONFIGURATION ====================

def setup_openapi_schema():
    """Configure OpenAPI schema with security schemes."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token: **test_token** will be used in test environment"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for service-to-service communication"
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


setup_openapi_schema()
logger.info("✅ OpenAPI schema configured with security schemes")


# ==================== RUN APPLICATION ====================

if __name__ == "__main__":
    import uvicorn

    preferred_port = getattr(settings, 'PORT', 8000)
    port = resolve_port(preferred_port)
    host = getattr(settings, 'HOST', '0.0.0.0')

    logger.info(f"🎯 Starting server on {host}:{port}")
    os.environ["SERVER_PORT"] = str(port)

    uvicorn.run(
        app=app,
        host=host,
        port=port,
        reload=getattr(settings, 'RELOAD', False),
        log_level=getattr(settings, 'LOG_LEVEL', 'INFO').lower(),
        access_log=True,
        timeout_graceful_shutdown=30,
    )
