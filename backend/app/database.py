"""
Database Configuration Module
SQLAlchemy setup and session management
"""

import logging
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool

from app.config import settings

logger = logging.getLogger(__name__)


# ==================== DATABASE ENGINE SETUP ====================

# Create engine based on environment
if settings.ENVIRONMENT == "testing":
    # Use NullPool for testing (no connection pooling)
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=settings.DB_ECHO,
        connect_args={"check_same_thread": False},  # For SQLite in tests
    )
    logger.info("🧪 Testing database engine created")
else:
    # Use QueuePool for production/development
    # Handle different database types
    if "sqlite" in settings.DATABASE_URL.lower():
        # SQLite-specific configuration
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            echo=settings.DB_ECHO,
            connect_args={
                "check_same_thread": False,
            }
        )
    else:
        # PostgreSQL/other database configuration
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_pre_ping=True,
            echo=settings.DB_ECHO,
            connect_args={
                "connect_timeout": 10,
                "application_name": "mentorhub",
            }
        )
    logger.info(
        f"🗄️ Production database engine created "
        f"(pool_size={settings.DB_POOL_SIZE}, max_overflow={settings.DB_MAX_OVERFLOW})"
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

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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
        try:
            from sqlalchemy import text
            session = SessionLocal()
            session.execute(text("SELECT 1"))
            session.close()
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information"""
        return {
            "url": settings.DATABASE_URL,
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

from contextlib import contextmanager

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
        logger.debug("✅ Transaction committed")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Transaction rolled back: {e}")
        raise
    finally:
        db.close()


# ==================== DEPENDENCY INJECTION ====================

def get_db():
    """
    FastAPI dependency for getting database session
    
    Usage in routes:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
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
    "get_db",
]