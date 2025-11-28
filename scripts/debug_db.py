#!/usr/bin/env python3
"""
Debug database connection issues
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set environment variables for proper encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def debug_database_config():
    """Debug database configuration"""
    try:
        from app.config import settings
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        logger.info(f"Database URL type: {type(settings.DATABASE_URL)}")
        logger.info(f"Database URL repr: {repr(settings.DATABASE_URL)}")
        
        # Try to create engine
        from sqlalchemy import create_engine
        logger.info("Creating engine...")
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=None,  # Use default pool
            echo=True,
            connect_args={
                "check_same_thread": False,
            } if "sqlite" in settings.DATABASE_URL.lower() else {}
        )
        logger.info("Engine created successfully")
        
        # Try to connect
        logger.info("Testing connection...")
        with engine.connect() as conn:
            logger.info("Connection successful!")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database_config()