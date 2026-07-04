"""
Database Configuration Module
SQLAlchemy setup and session management
"""

import logging
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

logger = logging.getLogger(__name__)


# ==================== DATABASE ENGINE SETUP ====================

# Use SQLAlchemy 2.0 DeclarativeBase
class Base(DeclarativeBase):
    pass


def _create_engine_for_testing():
    """Create engine for testing environment with NullPool"""
    return create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},
    )


def _create_engine_for_sqlite():
    """Create engine for SQLite with QueuePool"""
    return create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},
    )


def _create_engine_for_postgresql():
    """Create engine for PostgreSQL with PgBouncer connection pooling support"""
    # PgBouncer is used in Docker production environment
    # The DATABASE_URL should already point to pgbouncer:6432 in production
    db_url = settings.DATABASE_URL

    # Detect if using PgBouncer based on host or port
    is_pgbouncer = "pgbouncer" in db_url.lower() or ":6432" in db_url

    if is_pgbouncer:
        # PgBouncer transaction pooling mode - use smaller pool
        # PgBouncer handles connection multiplexing
        logger.info("🔄 PgBouncer detected - using optimized pool settings")
        return create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,  # 5 in production with PgBouncer
            max_overflow=settings.DB_MAX_OVERFLOW,  # 10 in production with PgBouncer
            pool_pre_ping=True,  # Health check before using connection
            pool_recycle=settings.DB_POOL_RECYCLE,  # 30 minutes
            pool_timeout=settings.DB_POOL_TIMEOUT,  # 30 seconds
            echo=settings.DB_ECHO,
            connect_args={
                "connect_timeout": settings.DB_CONNECT_TIMEOUT,
                "application_name": "mentorhub",
                "options": "-c statement_timeout=30000",  # 30s statement timeout
            },
        )
    else:
        # Direct PostgreSQL connection (development/testing)
        # Use larger pool since no connection multiplexer
        logger.info("📡 Direct PostgreSQL connection - using standard pool settings")
        return create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=20,  # Larger pool for direct connections
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            echo=settings.DB_ECHO,
            connect_args={
                "connect_timeout": 10,
                "application_name": "mentorhub",
                "options": "-c statement_timeout=30000",
            },
        )


# Create engine based on environment
if settings.ENVIRONMENT == "testing":
    engine = _create_engine_for_testing()
    logger.info("🧪 Testing database engine created")
elif "sqlite" in settings.DATABASE_URL.lower():
    engine = _create_engine_for_sqlite()
    logger.info("📱 SQLite database engine created")
else:
    engine = _create_engine_for_postgresql()
    pgbouncer_enabled = getattr(settings, "PGBOUNCER_ENABLED", False)
    logger.info(
        f"🗄️ Production database engine created "
        f"(pool_size={settings.DB_POOL_SIZE}, max_overflow={settings.DB_MAX_OVERFLOW}, pgbouncer={pgbouncer_enabled})"
    )


# ==================== CONNECTION POOL LISTENERS ====================


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for optimization"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


@event.listens_for(Engine, "connect")
def log_connect(dbapi_conn, connection_record):
    """Log database connections in debug mode"""
    if settings.DEBUG:
        logger.debug("📡 Database connection established")


@event.listens_for(Engine, "checkout")
def log_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout from pool in debug mode"""
    if settings.DEBUG:
        logger.debug("📡 Database connection acquired from pool")


@event.listens_for(Engine, "checkin")
def log_checkin(dbapi_conn, connection_record):
    """Log connection checkin to pool in debug mode"""
    if settings.DEBUG:
        logger.debug("📡 Database connection returned to pool")


# ==================== SESSION FACTORY ====================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

logger.info("✅ SessionLocal factory created")


# ==================== BASE MODEL ====================
# Base is already defined at the top of the file
logger.info("✅ SQLAlchemy Base created")


# ==================== DATABASE UTILITIES ====================


class Database:
    """Database utility class"""

    @staticmethod
    def create_all_tables():
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ All database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating tables: {e}")
            raise

    @staticmethod
    def drop_all_tables():
        """Drop all tables from the database (WARNING: Destructive!)"""
        try:
            Base.metadata.drop_all(bind=engine)
            logger.warning("⚠️ All database tables dropped!")
        except Exception as e:
            logger.error(f"❌ Error dropping tables: {e}")
            raise

    @staticmethod
    def get_session() -> Session:
        """Get a new database session"""
        return SessionLocal()

    @staticmethod
    def check_connection() -> bool:
        """Check if database connection is working"""
        from sqlalchemy import text

        session = None
        try:
            session = SessionLocal()
            session.execute(text("SELECT :value"), {"value": 1})
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
        finally:
            if session:
                session.close()

    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information (credentials masked)"""
        from urllib.parse import urlparse
        parsed = urlparse(settings.DATABASE_URL)
        masked_url = f"{parsed.scheme}://***:***@{parsed.hostname}:{parsed.port}{parsed.path}"
        return {
            "url": masked_url,
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_pre_ping": True,
            "echo": settings.DB_ECHO,
        }


# ==================== INITIALIZATION ====================


def init_db():
    """Initialize database (create tables, apply migrations, etc.)"""
    logger.info("🔧 Initializing database...")

    # Check connection
    if not Database.check_connection():
        raise RuntimeError("Cannot connect to database")

    # Create tables
    Database.create_all_tables()

    logger.info("✅ Database initialization complete")


def close_db():
    """Close database connections"""
    logger.info("🔌 Closing database connections...")
    try:
        engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# ==================== CONTEXT MANAGERS ====================

@contextmanager
def get_db_context():
    """
    Context manager for database session

    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


@contextmanager
def transactional():
    """
    Context manager for transactional operations

    Usage:
        with transactional() as db:
            db.add(new_user)
            db.add(new_mentor)
            # Auto commit on success, auto rollback on exception
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Transaction rolled back: {e}")
        raise
    finally:
        db.close()


# ==================== EXPORT ====================

__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "Database",
    "init_db",
    "close_db",
    "get_db_context",
    "transactional",
]
