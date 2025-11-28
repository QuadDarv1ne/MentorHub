#!/usr/bin/env python3
"""
Initialize database with course tables
Creates the necessary tables for courses, lessons, and enrollments
Fixed version with proper encoding handling
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set environment variables for proper encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

def create_course_tables():
    """Create course-related tables in the database"""
    try:
        logger.info("Creating course tables...")
        
        # Import after setting environment variables
        from app.database import Base, engine
        from app.models.course import Course, Lesson, CourseEnrollment
        
        # Create all tables (this will only create tables that don't exist)
        Base.metadata.create_all(bind=engine)
        
        logger.info("Course tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating course tables: {e}")
        return False

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        from app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            return True
            
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def main():
    """Main function to run the database initialization"""
    logger.info("Starting database initialization...")
    
    # Check database connection first
    if not check_database_connection():
        logger.error("Cannot connect to database. Exiting.")
        return False
    
    # Create course tables
    if not create_course_tables():
        logger.error("Failed to create course tables.")
        return False
    
    logger.info("Database initialization completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)