#!/usr/bin/env python3
"""
Initialize database with course tables
Creates the necessary tables for courses, lessons, and enrollments
"""

import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import Base, engine
from app.models.course import Course, Lesson, CourseEnrollment

def create_course_tables():
    """Create course-related tables in the database"""
    print("Creating course tables...")
    
    # Create all tables (this will only create tables that don't exist)
    Base.metadata.create_all(bind=engine)
    
    print("Course tables created successfully!")

if __name__ == "__main__":
    create_course_tables()